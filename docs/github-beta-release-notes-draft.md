# OpenSpawn GitHub Beta Release Notes Draft

Updated: 2026-03-18

## OpenSpawn GitHub Beta

OpenSpawn gives a folder its own persistent local AI agent.

Drop a folder onto `OpenSpawn.app`, or run OpenSpawn from the CLI, and it will:

- scan supported files
- keep local `.agent/` state
- open with an AI-generated orientation
- support grounded chat about the folder
- create a folder-local `OpenSpawn Agent.app` for reopening later

## What Works In This Beta

- `OpenSpawn.app` main launcher
- `OpenSpawn.command` shell fallback
- folder-local `OpenSpawn Agent.app`
- local-first startup
- AI-generated first-open and reopen orientation
- grounded chat with Claude when configured
- persistent folder state in `.agent/`
- session capture

## Beta Caveats

- macOS only
- distributed through GitHub, not DMG
- not yet signed/notarized for broad consumer distribution
- some Claude-backed flows are still being stabilized
- some comparison-heavy chat responses are still too terse
- this is an early beta intended for feedback, not a polished final release

## Install

Recommended path:

```bash
brew install uv
uv sync
uv run python -m openspawn --setup
open OpenSpawn.app
```

Fallback:

```bash
uv run python -m openspawn /path/to/folder
```

## Trust Notes

- OpenSpawn stores local folder state in `.agent/`
- local startup works without Claude
- Claude features send selected prompt/file excerpts to Anthropic
- AI failures should fall back cleanly without breaking the session

## Feedback

Please file GitHub issues using the beta bug report template and include:

- exact error text
- whether Claude was enabled
- the command or flow you used
- what kind of folder you were testing

## Current Priority After Release

- stabilize Claude-backed flows under real latency
- improve chat quality for compare/summarize questions
- learn from real beta usage before broader packaging work
