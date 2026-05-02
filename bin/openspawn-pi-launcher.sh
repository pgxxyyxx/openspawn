#!/usr/bin/env bash
set -euo pipefail

target="${1:-}"

if [[ -z "$target" ]]; then
  cat <<'EOF'
OpenSpawn Pi spike

Drop a folder onto OpenSpawn.app, or run:

  bin/openspawn-pi-launcher.sh /path/to/folder

This launcher prepares a folder-local OpenSpawn memory scaffold and opens pi
inside that folder.
EOF
  exit 0
fi

if [[ "$target" == file://* ]]; then
  target="${target#file://}"
  target="$(printf '%b' "${target//%/\\x}")"
fi

if [[ ! -d "$target" ]]; then
  echo "Folder not found: $target"
  exit 1
fi

if ! command -v pi >/dev/null 2>&1; then
  cat <<'EOF'
pi is not installed yet.

Install it with:

  npm install -g @mariozechner/pi-coding-agent

Then run this launcher again. In pi, use /login to select ChatGPT Plus/Pro
(Codex) or an API-key provider.
EOF
  exit 1
fi

pi_agent_dir="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
pi_auth_file="$pi_agent_dir/auth.json"

has_pi_auth() {
  [[ -n "${ANTHROPIC_API_KEY:-}" ]] && return 0
  [[ -n "${OPENAI_API_KEY:-}" ]] && return 0
  [[ -n "${GEMINI_API_KEY:-}" ]] && return 0
  [[ -n "${MISTRAL_API_KEY:-}" ]] && return 0
  [[ -n "${OPENROUTER_API_KEY:-}" ]] && return 0
  [[ -n "${XAI_API_KEY:-}" ]] && return 0
  [[ -s "$pi_auth_file" ]] && return 0
  return 1
}

if ! has_pi_auth; then
  cd "$target"
  cat <<'EOF'
OpenSpawn needs Pi to be logged in before it can start this folder agent.

Pi is opening now. Run:

  /login

Choose ChatGPT Plus/Pro (Codex) or an API-key provider. After login succeeds,
quit Pi and drag this folder onto OpenSpawn.app again.

OpenSpawn has not created folder memory yet, so the next launch will still be a
true first run.

EOF
  exec pi
fi

cd "$target"

first_run=0
if [[ ! -d ".openspawn" ]]; then
  first_run=1
fi

mkdir -p .openspawn/wiki .openspawn/raw .openspawn/logs .pi

if [[ ! -f ".openspawn/project.md" ]]; then
  cat > .openspawn/project.md <<'EOF'
# OpenSpawn Project Context

## Purpose
- Unknown. The agent should infer this from the folder and update it.

## User Preferences
- Keep durable context in plain markdown files.
- Prefer grounded claims with source file paths.
- Ask before destructive edits or broad reorganizations.

## Recurring Goals
- Orient the user to what matters in this folder.
- Maintain a useful memory/wiki for future sessions.
- Turn useful answers back into durable project artifacts.

## Standing Facts
- This folder is managed by OpenSpawn through pi.
EOF
fi

if [[ ! -f ".openspawn/wiki/index.md" ]]; then
  cat > .openspawn/wiki/index.md <<'EOF'
# OpenSpawn Wiki Index

This index is maintained by the agent. It should list useful pages, source notes,
decisions, concepts, open questions, and generated artifacts.
EOF
fi

if [[ ! -f ".openspawn/wiki/log.md" ]]; then
  cat > .openspawn/wiki/log.md <<'EOF'
# OpenSpawn Log

Append session entries in reverse chronological order.
EOF
fi

if [[ ! -f ".openspawn/raw/README.md" ]]; then
  cat > .openspawn/raw/README.md <<'EOF'
# Raw Sources

Optional landing area for immutable source files or clipped notes that the agent
should read and integrate into the wiki.
EOF
fi

system_file=".pi/APPEND_SYSTEM.md"
system_tmp="$(mktemp "${TMPDIR:-/tmp}/openspawn-system.XXXXXX")"
if [[ -f "$system_file" ]]; then
  awk '
    /^<!-- BEGIN OPENSPAWN -->$/ { skip = 1; next }
    /^<!-- END OPENSPAWN -->$/ { skip = 0; next }
    !skip { print }
  ' "$system_file" > "$system_tmp"
else
  : > "$system_tmp"
fi

{
  cat "$system_tmp"
  if [[ -s "$system_tmp" ]]; then
    echo
  fi
  cat <<'EOF'
<!-- BEGIN OPENSPAWN -->
# OpenSpawn Folder Agent

You are running as OpenSpawn inside a user-selected folder. Your job is to turn
this folder into a persistent, useful workspace.

Use the Karpathy-style LLM wiki pattern:

- Treat the user's existing files as source material.
- Maintain `.openspawn/project.md` as durable project context.
- Maintain `.openspawn/wiki/index.md` as the navigational catalog.
- Maintain `.openspawn/wiki/log.md` as the chronological record of work.
- Create additional markdown pages under `.openspawn/wiki/` when they help the
  folder become more legible.
- Prefer source-grounded claims and cite local file paths.
- Update memory/wiki files as you learn; do not leave useful context stranded
  only in chat.

Operating rules:

- Inspect before acting.
- Do not modify, delete, move, or rename user source files unless the user asks.
- It is fine to create and update files under `.openspawn/` proactively.
- Ask before destructive actions, package installs, network access, or large
  broad edits.
- Keep user-facing responses concise and action-oriented.
<!-- END OPENSPAWN -->
EOF
} > "$system_file"
rm -f "$system_tmp"

timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
{
  echo
  if [[ "$first_run" == "1" ]]; then
    echo "## [$timestamp] open | first run"
  else
    echo "## [$timestamp] open | reopen"
  fi
  echo "- Launcher prepared OpenSpawn Pi memory scaffold."
} >> .openspawn/wiki/log.md

if [[ "$first_run" == "1" ]]; then
  prompt="$(cat <<'EOF'
This is the first OpenSpawn run for this folder.

Set yourself loose on the folder now:

1. Inspect the folder structure and the most important readable files.
2. Create or update `.openspawn/project.md`, `.openspawn/wiki/index.md`, and useful pages under `.openspawn/wiki/`.
3. Record what you did in `.openspawn/wiki/log.md`.
4. Give me a concise initial orientation grounded in the files you inspected.
5. End with 3-5 concrete next actions you can take in this folder.

Do not ask me what to do first unless you are blocked. Do not edit user source
files yet; use `.openspawn/` for generated memory and wiki artifacts.
EOF
)"
else
  prompt="$(cat <<'EOF'
This is a reopened OpenSpawn folder.

Pick up where the folder memory left off:

1. Read `.openspawn/project.md`, `.openspawn/wiki/index.md`, and recent entries in `.openspawn/wiki/log.md`.
2. Inspect what changed or what now looks important in the folder.
3. Update the `.openspawn/` memory/wiki files with any useful new context.
4. Give me a concise re-entry note: open threads, notable changes, and concrete next actions.

Do not ask what to do first unless you are blocked. Do not edit user source files
unless I ask.
EOF
)"
fi

exec pi "$prompt"
