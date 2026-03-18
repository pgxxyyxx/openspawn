from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from .ai import ClaudeClient, get_api_key
from .context import build_system_prompt, build_user_message
from .extractor import extract_file
from .launcher import ensure_folder_launcher
from .scanner import detect_changes, prioritize, scan_folder, should_read_file
from .store import AgentStore, load_global_config, save_global_config
from .types import AgentConfig, ExtractionResult, Fact, FileChange, FileEntry, FileIndex, HistoryEntry, Memory, SessionNote
from .utils import utc_now


class AgentSession:
    def __init__(self, folder: Path):
        self.folder = folder.resolve()
        self.store = AgentStore(self.folder)
        self.global_config = load_global_config()
        self.config = self.store.load_config()
        self.memory = self.store.load_memory()
        self.index = self.store.load_index()
        self.history = self.store.load_history()
        self.session_notes = self.store.load_session_notes()
        self.changes: list[FileChange] = []
        self.last_response = ""

    @classmethod
    def spawn(cls, folder: Path) -> "AgentSession":
        session = cls(folder)
        if session.config is None:
            session.config = AgentConfig(name=folder.name, root_path=str(folder.resolve()), created_at=utc_now())
        session.refresh(initial=True)
        ensure_folder_launcher(folder)
        session._save()
        session._update_global_agents()
        return session

    def open_existing(self) -> None:
        if self.config is None:
            raise FileNotFoundError("No OpenSpawn agent exists in this folder yet. Run with --init first.")
        ensure_folder_launcher(self.folder)
        self.refresh(initial=False)
        self._save()
        self._update_global_agents()

    def refresh(self, initial: bool) -> None:
        previous_index = self.index
        new_index = scan_folder(self.folder, self.global_config.limits)
        self.changes = detect_changes(previous_index, new_index)
        old_entries = {entry.path: entry for entry in previous_index.files}
        merged_entries: list[FileEntry] = []
        for entry in prioritize(new_index.files):
            prior = old_entries.get(entry.path)
            if prior and prior.hash == entry.hash and prior.mod_time == entry.mod_time and prior.size == entry.size and prior.read_status in {"read_full", "read_partial", "read_metadata_only"}:
                merged_entries.append(reuse_entry(entry, prior))
                continue
            if should_read_file(entry, self.global_config.limits, sum(1 for item in merged_entries if item.read_status in {"read_full", "read_partial"})):
                merged_entries.append(self._read_entry(entry))
            else:
                merged_entries.append(entry)
        self.index = FileIndex(files=sorted(merged_entries, key=lambda item: item.path), scanned_at=utc_now(), partial=new_index.partial)
        self._trim_cache()
        self._write_readme()
        self.add_history("Initial scan" if initial else "Refreshed folder", "scan")

    def read_file_now(self, query: str) -> FileEntry | None:
        entry = self.find_file(query)
        if entry is None or entry.is_dir:
            return None
        updated = self._read_entry(entry)
        self._replace_entry(updated)
        self._trim_cache()
        self._write_readme()
        self._save()
        return updated

    def find_file(self, query: str) -> FileEntry | None:
        lowered = query.lower().strip()
        for entry in self.index.files:
            if entry.path.lower() == lowered or entry.name.lower() == lowered:
                return entry
        for entry in self.index.files:
            if lowered in entry.path.lower():
                return entry
        return None

    def add_fact(self, text: str, source: str = "user") -> None:
        self.memory.facts.append(Fact(text=text, created_at=utc_now(), source=source))
        self.add_history(f"Remembered: {text}", "memory")
        self._write_readme()
        self.save()

    def chat(self, client: ClaudeClient, question: str) -> str:
        specific = None
        for entry in self.index.files:
            if entry.name.lower() in question.lower() or entry.path.lower() in question.lower():
                specific = entry
                if entry.read_status not in {"read_full", "read_partial"}:
                    specific = self.read_file_now(entry.path) or entry
                break
        system_prompt = build_system_prompt(self.config, self.index.files, self.memory, self.changes, self.history)
        user_message = build_user_message(question, self.index.files, specific)
        answer = client.chat(system_prompt, user_message)
        self.last_response = answer
        self.add_history(f"Asked: {question[:80]}", "chat")
        self.save()
        return answer

    def status_lines(self) -> list[str]:
        indexed = len(self.index.files)
        readable = sum(1 for entry in self.index.files if entry.read_status in {"read_full", "read_partial"})
        metadata_only = sum(1 for entry in self.index.files if entry.read_status == "read_metadata_only")
        errors = sum(1 for entry in self.index.files if entry.error)
        lines = [
            f"{self.config.name} — {indexed} files indexed",
            f"{readable} files read, {metadata_only} metadata-only, {errors} with errors",
        ]
        if self.index.partial:
            lines.append("Index is partial because folder limits were reached.")
        return lines

    def capture_session_note(self) -> SessionNote:
        note = SessionNote(
            created_at=utc_now(),
            remembered_facts=[fact.text for fact in self.memory.facts[-5:]],
        )
        self.session_notes.append(note)
        self.add_history("Captured session note", "session")
        self._write_done_note(note)
        self.save()
        return note

    def save_response(self, filename: str) -> Path:
        content = self.last_response
        if not content:
            raise ValueError("No response to save yet.")
        path = self.folder / filename
        if path.suffix == ".docx":
            _save_as_docx(content, path)
        else:
            path.write_text(content, encoding="utf-8")
        self.add_history(f"Saved response to {filename}", "save")
        self.save()
        return path

    def add_history(self, action: str, entry_type: str, details: str = "") -> None:
        self.history.append(HistoryEntry(time=utc_now(), action=action, entry_type=entry_type, details=details))

    def save(self) -> None:
        save_global_config(self.global_config)
        self._save()

    def close(self) -> None:
        self.add_history("Session closed", "system")
        self.save()

    def _read_entry(self, entry: FileEntry) -> FileEntry:
        result = extract_file(self.folder / entry.path, entry, self.global_config.limits)
        return replace(
            entry,
            read_status=result.status,
            parser=result.parser,
            bytes_read=result.bytes_read,
            content_text=result.content_text[: self.global_config.limits.max_text_bytes],
            structured_summary=result.structured_summary,
            warnings=result.warnings,
            error=result.error,
            summary=summarize_extraction(entry, result),
        )

    def _replace_entry(self, updated: FileEntry) -> None:
        self.index = replace(self.index, files=[updated if entry.path == updated.path else entry for entry in self.index.files])

    def _trim_cache(self) -> None:
        max_per_file = self.global_config.limits.max_text_bytes
        for entry in self.index.files:
            if len(entry.content_text.encode("utf-8")) > max_per_file:
                entry.content_text = trim_to_bytes(entry.content_text, max_per_file)
        total = sum(len(entry.content_text.encode("utf-8")) for entry in self.index.files)
        cap = self.global_config.limits.max_folder_cache_bytes
        if total <= cap:
            return
        for entry in sorted(self.index.files, key=lambda item: (item.priority, len(item.content_text))):
            if total <= cap:
                break
            if not entry.content_text:
                continue
            total -= len(entry.content_text.encode("utf-8"))
            entry.content_text = ""
            entry.read_status = "read_metadata_only"
            entry.warnings = list(entry.warnings) + ["Content trimmed for cache limits. Metadata only until re-read."]

    def _save(self) -> None:
        self.store.save_config(self.config)
        self.store.save_memory(self.memory)
        self.store.save_index(self.index)
        self.store.save_history(self.history)
        self.store.save_session_notes(self.session_notes)

    def _write_readme(self) -> None:
        lines = [f"# {self.config.name}", "", f"Last scan: {self.index.scanned_at}", "", "## Status"]
        lines.extend(f"- {line}" for line in self.status_lines())
        lines.extend(["", "## Files"])
        for entry in self.index.files[:100]:
            lines.append(f"- `{entry.path}` — {entry.read_status}{f' — {entry.summary}' if entry.summary else ''}")
        unreadable = [entry for entry in self.index.files if entry.error]
        if unreadable:
            lines.extend(["", "## Warnings"])
            for entry in unreadable[:20]:
                lines.append(f"- `{entry.path}` — {entry.error}")
        if self.memory.facts:
            lines.extend(["", "## Memory"])
            for fact in self.memory.facts[-20:]:
                lines.append(f"- {fact.text}")
        self.store.write_readme("\n".join(lines) + "\n")

    def _write_done_note(self, note: SessionNote) -> None:
        lines = ["# Session Note", "", f"Created: {note.created_at}", "", "## Remembered Facts"]
        lines.extend(f"- {item}" for item in (note.remembered_facts or ["None yet."]))
        self.store.write_done_note("\n".join(lines) + "\n")

    def _update_global_agents(self) -> None:
        agents = [agent for agent in self.global_config.agents if agent.get("path") != str(self.folder)]
        agents.append({"path": str(self.folder), "name": self.config.name, "last_opened": utc_now()})
        self.global_config.agents = agents[-100:]
        save_global_config(self.global_config)


def reuse_entry(current: FileEntry, previous: FileEntry) -> FileEntry:
    return replace(
        current,
        read_status=previous.read_status,
        bytes_read=previous.bytes_read,
        parser=previous.parser,
        summary=previous.summary,
        warnings=list(previous.warnings),
        error=previous.error,
        content_text=previous.content_text,
        structured_summary=dict(previous.structured_summary),
    )


def summarize_extraction(entry: FileEntry, result: ExtractionResult) -> str:
    if result.error:
        return result.error
    kind = result.structured_summary.get("kind")
    if kind == "table":
        return f"Structured table file with {len(result.structured_summary.get('columns', []))} columns."
    if kind == "workbook":
        return f"Workbook with {len(result.structured_summary.get('sheets', []))} sampled sheets."
    if kind == "pdf":
        return "PDF text extracted." if result.content_text else "PDF metadata only."
    if kind == "notebook":
        return f"Notebook with {result.structured_summary.get('cell_count', 0)} cells."
    if kind == "document":
        return f"Word document with {result.structured_summary.get('paragraph_count', 0)} paragraphs."
    if kind == "presentation":
        return f"Presentation with {result.structured_summary.get('slide_count', 0)} slides."
    return f"Read {entry.name}." if result.content_text else ""


def trim_to_bytes(text: str, max_bytes: int) -> str:
    return text.encode("utf-8")[:max_bytes].decode("utf-8", errors="ignore")


def _save_as_docx(content: str, path: Path) -> None:
    try:
        from docx import Document
        from docx.shared import Pt
    except ImportError:
        path.with_suffix(".md").write_text(content, encoding="utf-8")
        return
    doc = Document()
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("### "):
            doc.add_heading(stripped[4:], level=3)
        elif stripped.startswith("## "):
            doc.add_heading(stripped[3:], level=2)
        elif stripped.startswith("# "):
            doc.add_heading(stripped[2:], level=1)
        elif stripped.startswith("- ") or stripped.startswith("* "):
            doc.add_paragraph(stripped[2:], style="List Bullet")
        elif stripped:
            doc.add_paragraph(stripped)
    doc.save(str(path))
