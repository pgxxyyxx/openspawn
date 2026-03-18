# OpenSpawn GitHub Beta Launch Plan

Updated: 2026-03-18

## Goal

Ship OpenSpawn publicly as a macOS GitHub beta without blocking on DMG packaging.

The beta should be good enough for early users to:

- download the repo from GitHub
- run setup
- launch `OpenSpawn.app`
- create/open a folder agent
- get a useful AI-generated first response
- ask grounded questions
- reopen through `OpenSpawn Agent.app`
- report problems

## Distribution Decision

Launch from GitHub first.

Why:

- fastest path to public testing
- lower packaging overhead than DMG + notarization work
- easier to iterate after early user feedback
- acceptable for beta users who can tolerate a little setup

## What We Are Shipping

- `OpenSpawn.app` in development/beta form
- `OpenSpawn.command` as shell fallback
- Python package + source in the repo
- folder-local `OpenSpawn Agent.app` convenience entrypoint
- local-first scan/read/state flow
- AI-generated session opening on first open and reopen
- grounded Claude chat when configured

## Beta Audience

Good beta users:

- macOS users
- comfortable downloading from GitHub
- comfortable following a short setup guide
- willing to tolerate rough edges and report issues

Not yet ideal for:

- non-technical users expecting App Store / signed-app smoothness
- users who need zero-setup install
- users who need enterprise packaging or broad deployment guarantees

## Required Beta Readiness

### Must pass before public release

- `OpenSpawn.app` launches on the maintainer machine from a clean repo checkout
- `OpenSpawn.command` works as a fallback
- `uv run python -m openspawn --setup` works
- a user can create/open a folder agent from `OpenSpawn.app`
- first-open and reopen responses feel useful on real folders
- grounded chat works on at least 3 real folders
- `OpenSpawn Agent.app` appears inside spawned folders with the right icon

### Strongly recommended before wider sharing

- test on a second Mac/user account
- tighten sparse chat responses for compare/summarize prompts
- confirm Claude failures are understandable and non-fatal
- confirm `.agent/` state behaves sensibly across reopen flows

## GitHub Release Shape

### Repo-first beta

Users:

1. clone or download the repo
2. install dependencies with `uv`
3. run setup
4. launch `OpenSpawn.app`

This is the fastest way to ship and is the current intended path.

## README Requirements

The public README should clearly include:

- what OpenSpawn is
- macOS-only beta status
- install steps
- Claude setup steps
- what `.agent/` stores locally
- what gets sent to Claude
- known rough edges
- how to report bugs

## Trust Notes For Beta

Be explicit about:

- OpenSpawn stores folder state in `.agent/`
- Claude features send selected prompt/file excerpts to Anthropic
- local startup still works without Claude
- AI responses may be imperfect, slow, or occasionally unavailable
- this is a beta, not yet polished distribution

## Known Beta Caveats

- macOS only
- unsigned / development-style app behavior may trigger friction on some systems
- some chat answers are still too terse for comparison-heavy questions
- launcher/runtime polish is beta-quality, not final distribution quality
- this is a GitHub beta, not a polished installer

## Immediate Next Tasks

1. run the final public-repo sanity pass
2. test core flows on multiple real folders
3. test on a second machine/account
4. push the public repo
5. gather feedback before doing bigger product expansion

## Release Checklist

- [x] README updated for public beta
- [x] beta caveats documented
- [x] feedback channel decided
- [x] issue template or bug-report path available
- [ ] launch tested on maintainer machine from the exact public repo state
- [ ] launch tested on second machine/account
- [x] GitHub release notes drafted
