# OpenSpawn TODOs

## Current Priority

### GitHub beta launch readiness

Status: now

Why:
- the product shape is now coherent enough to ship publicly from GitHub
- the main remaining risk is not missing product scope; it is rough edges in the real launch path
- the next learning should come from real beta users, not more internal feature branching

What to finish:
- run the full public beta flow end to end on the maintainer machine
- test the same flow on at least one second machine or user account
- make sure `OpenSpawn.app`, `OpenSpawn.command`, and folder-local `OpenSpawn Agent.app` all behave sensibly
- make Claude-backed startup/chat flows feel reliable enough for early users
- finalize the public repo/release surface and push

Success looks like:
- an outside user can install from GitHub and get to a useful folder session without hand-holding
- the app opens with a useful AI-generated orientation on first open and reopen
- failures are understandable and do not break the session
- the repo and release docs match the real product

## Near-Term

### Improve startup and chat quality

Status: next

Why:
- the product is now intentionally AI-first at the session layer
- first-open and reopen responses need to feel strong enough to carry the default experience
- comparison and synthesis answers are still sometimes too terse

What to improve:
- tighten first-open and reopen prompt quality
- improve depth and structure for compare/summarize questions
- reduce repeated or generic “what do you want me to do next?” suggestions
- keep recommendations tied to likely user intent and folder purpose

### Claude latency and reliability

Status: next

Why:
- Claude-backed flows are now core to the visible product experience
- timeouts and slow responses are still a meaningful beta risk

What to improve:
- reduce timeout frequency
- improve fallback messaging when Claude is slow or unavailable
- consider streaming or better progressive wait UX later if needed

## Later

### Packaging and identity polish

Status: later

Why:
- the product loop works, but distribution and wrapper polish are still beta-grade

What to build:
- cleaner packaging than GitHub-first beta
- signing/notarization path
- broader app identity polish

### Skills / modes

Status: later

Why:
- the likely next product expansion is folder-specific ways of working
- skills are a better long-term extension point than adding lots of hardcoded commands

What to build:
- skill-aware prompting
- selectable or inferred folder modes
- skill-shaped suggestions and outputs

## Explicitly not now

- multi-provider support
- rules/automation engine
- full multi-agent orchestration
- background daemons
- autonomous file edits
