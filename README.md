# AI Skills Compilation

Private curated registry of AI skills, agents, tools, prompts, workflows, and repositories that may be useful with ChatGPT, Codex, or other AI-assisted development environments.

This repository is intentionally documentation-first. It is not an installer, package manager, runtime, or automation layer.

## Purpose

Use this repository to collect and review external AI-related repositories before deciding whether they are useful, safe, and appropriate for a specific workflow.

The registry helps answer:

- What does this skill/tool do?
- Is it useful for ChatGPT, Codex, or both?
- Does it require installation or only documentation?
- Does it use memory, hooks, network access, terminal commands, credentials, or file writes?
- Is it safe to test?
- Should it remain only as reference material?

## Core rule

No external skill, agent, repository, script, hook, or automation is installed or executed just because it is listed here.

Every item must pass review before any real use.

## Repository structure

```text
.
├── AGENTS.md
├── README.md
├── docs/
│   ├── review_policy.md
│   ├── risk_matrix.md
│   └── usage_examples.md
└── skills/
    ├── README.md
    ├── registry.yml
    ├── accepted/
    ├── candidates/
    └── rejected/
```

## Status values

| Status | Meaning |
| --- | --- |
| `candidate` | Interesting but not reviewed enough for use. |
| `watchlist` | Worth monitoring, but not currently recommended. |
| `approved` | Reviewed and considered acceptable for a defined use case. |
| `rejected` | Not recommended due to risk, low value, poor maintenance, or unclear behavior. |

## Risk levels

| Level | Meaning |
| --- | --- |
| `low` | Documentation-only, no execution, no credentials, no persistent changes. |
| `medium` | May affect workflow, context, local files, or external services. |
| `high` | Can execute commands, modify code, use hooks, write files, or affect automation. |
| `critical` | Handles credentials, remote execution, hidden persistence, destructive actions, or unclear control flow. |

## Recommended workflow

1. Add the repository URL as a `candidate`.
2. Create or update a skill profile under `skills/candidates/`.
3. Summarize what it does and why it might be useful.
4. Classify risks using `docs/risk_matrix.md`.
5. Decide whether it belongs in `accepted`, `watchlist`, or `rejected`.
6. Never install or execute it without a separate explicit review.

## Practical use with ChatGPT or Codex

When evaluating a new repository, provide the URL and ask for a structured review using this registry format.

Recommended decision outputs:

- `recommended_for_chatgpt`: yes/no/limited
- `recommended_for_codex`: yes/no/limited
- `install_allowed`: true/false
- `execution_allowed`: true/false
- `requires_sandbox`: true/false
- `risk_level`: low/medium/high/critical

## Safety position

This repository should prefer caution. A useful tool is not automatically a safe tool.

Any item involving persistent memory, shell commands, Git hooks, background agents, browser automation, credential access, repository writes, or network calls must be treated as elevated risk until reviewed.
