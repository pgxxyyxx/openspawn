# OpenSpawn

A persistent local AI agent for your folders on macOS.

You drop a folder in. OpenSpawn reads supported files inside, orients you to what matters, and lets you ask grounded questions from your actual files. When you come back, it picks up where you left off.

---

## What You Get

**On first open** — an immediate AI-generated orientation. What's in this folder, what looks important, what you might want to do next. Grounded in files it actually read.

**On reopen** — continuity, not a blank slate. Claude leads with your open threads from last session, then what changed, then suggested next actions.

**In between** — chat with Claude grounded in your files. Chat responses cite the specific files they came from. If you ask about a specific file it hasn't read yet, OpenSpawn can read it first.

**When you're done** — type `done`. OpenSpawn saves a session summary: what was worked on, what's unfinished, any decisions made. That feeds the next reopen.

---

## User Journey

**First time with a folder:**

1. Drag the folder onto `OpenSpawn.app`
2. OpenSpawn scans and reads your files locally
3. Claude orients you — what's here, what looks important, what to do next
4. Ask questions, get answers grounded in your actual files
5. Type `done` before you leave — saves open threads and decisions for next time

**Every time after:**

1. Open `OpenSpawn Agent.app` inside the folder, or drag the folder onto `OpenSpawn.app` again
2. Claude leads with what was left unfinished, then what changed
3. Pick up where you left off

---

## Install

Requires macOS and Python 3.12+. Uses `uv` for dependency management.

```bash
brew install uv
uv sync
uv run python -m openspawn --setup
```

Then double-click `OpenSpawn.app` to launch, or drag a folder onto it.

**Claude setup:** Run `--setup` once and paste your [Anthropic API key](https://console.anthropic.com/). OpenSpawn saves it for future runs.

---

## Commands

Inside a folder session:

| Command | What it does |
|---|---|
| *(any question)* | Chat with Claude, grounded in your files |
| `help` | Show available commands |
| `done` | Save a session summary — open threads, decisions |
| `save [filename]` | Save last response to a `.md` or `.docx` file |
| `setup` | Add or replace your Claude API key |
| `quit` | Save state and exit |

---

## How It Works

- **Local-first** — files are scanned and indexed on your machine. No cloud sync.
- **Grounded answers** — Claude only claims to know what it has actually read. Chat responses include a source basis.
- **Persistent state** — each folder gets a hidden `.agent/` directory with its file index, session history, memory, and session notes.
- **Session continuity** — `done` captures open threads and decisions. Reopen surfaces them before anything else.

Supported file types: text, Markdown, PDF, CSV/TSV, Excel, Word, Jupyter notebooks.

---

## Beta Caveats

- macOS only
- GitHub beta — not yet polished distribution
- Claude features send selected prompt and file excerpts to Anthropic
- Local scanning and state work without Claude; chat features require an API key
- Some Claude-backed flows are still being stabilized (latency, timeouts)

For issues, open a GitHub bug report and include the exact error text.
