from __future__ import annotations

import json
from dataclasses import asdict

from .types import AgentConfig, ArtifactRecord, FileChange, FileEntry, HistoryEntry, Memory, SessionNote


def build_system_prompt(
    config: AgentConfig,
    files: list[FileEntry],
    memory: Memory,
    changes: list[FileChange],
    history: list[HistoryEntry],
    session_notes: list[SessionNote],
    artifacts: list[ArtifactRecord],
    promoted_paths: set[str],
    skill_prompt: str | None = None,
    max_tokens: int = 120_000,
) -> tuple[str, dict]:
    """Build a system prompt with tiered file inclusion.

    Files are included at three levels:
      Level 0 — metadata: path, ext, size, read_status (all files)
      Level 1 — plus structured_summary if available (all readable files)
      Level 2 — plus content_text (only files in promoted_paths)

    Returns (prompt, stats) where stats has included_files and total_files.
    """
    sections = [
        f"You are OpenSpawn, a grounded folder agent for '{config.name}'.",
        "Never claim to have read a file unless its read_status confirms it.",
        "Cite file names. Include a 'Source basis:' line.",
        "If you only have metadata for a file, say so clearly.",
    ]

    # Budget the total prompt, not just files. Reserve half for files minimum.
    total_char_budget = max_tokens * 4
    state_sections: list[str] = []
    state_char_cap = total_char_budget // 2
    state_chars = 0

    def _add_state(label: str, payload: str) -> None:
        nonlocal state_chars
        candidate = f"\n{label}:\n{payload}"
        if state_chars + len(candidate) > state_char_cap:
            return
        state_sections.append(candidate)
        state_chars += len(candidate)

    if changes:
        _add_state("CHANGES", json.dumps([asdict(c) for c in changes]))
    if session_notes:
        _add_state("SESSION NOTES", json.dumps([asdict(n) for n in session_notes[-3:]]))
    if memory.facts:
        _add_state("MEMORY", json.dumps([f.text for f in memory.facts[-20:]]))
    if history:
        _add_state("HISTORY", json.dumps([asdict(h) for h in history[-10:]]))
    if artifacts:
        _add_state("ARTIFACTS", json.dumps([asdict(a) for a in artifacts[-10:]]))
    if skill_prompt:
        _add_state("SKILL INSTRUCTION", skill_prompt)

    sections.extend(state_sections)

    # File inclusion with tiered content — budget is whatever remains
    preamble_chars = sum(len(s) for s in sections)
    char_budget = max(0, total_char_budget - preamble_chars)
    file_entries: list[dict] = []
    chars_used = 0
    for entry in files:
        obj: dict = {
            "path": entry.path,
            "ext": entry.ext,
            "size": entry.size,
            "read_status": entry.read_status,
        }
        if entry.structured_summary:
            obj["structure"] = entry.structured_summary
        if entry.path in promoted_paths and entry.content_text:
            obj["content"] = entry.content_text
        serialized = json.dumps(obj)
        if chars_used + len(serialized) > char_budget:
            # Try without content
            obj.pop("content", None)
            serialized = json.dumps(obj)
            if chars_used + len(serialized) > char_budget:
                break
        file_entries.append(obj)
        chars_used += len(serialized)

    included = len(file_entries)
    sections.append(f"\nFILES ({included}/{len(files)}):\n{json.dumps(file_entries)}")

    prompt = "\n".join(sections)
    stats = {"included_files": included, "total_files": len(files)}
    return prompt, stats


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return max(1, len(text) // 4)
