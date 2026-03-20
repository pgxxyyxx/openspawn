from __future__ import annotations

import re
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def render_for_terminal(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    in_code_block = False
    for line in lines:
        rendered, in_code_block = render_line(line, in_code_block)
        out.extend(rendered)
    return "\n".join(out).strip()


def render_line(line: str, in_code_block: bool = False) -> tuple[list[str], bool]:
    """Render a single markdown line to formatted terminal output.

    Returns (list of output lines, updated in_code_block state).
    """
    if line.startswith("```"):
        return [], not in_code_block
    if in_code_block:
        return ["  " + line], True
    if line.startswith("### "):
        return ["\n\033[1m" + line[4:] + "\033[0m"], False
    if line.startswith("## "):
        label = line[3:]
        return ["\n\033[1m" + label + "\033[0m", "-" * len(label)], False
    if line.startswith("# "):
        label = line[2:]
        return ["\n\033[1m" + label.upper() + "\033[0m", "=" * len(label)], False
    line = re.sub(r"\*\*(.+?)\*\*", r"\033[1m\1\033[0m", line)
    line = re.sub(r"\*(.+?)\*", r"\1", line)
    line = re.sub(r"`(.+?)`", r"\1", line)
    line = re.sub(r"^- ", "• ", line)
    return [line], False
