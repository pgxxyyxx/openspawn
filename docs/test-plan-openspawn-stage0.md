# Test Plan

Generated from PRD engineering review on 2026-03-18
Branch: master
Repo: openspawn/prototype

## Affected Pages/Routes

- CLI first-launch flow — verify provider setup, skip-AI flow, and degraded-mode messaging
- CLI spawn flow — verify folder indexing, extraction progress, partial-state messaging, and session entry
- CLI open flow — verify change detection, state reload, and status summary
- CLI command surface — verify `status`, `files`, `memory`, `history`, `scan`, `scan more`, `read <file>`, and `why`

## Key Interactions to Verify

- Launch without prior config and skip AI setup
- Launch without prior config and complete Claude setup
- Spawn an agent from a small fixture folder
- Re-open the same folder after add/modify/delete changes
- Ask a question answered from already-read content
- Ask a question that triggers on-demand file reading
- Ask a question when only metadata is available
- Recover from provider failure while keeping the session usable
- Recover from corrupt but recoverable `.agent` state

## Edge Cases

- Empty folder or hidden-files-only folder
- No readable supported files
- Large folder that exceeds initial indexing and read budget
- PDF parse timeout or encrypted PDF
- Malformed Excel workbook
- Unsupported binary file
- Missing state files
- Partially written or malformed JSON in `.agent`
- Metadata-only answer must not imply full file read

## Critical Paths

- First launch -> skip AI -> spawn folder -> use non-AI commands successfully
- First launch -> configure Claude -> spawn folder -> ask grounded question with file citations
- Spawn folder -> persist state -> reopen later -> detect changes -> preserve continuity
- Ask about not-yet-read file -> on-demand read -> answer from content or explain limitation clearly
- Provider failure during answer -> clear error -> remain in usable session
