# Usage examples

This document shows how to use the registry without making it complicated.

## Add a new repository

When a new repository is found, create a candidate profile.

Example request:

```text
Review this repository for the AI skills registry:
https://github.com/owner/repository

Classify what it does, which AI systems it is compatible with, risks, and whether it should be accepted, rejected, or kept as candidate/watchlist.
```

## Expected review output

A good review should answer:

- What does it do?
- Which AI systems can use it?
- Is it prompt-only, documentation-only, or executable?
- Does it need installation?
- Does it touch files, commands, memory, hooks, credentials, or network?
- Is it safe to use directly?
- Is it better as inspiration/documentation only?

## Simple compatibility summary

Use a short table in the review notes:

| AI system | Compatibility | Notes |
| --- | --- | --- |
| ChatGPT | limited | Can use the workflow as reference. |
| OpenAI Codex | `yes` | Useful for repository tasks. |
| Claude | limited | Prompt ideas may transfer. |
| Claude Code | `yes` | Designed for coding-agent workflows. |
| Perplexity | `no` | Not a research/search workflow. |
| Gemini | unknown | No specific support documented. |

## Example decision

```yaml
recommended_status: candidate
risk_level: high
reason: >
  Interesting coding-agent workflow, but it can modify files and execute commands. Keep as candidate until sandbox-tested.
install_allowed: false
execution_allowed: false
requires_sandbox: true
```

## Practical safe use

Many repositories should not be installed. Instead, extract useful parts:

- Prompt patterns.
- Review checklists.
- Agent rules.
- Folder structures.
- Safety policies.
- Documentation ideas.

This is often safer than using the original tool directly.

## Avoid clutter

Each skill profile should be understandable in less than one minute.

Prefer:

- Short summary.
- Clear compatibility table.
- Clear risk level.
- Clear next action.

Avoid:

- Long copied README sections.
- Unverified claims.
- Installation instructions unless explicitly approved.
- Ambiguous status labels.
