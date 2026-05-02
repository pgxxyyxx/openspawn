# OpenSpawn

OpenSpawn turns a macOS folder into a persistent local AI workspace.

Drag a folder onto `OpenSpawn.app`. OpenSpawn opens Pi in that folder, gives the
agent durable folder memory, and asks it to orient itself by reading the files
that matter. The first useful output is not a blank chat box; it is a grounded
folder briefing plus local memory files the agent can update over time.

---

## What You Get

**On first open** — OpenSpawn prepares a folder-local `.openspawn/` workspace,
adds Pi project instructions, and sends Pi a first-run prompt to inspect the
folder, update memory, and give a concise orientation.

**On reopen** — Pi reads the existing OpenSpawn memory first, checks what now
looks important, updates the wiki, and gives a re-entry note with concrete next
actions.

**In between** — use Pi normally. Ask it to draft, audit, summarize, compare,
edit, or create new artifacts. OpenSpawn instructs Pi to keep durable context in
plain markdown instead of leaving everything stranded in chat.

---

## Install

Requires macOS, Node.js/npm, and Pi.

```bash
npm install -g @mariozechner/pi-coding-agent
```

Then drag a folder onto the checked-in `OpenSpawn.app`.

On first use, if Pi is not logged in yet, OpenSpawn opens Pi with setup
instructions. Run:

```text
/login
```

Choose ChatGPT Plus/Pro (Codex) or an API-key provider. After login succeeds,
quit Pi and drag the folder onto `OpenSpawn.app` again.

---

## User Journey

1. Drag a folder onto `OpenSpawn.app`.
2. If needed, log in to Pi with `/login`.
3. OpenSpawn creates local folder memory under `.openspawn/`.
4. Pi inspects the folder and writes an initial project/wiki summary.
5. Continue working with Pi in the terminal.
6. Drag the same folder onto `OpenSpawn.app` later to pick up from memory.

---

## Folder Memory

OpenSpawn uses a Karpathy-style "LLM wiki" pattern: raw folder files remain the
source material, while the agent maintains a small local memory/wiki.

Typical generated files:

```text
.openspawn/
  project.md
  raw/README.md
  wiki/
    index.md
    log.md
    findings.md
    ...
.pi/
  APPEND_SYSTEM.md
```

`project.md` is durable project context. `wiki/index.md` is the table of
contents. `wiki/log.md` records session activity. Additional wiki pages are
created as useful.

OpenSpawn owns only the marked OpenSpawn block inside `.pi/APPEND_SYSTEM.md`,
so existing Pi project instructions are preserved.

---

## How It Works

- **Local-first state** — OpenSpawn writes plain files in the selected folder.
- **Pi-backed agent** — Pi handles tool use, file inspection, editing, and model
  provider access.
- **Minimal runtime** — the active launcher path is a small shell script plus
  the checked-in macOS app wrapper.
- **Transparent memory** — the agent's durable understanding is inspectable and
  editable as markdown.
- **Login preflight** — OpenSpawn does not consume the first-run prompt until Pi
  credentials exist.

---

## Developer Notes

The active app path is:

```text
OpenSpawn.app -> bin/openspawn-pi-launcher.sh -> pi
```

Useful commands:

```bash
# Launch a folder directly
bin/openspawn-pi-launcher.sh /path/to/folder

# Rebuild the app icon from the configured source PNG
uv run python tools/generate_spawn_icon.py

# Rebuild the checked-in OpenSpawn.app wrapper
uv run python -c "from pathlib import Path; from openspawn.app_bundle import build_main_app; build_main_app(Path('OpenSpawn.app'))"
```

The Python package under `openspawn/` still contains the earlier Claude-backed
prototype and the macOS app builder. The current spike keeps that code in place,
but the checked-in app now launches the Pi-backed shell path.

---

## Beta Caveats

- macOS only.
- Distributed through GitHub, not a signed/notarized installer.
- Pi must be installed separately with npm.
- Model/provider behavior is managed by Pi.
- `.openspawn/` and `.pi/` are local folder state and are intentionally ignored
  by this repo.
