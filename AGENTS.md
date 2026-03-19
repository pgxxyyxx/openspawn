# Repository Guidelines

## Project Structure & Module Organization

`openspawn/` contains the shipping Python package. Key modules include `cli.py` for the command-line entrypoint, `session.py` and `store.py` for persisted `.agent/` state, `scanner.py` and `extractor.py` for file discovery and content extraction, and `app_bundle.py` / `launcher.py` for macOS app generation. `tools/` holds one-off developer utilities such as `generate_spawn_icon.py`. Product and release notes live in `docs/`. Static website assets are under `website/`. Bundled macOS launchers such as `OpenSpawn.app` and `OpenSpawn.command` are checked in at the repo root.

## Build, Test, and Development Commands

Use `uv` with Python 3.12+:

- `uv sync`: create or refresh the local virtual environment.
- `uv run python -m openspawn --setup`: configure Anthropic access for local runs.
- `uv run python -m openspawn /path/to/folder`: launch OpenSpawn against a target folder.
- `uv run python -m openspawn --init --path /path/to/folder`: force creation of a new folder agent.
- `uv run python tools/generate_spawn_icon.py`: rebuild `build/OpenSpawn.icns` and refresh the checked-in app icon.

There is no dedicated build system or test runner config yet; use the CLI flows in `README.md` and `docs/test-plan-openspawn-stage0.md` as the current validation path.

## Coding Style & Naming Conventions

Follow the existing Python style: 4-space indentation, type hints where helpful, `snake_case` for functions and modules, and `CapWords` for classes. Keep modules focused and prefer `pathlib.Path` over manual path strings. Preserve the repo’s direct, dependency-light approach; do not add new tooling unless it is justified by repeated need. No formatter or linter is configured today, so match surrounding code closely.

## Testing Guidelines

This repo currently relies on manual validation of critical CLI flows rather than automated tests. When changing behavior, exercise first-launch, reopen, and degraded-mode scenarios from `docs/test-plan-openspawn-stage0.md`. If you add automated tests, place them in a top-level `tests/` package and name files `test_<feature>.py`.

## Commit & Pull Request Guidelines

Current history uses short, imperative commit subjects such as `add website` and `Initial beta release`. Keep commit titles brief, action-oriented, and scoped to one change. Pull requests should describe the user-visible effect, list manual verification steps, and include screenshots when app or website behavior changes. For bugs, mirror the issue template: include reproduction steps, folder type, Claude on/off status, and exact error text where available.
