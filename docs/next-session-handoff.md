# OpenSpawn Handoff

Updated: 2026-03-18

## Current State

OpenSpawn is now a working macOS folder agent with a real drag-and-drop entrypoint and a much simpler product shape than the earlier recommendation-heavy prototype.

Working product loop:
- drag a folder onto `OpenSpawn.app`
- OpenSpawn creates or opens the folder agent
- the folder gets hidden `.agent/` state
- the folder gets a visible `OpenSpawn Agent.app`
- supported files are scanned and read locally
- if Claude is configured, the session opens with an AI-generated orientation
- on reopen, Claude reviews changes/history and gives a short update
- the user mostly just chats, instead of navigating lots of commands

## What Works

- main launcher: `OpenSpawn.app`
- shell fallback: `OpenSpawn.command`
- folder-local agent app: `OpenSpawn Agent.app`
- custom icon is now wired into both the main app and generated folder agent apps
- persistent `.agent/` state
- file reading for text, CSV/TSV, notebook, Excel, PDF
- grounded chat with Claude
- first-open startup prompt
- reopen startup prompt with change-aware context
- minimal command surface: `help`, `recommend ai`, `done`, `setup`, `quit`
- persistent `project.md`
- session capture via `done`

## What Changed Recently

- removed the heavy visible command surface and recommendation-plumbing feel
- startup now uses two separate prompts:
  - first open
  - reopen
- both prompts explicitly infer likely folder purpose and likely user intent
- startup suggestions are now framed as `What do you want me to do next?`
- `OpenSpawn Agent.command` stayed removed; folder-local reopen is via `OpenSpawn Agent.app`
- icon generation/copying was fixed for both app bundles
- public-facing README/release docs were rewritten for GitHub beta
- private docs like the PRD and `CLAUDE.md` are now excluded from the public repo surface

## Important Files

- Product plan: `OpenSpawn PRD v4.md` (private/local only)
- vNext roadmap: [openspawn-vnext-agentic-roadmap.md](/Users/petergratzke/projects/openspawn/prototype/docs/openspawn-vnext-agentic-roadmap.md)
- Stage 0 test plan: [test-plan-openspawn-stage0.md](/Users/petergratzke/projects/openspawn/prototype/docs/test-plan-openspawn-stage0.md)
- Backlog: [TODOS.md](/Users/petergratzke/projects/openspawn/prototype/TODOS.md)
- Public launch plan: [github-beta-launch-plan.md](/Users/petergratzke/projects/openspawn/prototype/docs/github-beta-launch-plan.md)
- Release checklist: [beta-release-checklist.md](/Users/petergratzke/projects/openspawn/prototype/docs/beta-release-checklist.md)

## Important Runtime Files

- CLI entrypoint and startup prompts: [cli.py](/Users/petergratzke/projects/openspawn/prototype/openspawn/cli.py)
- session orchestration: [session.py](/Users/petergratzke/projects/openspawn/prototype/openspawn/session.py)
- prompt context assembly: [context.py](/Users/petergratzke/projects/openspawn/prototype/openspawn/context.py)
- file scanning: [scanner.py](/Users/petergratzke/projects/openspawn/prototype/openspawn/scanner.py)
- extraction: [extractor.py](/Users/petergratzke/projects/openspawn/prototype/openspawn/extractor.py)
- AI client: [ai.py](/Users/petergratzke/projects/openspawn/prototype/openspawn/ai.py)
- folder launcher builder: [launcher.py](/Users/petergratzke/projects/openspawn/prototype/openspawn/launcher.py)
- main app builder: [app_bundle.py](/Users/petergratzke/projects/openspawn/prototype/openspawn/app_bundle.py)
- icon builder: [generate_spawn_icon.py](/Users/petergratzke/projects/openspawn/prototype/tools/generate_spawn_icon.py)

## Known Product Truths

- explicit invocation with a folder path is treated as user intent, so auto-create is okay there
- drag-and-drop onto `OpenSpawn.app` is treated as user intent, so auto-create is okay there
- the visible product is now mostly prompt-driven rather than command-driven
- the right hardcoding boundary is lifecycle triggers and trust rails, not lots of domain logic
- folder-local reopen is `OpenSpawn Agent.app`, not `.command`
- Claude setup is persisted inside OpenSpawn, not dependent on shell env vars

## Main Known Rough Edges

- Claude-backed startup and chat quality are better, but still need tuning
- some compare/summarize answers are still too sparse
- `recommend ai` still exists, but may end up redundant if startup prompting gets strong enough
- Claude latency/timeouts are still a meaningful beta risk
- packaging is still GitHub-first beta, not polished consumer distribution

## Best Next Task

Finish the GitHub beta push with a final product-feel pass.

Concrete next implementation/testing steps:
1. run the public beta flow end to end from the current repo state
2. confirm first-open and reopen responses feel good on real folders
3. confirm the main app and generated folder agent app both present with the correct icon
4. do a final public repo sanity check before push

## Good Test Folders

- [amazon](/Users/petergratzke/projects/openspawn/prototype/amazon)
- [amazon-2](/Users/petergratzke/projects/openspawn/prototype/amazon-2)

These are still good regression folders because they exercise:
- drag-and-drop app flow
- PDF extraction
- AI-generated startup orientation
- reopen/change-aware prompting
- Claude chat
