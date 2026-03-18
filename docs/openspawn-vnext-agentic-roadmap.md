# OpenSpawn vNext — Folder Briefing, Recommendations, and Agentic Roadmap

## Why This Exists

OpenSpawn now has a working core loop:

- drag a folder onto the app
- create a persistent folder agent
- read supported files
- chat with grounded file context

That is necessary, but not sufficient.

The next product move is not "more chat."
It is:

- immediate value on first read
- recommendations based on what the agent actually read
- stronger persistent folder context
- a review loop that improves output quality over time

This document turns that into a build plan.

## Product Shift

OpenSpawn should evolve from:

- a folder-aware chat interface

into:

- a persistent folder intelligence system that briefs, recommends, reviews, and learns

The user should get value even before asking the first question.

## Core Principles

### 1. Brief first, chat second

After scanning and reading a folder, OpenSpawn should proactively produce a short briefing.

### 2. Recommendations must be grounded

Recommendations should be tied to:

- actual files read
- folder archetype
- explicit rationale

No generic "you could ask me anything" filler.

### 3. Persistent context should become first-class

Each folder should accumulate durable context:

- project purpose
- user preferences
- recurring goals
- accepted/rejected recommendations
- stable "how to help" instructions

### 4. Reviews should use fresh eyes

When OpenSpawn starts drafting plans, comparisons, or memos, critique should come from a separate review pass, not the same generation pass.

### 5. Learning should compound

User corrections and accepted patterns should improve future behavior in that folder.

## What To Build Next

## 1. Folder Briefing

Add a generated folder briefing after scan/spawn/open.

This should be saved to `.agent/briefing.json` and rendered in the CLI at the top of a new or refreshed session.

### Folder briefing should include

- `what_this_folder_is`
- `important_files`
- `what_changed`
- `what_looks_important`
- `recommended_next_steps`
- `source_basis`
- `confidence`

### Example

```text
Folder briefing

This folder appears to contain Amazon investor and governance documents from 2023-2025.

What looks important:
- Annual reports across two years
- Proxy statements across two years
- A shareholder letter

Recommended next steps:
1. Compare 2024 vs 2025 proxy changes
2. Summarize executive compensation and governance themes
3. Build a year-over-year narrative from annual reports and letters

Source basis:
- Amazon-2025-Proxy-Statement.pdf
- Amazon-com-Inc-2024-Proxy-Statement.pdf
- Amazon-2024-Annual-Report.pdf
- Amazon-com-Inc-2023-Annual-Report.pdf
```

### Why this matters

This is the first real "immediate value" layer.

The user should not need to figure out what to ask first.

## 2. Recommendation Engine

Add a recommendation engine that turns extracted content + folder archetype into useful, specific next actions.

### Recommendation object

Each recommendation should have:

- `title`
- `why_this_is_useful`
- `source_files`
- `confidence`
- `recommended_action`
- `category`

### Recommendation categories

- compare
- summarize
- audit
- verify
- brief
- extract timeline
- extract decisions
- identify risks

### Folder archetypes for v1 recommendations

Start with lightweight archetype detection:

- annual reports / proxy statements / investor materials
- research folder
- project planning folder
- data + narrative folder
- code / spec folder

### Example archetype-specific recommendations

#### Investor-relations folder

- compare annual reports year over year
- compare proxy statements year over year
- summarize executive compensation
- summarize governance changes
- extract shareholder proposals and outcomes

#### Planning folder

- summarize open decisions
- extract milestones and deadlines
- identify unresolved risks
- generate an exec-ready update memo

#### Data + narrative folder

- verify claims in prose against spreadsheets
- list metrics mentioned without numeric support
- summarize inconsistencies

## 3. Persistent Project Context

Add `.agent/project.md` as the canonical durable context file for a folder.

This is not the same as memory facts or README.

It should represent:

- what the folder is for
- how the user wants help
- what matters most
- what to prioritize
- what output style to use

### Suggested structure

```md
# Project Context

## Purpose
- What this folder is about

## User Preferences
- Preferred answer style
- What to emphasize
- What to avoid

## Recurring Goals
- Typical tasks for this folder

## Important Standing Facts
- Durable context that should persist across sessions

## Recommendation Preferences
- What kinds of suggestions are most useful
```

### How it gets updated

- initially generated from the first scan
- refined via `remember`
- later refined through explicit "update project context" suggestions

## 4. Session Capture

Add session handoff capture to `.agent/session-notes.json` or `.agent/done.md`.

At session end, OpenSpawn should be able to capture:

- key decisions
- new facts remembered
- open questions
- follow-up recommendations

This is a lightweight version of a `/done` workflow.

### New command

- `done`

### Output

```text
Session summary saved.

Decisions:
- ...

Open questions:
- ...

Suggested next steps:
- ...
```

## 5. Review Passes

Once the agent starts producing more substantial outputs, add a review pass.

This should not be built as a full orchestration system first.

Start simple:

- main pass produces briefing/recommendations/draft
- review pass critiques it for grounding and usefulness

### Review criteria

- is every claim grounded in files that were actually read?
- are recommendations specific and useful?
- are there obvious missed comparisons?
- is the output too generic?

## 6. Feedback Loop

Add lightweight learning from user behavior.

Track:

- which recommendations were accepted
- which were ignored
- which were explicitly rejected
- which answer styles the user prefers

Do not over-automate this initially.

Start with:

- `accept <recommendation>`
- `reject <recommendation>`
- later, use that to improve recommendation ranking

## New Files

Add these to `.agent/`:

- `briefing.json`
- `recommendations.json`
- `project.md`
- `done.md` or `session-notes.json`

## New Commands

Add these next:

- `brief`
- `recommend`
- `done`
- `project`
- `accept <n>`
- `reject <n>`

### Command roles

`brief`
- show the latest folder briefing

`recommend`
- show recommended next actions

`done`
- save session capture

`project`
- show current durable project context

`accept <n>` / `reject <n>`
- provide explicit feedback on recommendation usefulness

## Build Order

### Phase A

- folder briefing
- recommendations
- `brief` command
- `recommend` command

### Phase B

- `project.md`
- `project` command
- recommendation rationale and confidence

### Phase C

- session capture / `done`
- accepted/rejected recommendations
- improved recommendation ranking

### Phase D

- review pass for briefings/recommendations/drafts
- fresh-context critique agent

## What Not To Do Yet

- full multi-agent orchestration
- background daemons
- autonomous file edits
- recommendation spam on every small change
- complex workflow builder

## Success Criteria

The next version is successful if the user can say:

- "It told me what mattered before I asked."
- "Its recommendations were specific, not generic."
- "It learned what kind of help I want in this folder."
- "It keeps getting more useful over time."
