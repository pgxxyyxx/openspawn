## OpenSpawn

Persistent local AI agents for your folders on macOS.

OpenSpawn turns a folder into a persistent local AI workspace. It scans supported files, keeps local `.agent/` state, opens with an AI-generated orientation, and lets you keep working through a folder-local `OpenSpawn Agent.app`.

macOS-only GitHub beta.

## Current Status

Working now:

- main launcher: `OpenSpawn.app`
- shell fallback: `OpenSpawn.command`
- folder-local agent app: `OpenSpawn Agent.app`
- file reading and grounded chat
- local-first folder scan and session startup
- AI-generated folder orientation on first open and reopen
- session capture

For build and release context, see:

- [docs/next-session-handoff.md](docs/next-session-handoff.md)
- [TODOS.md](TODOS.md)
- [docs/github-beta-launch-plan.md](docs/github-beta-launch-plan.md)
- [docs/beta-release-checklist.md](docs/beta-release-checklist.md)

### Beta Install

Current public-beta plan: distribute through GitHub first, not DMG.

Recommended install path:

```bash
brew install uv
uv sync
uv run python -m openspawn --setup
open OpenSpawn.app
```

If the app launcher misbehaves, use:

```bash
uv run python -m openspawn /path/to/folder
```

If you do not use Homebrew, install `uv` first and then run `uv sync`.

If `OpenSpawn.app` is blocked or does not open cleanly, try:

1. `uv run python -m openspawn /path/to/folder`
2. `OpenSpawn.command`

If Claude-backed features fail:

- local startup and folder state should still remain usable
- some Claude-backed flows may time out while the beta is still being stabilized

### Run

```bash
uv run python -m openspawn --setup
uv run python -m openspawn --init --path /path/to/folder
uv run python -m openspawn --path /path/to/folder
uv run python -m openspawn /path/to/folder
```

Or double-click:

- `OpenSpawn.app` for the main Finder-style launcher
- `OpenSpawn.command` as the shell fallback
- `OpenSpawn Agent.app` inside a spawned folder

Drag-and-drop:

- drag a folder onto `OpenSpawn.app`
- or invoke `openspawn /path/to/folder`
- both are treated as explicit intent to create/open that folder's agent

### Claude Setup

Run `uv run python -m openspawn --setup` and paste your Anthropic API key once.

OpenSpawn will save it for future launcher runs.

### Beta Caveats

- macOS only
- currently aimed at early users comfortable downloading from GitHub
- local-first startup works without Claude
- Claude features send selected prompt/file excerpts to Anthropic
- some Claude-backed flows are still being stabilized
- this is a GitHub beta, not yet polished distribution

### Local State

OpenSpawn stores per-folder local state in a hidden `.agent/` directory inside the folder you open.

That state can include:

- file index and scan status
- extracted summaries / cached text
- project context
- session history and notes

### Feedback

For beta issues, open a GitHub bug report using the repo's beta bug template and include the exact error text when possible.

Useful commands once inside a folder session:

- ask a normal question
- `done` to save a session summary
- `quit` to save and exit

### Current Scope

- CLI-first folder agent
- main app-style home screen in development
- drag-and-drop app entrypoint in development
- persisted `.agent` state
- folder scanning and change detection
- supported file reading with normalized extraction results
- automatic AI-generated first-open and reopen orientation
- generated `.agent/project.md` context file
- session capture via `done`
- grounded chat with Claude when configured
- degraded local mode without AI

### Current Creation Rule

- `openspawn /path/to/folder` creates an agent if needed, because invoking OpenSpawn with a folder is treated as intent
- `--init` also creates an agent explicitly
- drag-and-drop uses the same intent rule
