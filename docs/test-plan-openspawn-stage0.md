# Test Plan

Updated for the Pi-backed launcher spike on 2026-05-02.
Branch: master
Repo: openspawn/prototype

## Affected Pages/Routes

- Main app droplet flow — verify a dropped folder opens `bin/openspawn-pi-launcher.sh`
- Pi auth preflight — verify no `.openspawn/` memory is created before Pi credentials exist
- First-run flow — verify `.openspawn/` and `.pi/APPEND_SYSTEM.md` are created after auth
- Reopen flow — verify existing `.openspawn/` memory is read before new orientation work
- Icon/app wrapper — verify `OpenSpawn.app` uses the rebuilt app icon and launches the shell path

## Key Interactions to Verify

- Launch without Pi installed and confirm the install message is clear
- Launch with Pi installed but no credentials and confirm the user is directed to `/login`
- Confirm no `.openspawn/` folder is created during the no-auth setup path
- Complete Pi login with an API-key provider or subscription provider
- Drag a small fixture folder onto `OpenSpawn.app`
- Confirm `.openspawn/project.md`, `.openspawn/wiki/index.md`, `.openspawn/wiki/log.md`, and `.pi/APPEND_SYSTEM.md` are created
- Confirm existing `.pi/APPEND_SYSTEM.md` content is preserved outside the marked OpenSpawn block
- Confirm Pi writes a useful first orientation and durable wiki pages
- Re-open the same folder and confirm Pi uses `.openspawn/` memory before inspecting new files
- Confirm app icon updates after running `tools/generate_spawn_icon.py` and rebuilding `OpenSpawn.app`

## Edge Cases

- Empty folder or hidden-files-only folder
- Folder that already has `.pi/APPEND_SYSTEM.md`
- Folder that already has `.openspawn/` from a prior run
- Folder path with spaces
- Folder path received as `file://...`
- No Pi binary on `PATH`
- Empty or malformed Pi auth file
- Provider login succeeds but selected model later fails
- User asks Pi to edit source files before OpenSpawn has produced an orientation

## Critical Paths

- Drag folder -> no auth -> `/login` guidance -> no `.openspawn/` created
- Drag folder -> auth present -> scaffold `.openspawn/` -> Pi writes first orientation and wiki
- Drag same folder later -> Pi reads memory -> updates wiki/log -> gives reopen note
- Existing `.pi/APPEND_SYSTEM.md` -> launcher updates only the OpenSpawn block
- Rebuild icon -> rebuild app -> dragged folder still launches Pi path
