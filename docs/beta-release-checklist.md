# OpenSpawn Beta Release Checklist

Updated: 2026-03-18

Use this before each public GitHub beta release.

## Product Check

- [ ] `OpenSpawn.app` launches from the exact public repo state
- [x] `OpenSpawn.command` exists as fallback
- [x] `OpenSpawn Agent.app` appears inside spawned folders
- [x] folder-local agent apps inherit the custom icon
- [ ] first-open AI orientation feels useful on a real folder
- [ ] reopen AI orientation feels useful on a real folder
- [ ] grounded chat works with Claude configured

## Regression Folders

- [x] `amazon`
- [x] `amazon-2`
- [ ] one non-investor folder

## Install Check

- [ ] README install steps tested exactly as written from a fresh outsider-style flow including `open OpenSpawn.app`
- [x] `brew install uv` path available locally
- [x] `uv sync` works from a clean beta install pass
- [x] `uv run python -m openspawn --setup` works from a clean beta install pass

## Trust Check

- [x] README explains `.agent/` local state clearly
- [x] README explains what goes to Claude clearly
- [x] known beta caveats are still accurate
- [x] failure messages are understandable

## Release Prep

- [x] release notes drafted
- [ ] version / date references updated if needed
- [x] feedback path is visible in the README
- [x] issue template is present on GitHub
- [ ] public repo surface checked for private/local files

## Ship Decision

- [ ] good enough for early GitHub beta users
- [ ] not blocked on DMG/signing/notarization work

## Notes From Current Pass

- main app icon and generated folder-agent icon path are now fixed
- public README/release docs have been rewritten for the GitHub beta
- `CLAUDE.md` and the PRD are now kept out of the public repo surface
- remaining high-value checks are real product-feel tests and public-repo sanity, not major new features
