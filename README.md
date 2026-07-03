# AI Skills Compilation

Private curated registry of AI skills, agents, tools, prompts, workflows, and repositories that may be useful with ChatGPT, OpenAI Codex, Claude, Claude Code, Perplexity, Gemini, Cursor, Windsurf, or other AI-assisted environments.

This repository is intentionally documentation-first. It is not an installer, package manager, runtime, or automation layer.

## Purpose

Use this repository to collect and review external AI-related repositories before deciding whether they are useful, safe, and appropriate for a specific workflow.

The registry helps answer:

- What does this skill/tool do?
- Which AI systems is it compatible with?
- Is it useful for ChatGPT, OpenAI Codex, Claude, Claude Code, Perplexity, Gemini, Cursor, Windsurf, or others?
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
│   ├── compatibility_model.md
│   ├── intake_workflow.md
│   ├── review_policy.md
│   ├── risk_matrix.md
│   └── usage_examples.md
└── skills/
    ├── README.md
    ├── registry.yml
    ├── accepted/
    ├── candidates/
    │   └── template.yml
    ├── watchlist/
    └── rejected/
```

## Status values

| Status | Meaning |
| --- | --- |
| `candidate` | Interesting but not reviewed enough for use. |
| `watchlist` | Worth monitoring, but not currently recommended. |
| `approved` | Reviewed and considered acceptable for a defined use case. |
| `rejected` | Not recommended due to risk, low value, poor maintenance, or unclear behavior. |

## Compatibility values

| Value | Meaning |
| --- | --- |
| `yes` | Directly useful for that AI system. |
| `limited` | Useful only as reference, prompt material, or with adaptation. |
| `no` | Not useful or not appropriate for that AI system. |
| `unknown` | Not enough information yet. |

Default compatibility targets:

- ChatGPT
- OpenAI Codex
- Claude
- Claude Code
- Perplexity
- Gemini
- Cursor
- Windsurf

## Risk levels

| Level | Meaning |
| --- | --- |
| `low` | Documentation-only, no execution, no credentials, no persistent changes. |
| `medium` | May affect workflow, context, local files, or external services. |
| `high` | Can execute commands, modify code, use hooks, write files, or affect automation. |
| `critical` | Handles credentials, remote execution, hidden persistence, destructive actions, or unclear control flow. |

## Recommended workflow

1. Paste or add the repository URL as a `candidate`.
2. Create or update a skill profile under `skills/candidates/`.
3. Summarize what it does in plain language.
4. Add compatibility by AI system.
5. Classify risks using `docs/risk_matrix.md`.
6. Decide whether it belongs in `accepted`, `watchlist`, or `rejected`.
7. Never install or execute it without a separate explicit review.

## Practical review output

Every reviewed repository should end with a simple decision:

```yaml
recommended_status: candidate | watchlist | approved | rejected
risk_level: low | medium | high | critical
install_allowed: true | false
execution_allowed: true | false
requires_sandbox: true | false
compatibility:
  chatgpt: yes | limited | no | unknown
  openai_codex: yes | limited | no | unknown
  claude: yes | limited | no | unknown
  claude_code: yes | limited | no | unknown
  perplexity: yes | limited | no | unknown
  gemini: yes | limited | no | unknown
  cursor: yes | limited | no | unknown
  windsurf: yes | limited | no | unknown
```

## Safety position

This repository should prefer caution. A useful tool is not automatically a safe tool.

Any item involving persistent memory, shell commands, Git hooks, background agents, browser automation, credential access, repository writes, or network calls must be treated as elevated risk until reviewed.
