from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import FileEntry


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    prompt: str
    tags: frozenset[str]


SKILLS: dict[str, Skill] = {s.name: s for s in [
    Skill(
        name="summarize",
        description="Summarize what matters most across the files in this folder",
        prompt=(
            "Summarize what matters most in this folder. "
            "Focus only on files you have actually read. "
            "Give a structured summary with the most important points from each significant file, "
            "then a brief overall synthesis. "
            "Be specific — name files and quote or paraphrase key content where useful. "
            "Do not pad with generic observations."
        ),
        tags=frozenset({"any", "docs", "pdf", "text"}),
    ),
    Skill(
        name="compare",
        description="Compare the key documents and highlight meaningful differences",
        prompt=(
            "Compare the main documents in this folder. "
            "Identify the most meaningful document pairs or groups to compare. "
            "For each comparison: what they share, how they differ, and what those differences mean. "
            "Be specific with file names and content — quote or paraphrase where useful. "
            "If there are more than three documents, focus on the most important pairs."
        ),
        tags=frozenset({"multiple", "pdf", "docs", "text"}),
    ),
    Skill(
        name="brief",
        description="Draft a short executive briefing memo from this folder",
        prompt=(
            "Draft a short executive briefing based on this folder. "
            "Audience: a decision-maker who has not read the files. "
            "Format: memo style. "
            "Include: what this work is about, key findings or current status, "
            "decisions needed or recommendations, and open questions. "
            "Base it only on what you have actually read. Aim for one page."
        ),
        tags=frozenset({"any", "pdf", "docs", "text"}),
    ),
    Skill(
        name="timeline",
        description="Extract a chronological timeline of events, decisions, or milestones",
        prompt=(
            "Extract a chronological timeline from this folder. "
            "List events, decisions, milestones, or dated references in order. "
            "Include the source file for each item. "
            "If dates are unclear, note approximate timeframes. "
            "Focus on substantive events, not document creation dates."
        ),
        tags=frozenset({"docs", "pdf", "planning", "text"}),
    ),
    Skill(
        name="decisions",
        description="List all decisions, action items, and open questions",
        prompt=(
            "List all decisions, action items, and open questions visible in this folder. "
            "Separate them into three groups: decisions already made, "
            "action items assigned or implied, and questions that remain unresolved. "
            "Cite the source file for each item. Be specific."
        ),
        tags=frozenset({"any", "docs", "pdf", "planning", "text"}),
    ),
    Skill(
        name="risks",
        description="Identify risks, gaps, and unresolved issues",
        prompt=(
            "Identify risks, gaps, and unresolved issues in this folder. "
            "Look for: claims without supporting evidence, plans without owners or timelines, "
            "open questions that seem important, and missing context that would change the picture. "
            "Be specific about what is missing and why it matters."
        ),
        tags=frozenset({"any", "docs", "pdf", "planning", "text"}),
    ),
    Skill(
        name="audit",
        description="Audit the data files for structure, quality, and gaps",
        prompt=(
            "Audit the data files in this folder. "
            "For each structured file: describe what it contains, its row and column structure, "
            "any obvious quality issues such as missing values or inconsistencies, "
            "and what it can and cannot support analytically. "
            "Be specific about file names and column names."
        ),
        tags=frozenset({"data", "csv", "xlsx"}),
    ),
    Skill(
        name="verify",
        description="Check whether narrative claims are supported by the data",
        prompt=(
            "Check whether the narrative claims in this folder are supported by the data. "
            "For each significant quantitative or factual claim in the documents: "
            "state the claim, identify whether the data files support it, and flag discrepancies. "
            "Be specific about which documents and data files you are comparing."
        ),
        tags=frozenset({"data", "csv", "xlsx", "mixed"}),
    ),
    Skill(
        name="metrics",
        description="Extract all key metrics and numbers across the files",
        prompt=(
            "Extract all key metrics and numbers from this folder. "
            "List them in a structured format: metric name, value, source file, and context. "
            "Group by theme if useful. "
            "Flag metrics that appear in multiple files with different values."
        ),
        tags=frozenset({"data", "csv", "xlsx", "pdf"}),
    ),
    Skill(
        name="status",
        description="Produce a current status summary of the work in this folder",
        prompt=(
            "Produce a current status summary of the work in this folder. "
            "Based on the files and session history: what has been completed, "
            "what is in progress, what is blocked or unclear, and what should happen next. "
            "Format as a brief status update suitable for a team check-in."
        ),
        tags=frozenset({"any", "planning", "docs"}),
    ),
    Skill(
        name="gaps",
        description="Identify what is missing, unresolved, or needs follow-up",
        prompt=(
            "Identify what is missing, unresolved, or needs follow-up in this folder. "
            "Consider: incomplete documents, unanswered questions from the session history, "
            "files referenced but not present, analysis mentioned but not shown, "
            "and decisions that have been deferred. Be specific."
        ),
        tags=frozenset({"any", "planning", "docs", "text"}),
    ),
    Skill(
        name="next-steps",
        description="List the clearest next actions based on current folder state",
        prompt=(
            "List the clearest next actions based on the current state of this folder. "
            "For each action: state what needs to happen, why it matters, "
            "and which file or finding it connects to. "
            "Focus on actions that could be taken now, not abstract recommendations."
        ),
        tags=frozenset({"any", "planning", "docs", "text"}),
    ),
    Skill(
        name="memo",
        description="Draft a decision memo based on this folder",
        prompt=(
            "Draft a decision memo based on this folder. "
            "Structure: Background (one paragraph), Key Findings (three to five bullets), "
            "Recommendation or Decision Needed (one paragraph), Open Questions (two to three bullets). "
            "Base it only on what you have actually read. Aim for one page."
        ),
        tags=frozenset({"any", "pdf", "docs", "text"}),
    ),
    Skill(
        name="bullets",
        description="Distill the key points into a tight bulleted list",
        prompt=(
            "Distill the key points from this folder into a tight bulleted list. "
            "Aim for eight to twelve bullets that capture the most important facts, findings, and open items. "
            "Each bullet should be specific enough to stand alone. "
            "Cite file names where useful."
        ),
        tags=frozenset({"any", "pdf", "docs", "text"}),
    ),
    Skill(
        name="qa",
        description="Generate likely stakeholder questions and answer them from the files",
        prompt=(
            "Generate the questions a stakeholder or reader would most likely ask about this folder's content. "
            "For each question: state the question clearly and give the best answer you can from what you have read. "
            "If you cannot answer from the available files, say so explicitly."
        ),
        tags=frozenset({"any", "pdf", "docs", "text"}),
    ),
    Skill(
        name="year-over-year",
        description="Compare equivalent documents across different years or periods",
        prompt=(
            "Compare the equivalent documents across different time periods in this folder. "
            "Identify document pairs or groups that cover the same topic in different years or periods. "
            "For each comparison: what changed, what stayed the same, and what the trend suggests. "
            "Be specific about document names and dates."
        ),
        tags=frozenset({"multiple", "pdf", "investor"}),
    ),
    Skill(
        name="narrative",
        description="Write a coherent prose narrative of what this folder is about",
        prompt=(
            "Write a coherent narrative summary of this folder. "
            "Tell the story of what this work is: what problem it addresses, "
            "what has been done, what the key findings are, and where things stand now. "
            "Write in clear prose, not bullets. Aim for three to four paragraphs."
        ),
        tags=frozenset({"any", "pdf", "docs", "text"}),
    ),
    Skill(
        name="stakeholder",
        description="Summarize from an external stakeholder's perspective",
        prompt=(
            "Summarize this folder from the perspective of an external stakeholder or reader "
            "who needs to quickly understand what is going on. "
            "What do they need to know? What would concern them? What would they want to ask about? "
            "Keep it concise and focused on what matters to someone outside the day-to-day work."
        ),
        tags=frozenset({"pdf", "docs", "investor", "text"}),
    ),
    Skill(
        name="code-review",
        description="Review the code in this folder for issues, patterns, and improvements",
        prompt=(
            "Review the code in this folder. "
            "For each significant file you have read: identify issues (bugs, security concerns, bad patterns), "
            "note what is done well, and suggest concrete improvements. "
            "Prioritize by impact — lead with the most important findings. "
            "Be specific: quote the relevant code, name the file and approximate location. "
            "Do not invent issues for files you have not read."
        ),
        tags=frozenset({"code", "py", "js", "ts", "text"}),
    ),
    Skill(
        name="coauthor",
        description="Improve, extend, or restructure a draft document in this folder",
        prompt=(
            "Act as a co-author on the draft documents in this folder. "
            "Identify the document that most looks like a work-in-progress. "
            "For that document: assess its current structure and argument, "
            "identify what is weak, incomplete, or unclear, "
            "and produce an improved version or a specific set of targeted edits. "
            "Preserve the author's voice and intent. "
            "If there are multiple drafts, state which one you are working on and why."
        ),
        tags=frozenset({"docs", "text", "any"}),
    ),
    Skill(
        name="debug",
        description="Help diagnose issues from error logs, stack traces, or failing code",
        prompt=(
            "Help diagnose the issues visible in this folder. "
            "Look for error logs, stack traces, test output, or failing code. "
            "For each issue: state what the error is, identify the likely root cause from the available context, "
            "and suggest a concrete fix or next debugging step. "
            "If you cannot determine the cause from what you have read, say what additional context would help."
        ),
        tags=frozenset({"code", "text", "py", "js", "ts"}),
    ),
    Skill(
        name="weekly-review",
        description="Synthesize the state of this folder as a periodic review",
        prompt=(
            "Produce a weekly review of this folder. "
            "Based on the files, session history, and any notes or docs present: "
            "what was accomplished since the last review, what is currently in progress, "
            "what is stuck or overdue, and what the priorities should be for the coming week. "
            "Keep it concrete and grounded in what you can actually see. "
            "Format as a brief review a team lead or project owner could act on."
        ),
        tags=frozenset({"any", "planning", "docs", "text"}),
    ),
]}

# Aliases so users don't need exact names
ALIASES: dict[str, str] = {
    "yoy": "year-over-year",
    "exec-brief": "brief",
    "exec brief": "brief",
    "action-items": "decisions",
    "action items": "decisions",
    "next steps": "next-steps",
}


def get_skill(name: str) -> Skill | None:
    key = name.strip().lower()
    key = ALIASES.get(key, key)
    return SKILLS.get(key)


def recommend_skills(files: list[FileEntry], n: int = 3) -> list[Skill]:
    ext_set = {entry.ext for entry in files}
    name_tokens: set[str] = set()
    for entry in files:
        name_tokens.update(entry.name.lower().replace("-", " ").replace("_", " ").split(".")[0].split())

    active: set[str] = {"any"}
    if ext_set & {".csv", ".tsv", ".xlsx", ".xls"}:
        active |= {"data", "csv", "xlsx"}
    if ".pdf" in ext_set:
        active.add("pdf")
    if ext_set & {".docx", ".md", ".txt"}:
        active.add("text")
    if ext_set & {".docx", ".md", ".txt", ".pdf"}:
        active.add("docs")
    if ext_set & {".py", ".js", ".ts", ".go", ".rs", ".java", ".cpp", ".c"}:
        active |= {"code", "py", "js", "ts"}
    if len(files) > 2:
        active.add("multiple")
    if name_tokens & {"proxy", "annual", "shareholder", "report", "10-k", "earnings", "filing"}:
        active.add("investor")
    if name_tokens & {"plan", "roadmap", "todo", "sprint", "milestone", "project", "tracker"}:
        active.add("planning")
    if active & {"data", "csv"} and active & {"docs", "pdf"}:
        active.add("mixed")

    scored = sorted(SKILLS.values(), key=lambda s: len(s.tags & active), reverse=True)
    return [s for s in scored if s.tags & active][:n]


def skills_context_block() -> str:
    lines = [
        "RESPONSE GUIDANCE — when asked to do any of the following, follow the corresponding approach exactly:",
    ]
    for skill in SKILLS.values():
        lines.append(f"- {skill.description}:\n  {skill.prompt}")
    lines.append(
        "Never refer to these as 'skills' or mention their internal names. "
        "Just do the work as described above when the user's request matches."
    )
    return "\n".join(lines)
