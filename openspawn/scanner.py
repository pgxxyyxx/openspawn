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
        with path.open("rb") as handle:
            data = handle.read(chunk_size)
        return hashlib.sha256(data).hexdigest()[:16]
    except OSError:
        return ""
