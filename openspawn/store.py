from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, fields, is_dataclass
from pathlib import Path
from typing import Any, TypeVar, get_args, get_origin, get_type_hints

from .types import AgentConfig, ArtifactRecord, FileIndex, GlobalConfig, HistoryEntry, Memory, SessionNote
from .utils import utc_now

T = TypeVar("T")

AGENT_DIRNAME = ".agent"


def ensure_global_dir() -> Path:
    path = global_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def global_dir() -> Path:
    override = os.environ.get("OPENSPAWN_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".openspawn"


def load_global_config() -> GlobalConfig:
    path = ensure_global_dir() / "config.json"
    if not path.exists():
        return GlobalConfig()
    return _load_json(path, GlobalConfig, default=GlobalConfig())


def save_global_config(config: GlobalConfig) -> None:
    path = ensure_global_dir() / "config.json"
    _atomic_write_json(path, config)


def load_saved_api_key() -> str | None:
    path = ensure_global_dir() / "credentials.json"
    if not path.exists():
        return None
    data = _load_json(path, dict[str, str], default={}) or {}
    key = data.get("anthropic_api_key", "").strip()
    return key or None


def save_api_key(api_key: str) -> None:
    path = ensure_global_dir() / "credentials.json"
    _atomic_write_json(path, {"anthropic_api_key": api_key.strip()})


def ensure_agent_dir(folder: Path) -> Path:
    path = folder / AGENT_DIRNAME
    path.mkdir(parents=True, exist_ok=True)
    return path


class AgentStore:
    def __init__(self, folder: Path):
        self.folder = folder
        self.agent_dir = ensure_agent_dir(folder)

    def load_config(self) -> AgentConfig | None:
        return self._load_optional("config.json", AgentConfig)

    def save_config(self, config: AgentConfig) -> None:
        self._save("config.json", config)

    def load_memory(self) -> Memory:
        return self._load_optional("memory.json", Memory, default=Memory()) or Memory()

    def save_memory(self, memory: Memory) -> None:
        self._save("memory.json", memory)

    def load_index(self) -> FileIndex:
        return self._load_optional("file-index.json", FileIndex, default=FileIndex()) or FileIndex()

    def save_index(self, index: FileIndex) -> None:
        self._save("file-index.json", index)

    def load_history(self) -> list[HistoryEntry]:
        return self._load_optional("history.json", list[HistoryEntry], default=[]) or []

    def save_history(self, history: list[HistoryEntry]) -> None:
        self._save("history.json", history[-1000:])

    def load_session_notes(self) -> list[SessionNote]:
        return self._load_optional("session-notes.json", list[SessionNote], default=[]) or []

    def save_session_notes(self, notes: list[SessionNote]) -> None:
        self._save("session-notes.json", notes[-100:])

    def load_artifacts(self) -> list[ArtifactRecord]:
        return self._load_optional("artifacts.json", list[ArtifactRecord], default=[]) or []

    def save_artifacts(self, artifacts: list[ArtifactRecord]) -> None:
        self._save("artifacts.json", artifacts[-200:])

    def write_project_context(self, content: str) -> None:
        path = self.agent_dir / "project.md"
        _atomic_write_text(path, content)

    def write_done_note(self, content: str) -> None:
        path = self.agent_dir / "done.md"
        _atomic_write_text(path, content)

    def write_readme(self, content: str) -> None:
        path = self.agent_dir / "README.md"
        _atomic_write_text(path, content)

    def backup_corrupt_file(self, filename: str) -> None:
        path = self.agent_dir / filename
        if not path.exists():
            return
        backup = self.agent_dir / f"{filename}.corrupt-{utc_now().replace(':', '-')}"
        path.replace(backup)

    def _load_optional(self, filename: str, cls: Any, default: Any | None = None) -> Any:
        path = self.agent_dir / filename
        if not path.exists():
            return default
        return _load_json(path, cls, default=default)

    def _save(self, filename: str, data: Any) -> None:
        _atomic_write_json(self.agent_dir / filename, data)


def _load_json(path: Path, cls: Any, default: Any | None = None) -> Any:
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError:
        return default
    except OSError:
        return default
    try:
        return _convert_value(raw, cls)
    except Exception:
        return default


def _convert_value(value: Any, annotation: Any) -> Any:
    origin = get_origin(annotation)
    if annotation is Any:
        return value
    if origin is list:
        inner = get_args(annotation)[0]
        return [_convert_value(item, inner) for item in value]
    if origin is dict:
        return value
    if is_dataclass(annotation):
        type_hints = get_type_hints(annotation)
        kwargs = {}
        for field_info in fields(annotation):
            if field_info.name in value:
                nested_annotation = type_hints.get(field_info.name, field_info.type)
                kwargs[field_info.name] = _convert_value(value[field_info.name], nested_annotation)
        return annotation(**kwargs)
    return value


def _atomic_write_json(path: Path, data: Any) -> None:
    serializable = _to_jsonable(data)
    _atomic_write_text(path, json.dumps(serializable, indent=2, sort_keys=True))


def _to_jsonable(data: Any) -> Any:
    if is_dataclass(data):
        return {key: _to_jsonable(value) for key, value in asdict(data).items()}
    if isinstance(data, list):
        return [_to_jsonable(item) for item in data]
    if isinstance(data, dict):
        return {key: _to_jsonable(value) for key, value in data.items()}
    return data


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
