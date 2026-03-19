from __future__ import annotations

from .skills import skills_context_block
from .types import AgentConfig, ArtifactRecord, FileChange, FileEntry, HistoryEntry, Memory, SessionNote


def build_system_prompt(
    config: AgentConfig,
    files: list[FileEntry],
    memory: Memory,
    changes: list[FileChange],
    history: list[HistoryEntry],
    session_notes: list[SessionNote],
    artifacts: list[ArtifactRecord],
    include_skills: bool = True,
) -> str:
    lines = [
        "You are OpenSpawn, a grounded folder agent.",
        "Never imply that you have read a file unless the file read status says you have.",
        "Be concise, direct, and cite file names explicitly.",
        f"Folder: {config.name}",
        "",
        "FILES:",
    ]
    for entry in files[:100]:
        source_basis = _basis_for_entry(entry)
        summary = f" - {entry.summary}" if entry.summary else ""
        warning = f" [{'; '.join(entry.warnings)}]" if entry.warnings else ""
        lines.append(f"- {entry.path} ({source_basis}){summary}{warning}")
    if changes:
        lines.extend(["", "CHANGES:"])
        for change in changes:
            lines.append(f"- {change.change_type}: {change.path}")
    if memory.facts:
        lines.extend(["", "MEMORY:"])
        for fact in memory.facts[-20:]:
            lines.append(f"- {fact.text}")
    if history:
        lines.extend(["", "RECENT HISTORY:"])
        for item in history[-10:]:
            lines.append(f"- {item.time} {item.entry_type}: {item.action}")
    if session_notes:
        lines.extend(["", "RECENT SESSION NOTES:"])
        for note in session_notes[-3:]:
            lines.append(f"- {note.created_at}")
            for thread in note.open_threads[:3]:
                lines.append(f"  open thread: {thread}")
            for decision in note.decisions[:3]:
                lines.append(f"  decision: {decision}")
    if artifacts:
        lines.extend(["", "RECENT ARTIFACTS:"])
        for artifact in artifacts[-10:]:
            lines.append(f"- {artifact.filename} ({artifact.artifact_type}, saved {artifact.created_at})")
    if include_skills:
        lines.extend(["", skills_context_block()])
    lines.extend(
        [
            "",
            "When answering, include a 'Source basis:' line.",
            "If you only have metadata for a file, say so clearly.",
        ]
    )
    return "\n".join(lines)


def build_user_message(question: str, files: list[FileEntry], specific_file: FileEntry | None = None) -> str:
    lines = [question]
    if specific_file:
        lines.extend(
            [
                "",
                f"Requested file: {specific_file.path}",
                f"Read status: {specific_file.read_status}",
                f"Content sample:\n{specific_file.content_text[:6000]}",
            ]
        )
    return "\n".join(lines)


def _basis_for_entry(entry: FileEntry) -> str:
    if entry.read_status in {"read_full", "read_partial"} and entry.content_text.strip():
        return entry.read_status
    return "metadata-only"
