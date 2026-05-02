# Repository Guidelines

## Project Structure & Module Organization

`bin/openspawn-pi-launcher.sh` is the active runtime entrypoint for the current Pi-backed spike. The checked-in `OpenSpawn.app` opens this launcher, which prepares `.openspawn/` folder memory, updates the OpenSpawn-owned block in `.pi/APPEND_SYSTEM.md`, and starts `pi` in the dropped folder.

`openspawn/` contains the earlier Python package and the macOS app-generation helpers. Key legacy modules include `cli.py`, `session.py`, `store.py`, `scanner.py`, `extractor.py`, `context.py`, and `skills.py`. `app_bundle.py` and `launcher.py` are still used to generate app wrappers, but the active app path now points at the shell launcher and Pi. `tools/` holds developer utilities such as `generate_spawn_icon.py`. Product and release notes live in `docs/`. Static website assets are under `website/`. Bundled macOS launchers such as `OpenSpawn.app` and `OpenSpawn.command` are checked in at the repo root.

Design principle for the current memory pipeline: **plain files first**. Source files stay in the user folder; the agent maintains durable markdown memory under `.openspawn/`; `.pi/APPEND_SYSTEM.md` carries folder-local Pi instructions. Keep this memory inspectable and easy to correct.

## Build, Test, and Development Commands

Use Pi for the active product path and `uv` for Python-backed app/icon tooling:

- `npm install -g @mariozechner/pi-coding-agent`: install Pi.
- `bin/openspawn-pi-launcher.sh /path/to/folder`: run the active OpenSpawn/Pi launcher directly.
- `uv run python tools/generate_spawn_icon.py`: rebuild `build/OpenSpawn.icns` and refresh the checked-in app icon.
- `uv run python -c "from pathlib import Path; from openspawn.app_bundle import build_main_app; build_main_app(Path('OpenSpawn.app'))"`: rebuild the checked-in macOS app wrapper.
- `uv sync`: create or refresh the local Python environment for legacy tooling.

There is no dedicated build system or test runner config yet; use the launcher flows in `README.md` and `docs/test-plan-openspawn-stage0.md` as the current validation path.

## Coding Style & Naming Conventions

Follow the existing Python style when touching Python: 4-space indentation, type hints where helpful, `snake_case` for functions and modules, and `CapWords` for classes. Shell scripts should stay POSIX-ish bash with `set -euo pipefail`, clear preflight checks, and careful quoting. Preserve the repo's direct, dependency-light approach; do not add new tooling unless it is justified by repeated need. No formatter or linter is configured today, so match surrounding code closely.

## Testing Guidelines

This repo currently relies on manual validation of critical launcher flows rather than automated tests. When changing behavior, exercise no-auth preflight, first launch with auth, reopen, and `.openspawn/` memory update scenarios from `docs/test-plan-openspawn-stage0.md`. If you add automated tests, place them in a top-level `tests/` package and name files `test_<feature>.py`.

## Commit & Pull Request Guidelines

Current history uses short, imperative commit subjects such as `add website` and `Initial beta release`. Keep commit titles brief, action-oriented, and scoped to one change. Pull requests should describe the user-visible effect, list manual verification steps, and include screenshots when app or website behavior changes. For bugs, mirror the issue template: include reproduction steps, folder type, Claude on/off status, and exact error text where available.
