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
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            out.append("  " + line)
            continue
        if line.startswith("### "):
            out.append("\n\033[1m" + line[4:] + "\033[0m")
        elif line.startswith("## "):
            label = line[3:]
            out.append("\n\033[1m" + label + "\033[0m")
            out.append("-" * len(label))
        elif line.startswith("# "):
            label = line[2:]
            out.append("\n\033[1m" + label.upper() + "\033[0m")
            out.append("=" * len(label))
        else:
            line = re.sub(r"\*\*(.+?)\*\*", r"\033[1m\1\033[0m", line)
            line = re.sub(r"\*(.+?)\*", r"\1", line)
            line = re.sub(r"`(.+?)`", r"\1", line)
            line = re.sub(r"^- ", "• ", line)
            out.append(line)
    return "\n".join(out).strip()
