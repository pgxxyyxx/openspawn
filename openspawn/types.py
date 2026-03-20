from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Limits:
    max_index_files: int = 500
    max_initial_read_files: int = 100
    max_text_bytes: int = 262_144
    max_pdf_pages: int = 20
    max_folder_cache_bytes: int = 25 * 1024 * 1024
    prompt_budget: int = 120_000


@dataclass
class GlobalConfig:
    provider: str = "claude"
    model: str = "claude-sonnet-4-5"
    setup_complete: bool = False
    limits: Limits = field(default_factory=Limits)
    agents: list[dict[str, str]] = field(default_factory=list)


@dataclass
class AgentConfig:
    name: str
    root_path: str
    created_at: str
    provider: str = "claude"
    model: str = "claude-sonnet-4-5"


@dataclass
class Fact:
    text: str
    created_at: str
    source: str = "user"


@dataclass
class Memory:
    facts: list[Fact] = field(default_factory=list)


@dataclass
class FileEntry:
    path: str
    name: str
    ext: str
    size: int
    mod_time: str
    hash: str
    scan_status: str = "indexed"
    read_status: str = "read_metadata_only"
    bytes_read: int = 0
    parser: str = ""
    summary: str = ""
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
    is_dir: bool = False
    priority: int = 0
    content_text: str = ""
    structured_summary: dict[str, object] = field(default_factory=dict)


@dataclass
class FileIndex:
    files: list[FileEntry] = field(default_factory=list)
    scanned_at: str = ""
    partial: bool = False


@dataclass
class FileChange:
    path: str
    change_type: str
    details: str = ""


@dataclass
class HistoryEntry:
    time: str
    action: str
    entry_type: str
    details: str = ""


@dataclass
class SessionNote:
    created_at: str
    remembered_facts: list[str] = field(default_factory=list)
    open_threads: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)


@dataclass
class ArtifactRecord:
    filename: str
    artifact_type: str
    created_at: str


@dataclass
class ExtractionResult:
    status: str
    parser: str
    bytes_read: int
    content_text: str
    structured_summary: dict[str, object]
    warnings: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class PromptBuildResult:
    prompt: str
    included_file_count: int
    total_file_count: int
    estimated_tokens: int
