# AGENTS.md

This repository is a private documentation registry for AI skills, agents, tools, prompts, workflows, and external repositories.

It must be treated as a safety-focused catalog, not as an executable workspace.

## Mandatory rules for AI assistants

1. Do not install dependencies from listed repositories.
2. Do not execute code from listed repositories.
3. Do not add Git hooks, shell scripts, background jobs, cron tasks, package scripts, or automation without explicit human approval.
4. Do not add secrets, API keys, tokens, cookies, private credentials, SSH keys, or `.env` files.
5. Do not modify unrelated repositories based only on an item listed here.
6. Do not mark a skill as approved unless the review notes explain the use case and risk boundary.
7. Do not treat external repository README claims as sufficient evidence of safety.
8. Prefer documentation-only entries unless testing is explicitly requested.
9. If a repository can write files, execute commands, use network access, persist memory, or alter agent behavior, classify it as at least `medium` risk.
10. If a repository uses hooks, shell execution, code modification, browser control, credential access, or automatic commits, classify it as at least `high` risk unless there is a clear reason not to.

## Review expectations

When reviewing a new skill, produce a structured profile with:

- Repository URL
- Summary
- Intended use
- ChatGPT usefulness
- Codex usefulness
- Installation requirements
- Execution behavior
- Data handled
- Permissions required
- Risk level
- Reasons for the risk level
- Recommended status
- Safe usage boundary
- Next review action

## Status rules

- `candidate`: default for all new entries.
- `watchlist`: useful idea but not recommended now.
- `approved`: reviewed for a narrow, defined use case.
- `rejected`: unsafe, unnecessary, abandoned, unclear, or not worth using.

## Integration rule

Approval in this repository does not approve integration into any other project.

Any integration into a real project must happen through a separate branch, review, and explicit decision.

## Preferred style

Keep entries concise, practical, and skeptical. Focus on whether the skill is useful and safe enough for the user's actual workflows.
