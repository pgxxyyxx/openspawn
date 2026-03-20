from __future__ import annotations

from .skills import skills_context_block
from .types import AgentConfig, ArtifactRecord, FileChange, FileEntry, HistoryEntry, Memory, PromptBuildResult, SessionNote


def build_system_prompt(
    config: AgentConfig,
    prompt_budget: int,
    files: list[FileEntry],
    memory: Memory,
    changes: list[FileChange],
    history: list[HistoryEntry],
    session_notes: list[SessionNote],
    artifacts: list[ArtifactRecord],
    include_skills: bool = True,
) -> PromptBuildResult:
    lines = [
        "You are OpenSpawn, a grounded folder agent.",
        "Never imply that you have read a file unless the file read status says you have.",
        "Be concise, direct, and cite file names explicitly.",
        f"Folder: {config.name}",
    ]
    token_count = estimate_tokens("\n".join(lines))
    if changes:
        token_count = _extend_lines(lines, token_count, ["", "CHANGES:"])
        for change in changes:
            detail = f" ({change.details})" if change.details else ""
            token_count = _extend_lines(lines, token_count, [f"- {change.change_type}: {change.path}{detail}"])
    if session_notes:
        token_count = _extend_lines(lines, token_count, ["", "RECENT SESSION NOTES:"])
        for note in session_notes[-3:]:
            token_count = _extend_lines(lines, token_count, [f"- {note.created_at}"])
            for thread in note.open_threads[:3]:
                token_count = _extend_lines(lines, token_count, [f"  open thread: {thread}"])
            for decision in note.decisions[:3]:
                token_count = _extend_lines(lines, token_count, [f"  decision: {decision}"])
    if memory.facts:
        token_count = _extend_lines(lines, token_count, ["", "MEMORY:"])
        for fact in memory.facts[-20:]:
            token_count = _extend_lines(lines, token_count, [f"- {fact.text}"])
    if history:
        token_count = _extend_lines(lines, token_count, ["", "RECENT HISTORY:"])
        for item in history[-10:]:
            token_count = _extend_lines(lines, token_count, [f"- {item.time} {item.entry_type}: {item.action}"])
    if artifacts:
        token_count = _extend_lines(lines, token_count, ["", "RECENT ARTIFACTS:"])
        for artifact in artifacts[-10:]:
            token_count = _extend_lines(
                lines,
                token_count,
                [f"- {artifact.filename} ({artifact.artifact_type}, saved {artifact.created_at})"],
            )

    token_count = _extend_lines(lines, token_count, ["", "FILES:"])
    total_file_count = len(files)
    included_file_count = 0
    file_summary_index = len(lines)
    token_count = _extend_lines(lines, token_count, [""])
    for entry in files[:100]:
        candidate = _file_line(entry)
        candidate_tokens = estimate_tokens(candidate)
        if token_count + candidate_tokens > prompt_budget:
            break
        lines.append(candidate)
        token_count += candidate_tokens
        included_file_count += 1
    omitted_file_count = max(total_file_count - included_file_count, 0)
    summary_line = f"Context includes {included_file_count} of {total_file_count} files. {omitted_file_count} files omitted."
    token_count += estimate_tokens(summary_line)
    lines[file_summary_index] = summary_line
    if omitted_file_count:
        omitted_names = [entry.path for entry in files[included_file_count:included_file_count + 10]]
        token_count = _extend_lines(lines, token_count, ["", "OMITTED FILES:"])
        for path in omitted_names:
            token_count = _extend_lines(lines, token_count, [f"- {path}"])
        if omitted_file_count > len(omitted_names):
            token_count = _extend_lines(lines, token_count, [f"- ... and {omitted_file_count - len(omitted_names)} more"])

    if include_skills:
        skill_block = skills_context_block()
        skill_tokens = estimate_tokens(skill_block)
        if token_count + skill_tokens <= prompt_budget:
            token_count = _extend_lines(lines, token_count, ["", skill_block])

    token_count = _extend_lines(
        lines,
        token_count,
        [
            "",
            "When answering, include a 'Source basis:' line.",
            "If you only have metadata for a file, say so clearly.",
        ],
    )
    prompt = "\n".join(lines)
    return PromptBuildResult(
        prompt=prompt,
        included_file_count=included_file_count,
        total_file_count=total_file_count,
        estimated_tokens=token_count,
    )


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


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _file_line(entry: FileEntry) -> str:
    source_basis = _basis_for_entry(entry)
    summary = f" - {entry.summary}" if entry.summary else ""
    warning = f" [{'; '.join(entry.warnings)}]" if entry.warnings else ""
    return f"- {entry.path} ({source_basis}){summary}{warning}"


def _basis_for_entry(entry: FileEntry) -> str:
    if entry.read_status in {"read_full", "read_partial"} and entry.content_text.strip():
        return entry.read_status
    return "metadata-only"


def _extend_lines(lines: list[str], token_count: int, new_lines: list[str]) -> int:
    lines.extend(new_lines)
    for line in new_lines:
        token_count += estimate_tokens(line)
    return token_count
