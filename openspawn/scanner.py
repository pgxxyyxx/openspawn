from __future__ import annotations

import hashlib
import os
from pathlib import Path

from .types import FileChange, FileEntry, FileIndex, Limits
from .utils import utc_now

SKIP_NAMES = {".agent", ".git", ".DS_Store", "__pycache__", "OpenSpawn Agent.app", "OpenSpawn Agent.command"}
TEXT_PRIORITY = {".md": 90, ".txt": 80, ".csv": 75, ".tsv": 75, ".xlsx": 70, ".xls": 70, ".pdf": 70}
SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".py",
    ".js",
    ".ts",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".csv",
    ".tsv",
    ".ipynb",
    ".xlsx",
    ".xls",
    ".pdf",
    ".docx",
    ".pptx",
}


def scan_folder(folder: Path, limits: Limits) -> FileIndex:
    files: list[FileEntry] = []
    partial = False
    for current_root, dirnames, filenames in os.walk(folder):
        rel_root = Path(current_root).relative_to(folder)
        dirnames[:] = [d for d in dirnames if d not in SKIP_NAMES and not d.startswith(".")]
        for name in sorted(filenames):
            if name in SKIP_NAMES or name.startswith("."):
                continue
            rel_path = (rel_root / name) if rel_root != Path(".") else Path(name)
            full_path = folder / rel_path
            if len(files) >= limits.max_index_files:
                partial = True
                break
            files.append(_build_entry(full_path, rel_path))
        if partial:
            break
    return FileIndex(files=sorted(files, key=lambda item: item.path), scanned_at=utc_now(), partial=partial)


def detect_changes(old_index: FileIndex, new_index: FileIndex) -> list[FileChange]:
    old_by_path = {entry.path: entry for entry in old_index.files}
    new_by_path = {entry.path: entry for entry in new_index.files}
    changes: list[FileChange] = []
    for path, new_entry in new_by_path.items():
        old_entry = old_by_path.get(path)
        if old_entry is None:
            changes.append(FileChange(path=path, change_type="new"))
            continue
        if old_entry.hash != new_entry.hash or old_entry.mod_time != new_entry.mod_time or old_entry.size != new_entry.size:
            changes.append(FileChange(path=path, change_type="modified"))
    for path in old_by_path:
        if path not in new_by_path:
            changes.append(FileChange(path=path, change_type="deleted"))
    return changes


def describe_changes(changes: list[FileChange], old_entries: dict[str, FileEntry], new_entries: dict[str, FileEntry]) -> list[FileChange]:
    described: list[FileChange] = []
    for change in changes:
        details = change.details
        if change.change_type == "modified":
            old_entry = old_entries.get(change.path)
            new_entry = new_entries.get(change.path)
            if old_entry is not None and new_entry is not None:
                details = compute_change_details(old_entry, new_entry)
        described.append(FileChange(path=change.path, change_type=change.change_type, details=details))
    return described


def compute_change_details(old_entry: FileEntry, new_entry: FileEntry) -> str:
    if new_entry.ext in {".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".ini"}:
        detail = _describe_text_change(old_entry.content_text, new_entry.content_text)
        if detail:
            return detail
    if new_entry.ext in {".csv", ".tsv"}:
        detail = _describe_table_change(old_entry, new_entry)
        if detail:
            return detail
    if new_entry.ext in {".xlsx", ".xls"}:
        detail = _describe_workbook_change(old_entry, new_entry)
        if detail:
            return detail
    if new_entry.ext == ".pdf":
        detail = _describe_count_change("page", old_entry.structured_summary.get("page_count"), new_entry.structured_summary.get("page_count"))
        if detail:
            return detail
    if new_entry.ext == ".docx":
        detail = _describe_count_change("paragraph", old_entry.structured_summary.get("paragraph_count"), new_entry.structured_summary.get("paragraph_count"))
        if detail:
            return detail
    if new_entry.ext == ".pptx":
        detail = _describe_count_change("slide", old_entry.structured_summary.get("slide_count"), new_entry.structured_summary.get("slide_count"))
        if detail:
            return detail
    return _describe_size_delta(old_entry.size, new_entry.size)


def should_read_file(entry: FileEntry, limits: Limits, read_count: int) -> bool:
    if read_count >= limits.max_initial_read_files:
        return False
    if entry.is_dir:
        return False
    if entry.ext not in SUPPORTED_EXTENSIONS:
        return False
    return True


def prioritize(entries: list[FileEntry]) -> list[FileEntry]:
    return sorted(entries, key=lambda item: (-item.priority, item.path))


def _build_entry(full_path: Path, rel_path: Path) -> FileEntry:
    try:
        stat = full_path.stat()
        is_dir = full_path.is_dir()
    except OSError as exc:
        return FileEntry(
            path=str(rel_path),
            name=rel_path.name,
            ext=rel_path.suffix.lower(),
            size=0,
            mod_time=utc_now(),
            hash="",
            scan_status="error_stat",
            error=str(exc),
        )
    ext = rel_path.suffix.lower()
    priority = TEXT_PRIORITY.get(ext, 10)
    if len(rel_path.parts) == 1:
        priority += 20
    return FileEntry(
        path=str(rel_path),
        name=rel_path.name,
        ext=ext,
        size=stat.st_size,
        mod_time=utc_now() if is_dir else utc_now_from_epoch(stat.st_mtime),
        hash="" if is_dir else hash_file(full_path),
        scan_status="indexed",
        is_dir=is_dir,
        priority=priority,
    )


def utc_now_from_epoch(epoch: float) -> str:
    from datetime import datetime, timezone

    return datetime.fromtimestamp(epoch, tz=timezone.utc).replace(microsecond=0).isoformat()


def hash_file(path: Path, chunk_size: int = 8192) -> str:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(chunk_size)
                if not chunk:
                    break
                digest.update(chunk)
        return digest.hexdigest()[:16]
    except OSError:
        return ""


def _describe_text_change(old_text: str, new_text: str) -> str:
    if not old_text or not new_text:
        return ""
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    delta = len(new_lines) - len(old_lines)
    parts: list[str] = []
    if delta > 0:
        parts.append(f"grew by {delta} lines")
    elif delta < 0:
        parts.append(f"shortened by {abs(delta)} lines")
    for index, (old_line, new_line) in enumerate(zip(old_lines, new_lines), start=1):
        if old_line != new_line:
            parts.append(f"first difference near line {index}")
            break
    else:
        if len(old_lines) != len(new_lines):
            parts.append(f"first difference near line {min(len(old_lines), len(new_lines)) + 1}")
    return ", ".join(parts)


def _describe_table_change(old_entry: FileEntry, new_entry: FileEntry) -> str:
    old_columns = list(old_entry.structured_summary.get("columns", []))
    new_columns = list(new_entry.structured_summary.get("columns", []))
    old_rows = _safe_int(old_entry.structured_summary.get("row_count"))
    new_rows = _safe_int(new_entry.structured_summary.get("row_count"))
    parts: list[str] = []
    new_only = [column for column in new_columns if column and column not in old_columns]
    removed = [column for column in old_columns if column and column not in new_columns]
    if new_rows is not None and old_rows is not None and new_rows != old_rows:
        row_delta = new_rows - old_rows
        if row_delta > 0:
            parts.append(f"{row_delta} new rows")
        else:
            parts.append(f"{abs(row_delta)} fewer rows")
    if new_only:
        parts.append(f"new column: {new_only[0]}")
    if removed:
        parts.append(f"removed column: {removed[0]}")
    return ", ".join(parts)


def _describe_workbook_change(old_entry: FileEntry, new_entry: FileEntry) -> str:
    old_sheets = {sheet.get("name", ""): sheet for sheet in old_entry.structured_summary.get("sheets", []) if isinstance(sheet, dict)}
    new_sheets = {sheet.get("name", ""): sheet for sheet in new_entry.structured_summary.get("sheets", []) if isinstance(sheet, dict)}
    parts: list[str] = []
    added = [name for name in new_sheets if name and name not in old_sheets]
    removed = [name for name in old_sheets if name and name not in new_sheets]
    if added:
        parts.append(f"new sheet: {added[0]}")
    if removed:
        parts.append(f"removed sheet: {removed[0]}")
    for name in new_sheets:
        if name not in old_sheets:
            continue
        old_rows = _safe_int(old_sheets[name].get("rows"))
        new_rows = _safe_int(new_sheets[name].get("rows"))
        if old_rows is not None and new_rows is not None and old_rows != new_rows:
            delta = new_rows - old_rows
            if delta > 0:
                parts.append(f"sheet {name} grew by {delta} rows")
            else:
                parts.append(f"sheet {name} shrank by {abs(delta)} rows")
            break
    return ", ".join(parts)


def _describe_count_change(label: str, old_value: object, new_value: object) -> str:
    old_count = _safe_int(old_value)
    new_count = _safe_int(new_value)
    if old_count is None or new_count is None or old_count == new_count:
        return ""
    delta = new_count - old_count
    noun = label if abs(delta) == 1 else f"{label}s"
    if delta > 0:
        return f"{delta} new {noun}"
    return f"{abs(delta)} fewer {noun}"


def _describe_size_delta(old_size: int, new_size: int) -> str:
    delta = new_size - old_size
    if delta == 0:
        return ""
    direction = "grew" if delta > 0 else "shrunk"
    return f"{direction} by {abs(delta):,} bytes"


def _safe_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
