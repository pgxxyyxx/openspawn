from __future__ import annotations

import argparse
import getpass
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import unquote, urlparse

from .ai import ClaudeClient, ClaudeError, get_api_key
from .session import AgentSession
from .store import AGENT_DIRNAME, ensure_global_dir, load_global_config, save_api_key, save_global_config
from .utils import render_line

FIRST_OPEN_PROMPT = (
    "Orient me to this folder for the first time. "
    "Use the available file context and any readable content you have. "
    "Your job is to give the best first response for opening this folder now. "
    "Start by saying this is the initial overview of the folder. "
    "Explain what this folder appears to be in 2-4 grounded sentences. "
    "Infer the most likely purpose of this folder and what the user probably wants to do with it. "
    "Assume the user is likely a knowledge worker such as an analyst, program manager, project manager, consultant, operator, or researcher. "
    "State that likely purpose briefly and use it to shape your recommendations. "
    "List 2-4 concrete things that stand out from the files you actually have context for, mentioning file names when useful. "
    "Then end with a section titled exactly: What do you want me to do next? "
    "Under that heading, give 3-5 concrete suggestions for what I can do next. "
    "Make those suggestions specific to this folder and to the likely user goal you inferred. "
    "Prefer useful actions such as summarizing important materials, comparing key documents, identifying gaps or missing context, "
    "suggesting cleanup or organization improvements, or drafting a useful output artifact such as a brief, memo, timeline, or comparison. "
    "Keep the whole response concise, grounded, and action-oriented. "
    "Do not mention capabilities you cannot support from the current folder context. "
    "Do not say vague things like 'I can help with anything.'"
)
REOPEN_PROMPT = (
    "This is a reopen of a folder the user has worked in before. "
    "Do not re-explain the folder from scratch. "
    "Use recent session notes first, then recent history and detected changes, to pick up where the user left off. "
    "If there are open threads from the last session note, lead with the heading 'Open threads from last session:' "
    "and list the most important unfinished items before discussing file changes. "
    "If there are no open threads but files changed, start with: 'Changes since last session:' followed by a brief list. "
    "If there are no open threads and no meaningful changes, start with a single sentence acknowledging that and referencing what the user was last working on. "
    "Then give 3-4 concrete suggestions for what to do next. "
    "Base suggestions on the open threads, recent history, and detected changes. "
    "Mention specific file names when useful. "
    "End with the heading: What do you want me to do next? "
    "Keep the whole response short. Do not re-summarize the folder. Do not repeat what you said on first open."
)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OpenSpawn")
    parser.add_argument("--init", action="store_true", help="Create an agent in a folder")
    parser.add_argument("--path", type=str, help="Folder path")
    parser.add_argument("folders", nargs="*", help="Optional folder path(s)")
    parser.add_argument("--setup", action="store_true", help="Run setup")
    args = parser.parse_args(argv)

    if args.setup:
        run_setup()
        return 0

    target = args.path or (args.folders[0] if args.folders else None)
    if not target:
        return run_home()

    if len(args.folders) > 1:
        print("OpenSpawn currently handles one folder at a time. Using the first dropped folder.")

    folder = normalize_folder_target(target)
    if not folder.exists() or not folder.is_dir():
        print(f"Folder not found: {folder}")
        return 1

    created_new = False
    if args.init or not (folder / AGENT_DIRNAME).exists():
        session = AgentSession.spawn(folder)
        created_new = True
    else:
        session = AgentSession(folder)
        session.open_existing()

    run_cli(session, created_new=created_new)
    return 0


def run_setup() -> None:
    ensure_global_dir()
    config = load_global_config()
    print("◈ Welcome to OpenSpawn")
    print("OpenSpawn gives your folders a persistent local AI agent.")
    print("AI is optional. Local scanning still works without it.\n")
    key = get_api_key()
    if key:
        print("Claude is already configured.")
        replace = input("Replace the saved Claude key? [y/N] ").strip().lower()
        if replace != "y":
            config.setup_complete = True
            save_global_config(config)
            return
    print("No Claude API key found.")
    print("Paste your Anthropic API key. It will be saved for OpenSpawn.")
    api_key = getpass.getpass("Anthropic API key: ").strip()
    if not api_key:
        print("No key entered. You can still use local-only mode.")
        return
    if not api_key.startswith("sk-ant-"):
        print("That key does not look like an Anthropic API key.")
        return
    print("Testing key...")
    try:
        ClaudeClient(api_key, config.model).chat("You are a health check.", "Reply with OK.", max_tokens=10)
        print("Claude test call succeeded.")
    except ClaudeError as exc:
        print(f"Claude test failed: {exc}")
        save_anyway = input("Save this key anyway? [y/N] ").strip().lower()
        if save_anyway != "y":
            print("Key was not saved.")
            return
    save_api_key(api_key)
    config.setup_complete = True
    save_global_config(config)
    print("Claude is now configured for OpenSpawn.")


def run_home() -> int:
    config = load_global_config()
    print("◈ OpenSpawn")
    print("Persistent local AI agents for your folders.")
    print("Drop a folder onto OpenSpawn.app, or run `openspawn /path/to/folder`.\n")
    if get_api_key():
        print("Claude is configured.")
    else:
        print("Claude is not configured. Run `setup` to enable chat, or continue in local-only mode.")
    agents = config.agents[-10:]
    if not agents:
        print("\nNo agents yet.")
        print("Create one with: openspawn /path/to/folder")
        return 0
    print("\nRecent agents:")
    for index, agent in enumerate(reversed(agents), start=1):
        path = agent.get("path", "")
        name = agent.get("name", Path(path).name if path else "Unknown")
        exists = "available" if Path(path, AGENT_DIRNAME).exists() else "missing"
        print(f"[{index}] {name} — {path} ({exists})")
    print("\nEnter a number to open, `setup` to configure Claude, or `q` to quit.")
    while True:
        choice = input("> ").strip()
        if not choice:
            continue
        lowered = choice.lower()
        if lowered in {"q", "quit", "exit"}:
            return 0
        if lowered == "setup":
            run_setup()
            return 0
        if choice.isdigit():
            selected = int(choice)
            ordered = list(reversed(agents))
            if 1 <= selected <= len(ordered):
                path = Path(ordered[selected - 1]["path"])
                session = AgentSession(path)
                session.open_existing()
                run_cli(session, created_new=False)
                return 0
        print("Enter a listed number, `setup`, or `q`.")


def run_cli(session: AgentSession, created_new: bool = False) -> None:
    print()
    if created_new:
        print(f"◈ Created agent for {session.config.name}")
        print(f"Folder: {session.folder}")
        print(f"Agent app: {session.folder / 'OpenSpawn Agent.app'}")
    else:
        print(f"◈ {session.config.name}")
        print(f"Folder: {session.folder}")

    print()
    for line in session.status_lines():
        print(line)
    if session.changes:
        print("\nChanges since last session:")
        for change in session.changes:
            detail = f" ({change.details})" if change.details else ""
            print(f"- {change.change_type}: {change.path}{detail}")
    print("\nAsk a question, or type `help` for commands.")

    client = None
    key = get_api_key()
    if key:
        client = ClaudeClient(key, session.config.model)
        print("\nClaude is configured for this session.")
        print()
        prompt = FIRST_OPEN_PROMPT if created_new else REOPEN_PROMPT
        try:
            _stream_with_progress(session, client, prompt, "Preparing session")
        except ClaudeError as exc:
            print(f"Claude error: {exc}")
    else:
        print("\nClaude is not configured. Local folder mode is available; run `setup` to enable chat.")

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nState saved. Goodbye.")
            session.close()
            return
        if not user_input:
            continue
        cmd = user_input.lower()
        if cmd in {"quit", "exit", "q"}:
            session.close()
            print("State saved. Goodbye.")
            return
        if cmd == "help":
            print_help()
            continue
        if cmd.startswith("save"):
            parts = user_input.split(maxsplit=1)
            filename = parts[1].strip() if len(parts) > 1 else None
            if not filename:
                from .utils import utc_now
                filename = f"openspawn-output-{utc_now()[:10]}.md"
            try:
                saved_path = session.save_response(filename)
                print(f"Saved to {saved_path}")
            except ValueError as exc:
                print(str(exc))
            continue
        if cmd == "done":
            with wait_indicator("Saving session"):
                note = session.capture_session_note(client)
            print("Session summary saved.")
            if note.open_threads:
                print("Open threads:")
                for item in note.open_threads:
                    print(f"- {item}")
            if note.decisions:
                print("Decisions:")
                for item in note.decisions:
                    print(f"- {item}")
            continue
        if cmd == "setup":
            run_setup()
            key = get_api_key()
            if key:
                client = ClaudeClient(key, session.config.model)
                print("Claude is configured for this session.")
            else:
                client = None
            continue
        if client is None:
            print("Claude is not configured. Run `setup` to add or replace your Claude key.")
            continue
        try:
            _stream_with_progress(session, client, user_input, "Thinking")
        except ClaudeError as exc:
            print(f"Claude error: {exc}")


def print_help() -> None:
    print("Ask a question about the folder, or use one of these commands:")
    print("  save [file]        Save last response to a file (.md or .docx)")
    print("  done               Save a session summary")
    print("  setup              Configure or replace Claude setup")
    print("  quit               Save and exit")


@contextmanager
def wait_indicator(message: str):
    stop_event = threading.Event()

    def run() -> None:
        frames = [".", "..", "..."]
        index = 0
        while not stop_event.is_set():
            sys.stdout.write(f"\r{message}{frames[index % len(frames)]}")
            sys.stdout.flush()
            index += 1
            if stop_event.wait(0.4):
                break

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop_event.set()
        thread.join(timeout=1)
        sys.stdout.write("\r" + " " * (len(message) + 3) + "\r")
        sys.stdout.flush()


def _stream_with_progress(session: AgentSession, client: ClaudeClient, question: str, label: str) -> str:
    """Stream a chat response, rendering each line with formatting as it completes."""
    start = time.monotonic()
    stop_event = threading.Event()
    first_chunk = True
    line_buffer = ""
    in_code_block = False

    def tick() -> None:
        while not stop_event.is_set():
            elapsed = int(time.monotonic() - start)
            sys.stdout.write(f"\r{label}  ({elapsed}s)   ")
            sys.stdout.flush()
            if stop_event.wait(1.0):
                break

    print()
    ticker = threading.Thread(target=tick, daemon=True)
    ticker.start()
    try:
        for chunk in session.chat_stream(client, question):
            if first_chunk:
                stop_event.set()
                ticker.join(timeout=2)
                sys.stdout.write("\r" + " " * (len(label) + 20) + "\r")
                sys.stdout.flush()
                first_chunk = False
            line_buffer += chunk
            while "\n" in line_buffer:
                line, line_buffer = line_buffer.split("\n", 1)
                rendered, in_code_block = render_line(line, in_code_block)
                for out_line in rendered:
                    print(out_line)
    finally:
        if first_chunk:
            stop_event.set()
            ticker.join(timeout=2)
            sys.stdout.write("\r" + " " * (len(label) + 20) + "\r")
            sys.stdout.flush()
    # Flush any remaining partial line
    if line_buffer.strip():
        rendered, _ = render_line(line_buffer, in_code_block)
        for out_line in rendered:
            print(out_line)
    return session.last_response


def normalize_folder_target(raw_target: str) -> Path:
    if raw_target.startswith("file://"):
        parsed = urlparse(raw_target)
        target = unquote(parsed.path)
        return Path(target).expanduser()
    return Path(raw_target).expanduser()
