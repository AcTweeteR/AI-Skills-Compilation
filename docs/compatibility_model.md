# AI compatibility model

This repository tracks whether each skill, agent, tool, prompt pack, or workflow is useful with different AI systems.

The goal is to keep compatibility easy to understand and practical.

## Supported AI targets

Use these keys in skill profiles:

```yaml
compatibility:
  chatgpt: limited
  openai_codex: limited
  claude: limited
  claude_code: limited
  perplexity: no
  gemini: unknown
  cursor: unknown
  windsurf: unknown
  other: []
```

## Compatibility values

| Value | Meaning |
| --- | --- |
| `yes` | Directly useful for this AI system. |
| `limited` | Useful only as reference, prompt material, or with adaptation. |
| `no` | Not useful or not appropriate for this AI system. |
| `unknown` | Not enough information yet. |

## Recommended interpretation

### ChatGPT

Useful when the skill is mainly:

- Prompting guidance.
- Reusable workflows.
- Review checklists.
- Documented procedures.
- Reasoning frameworks.
- Non-executable instructions.

### OpenAI Codex

Useful when the skill helps with:

- Repository work.
- Code review.
- Tests.
- Refactoring.
- Project instructions.
- Development workflows.

Higher risk if it requires:

- Shell execution.
- Hooks.
- Package installation.
- Automatic code modification.
- Background agents.

### Claude

Useful when the skill is:

- Prompt-based.
- Documentation-based.
- Reasoning or writing oriented.
- Compatible with Claude Projects or custom instructions.

### Claude Code

Useful when the skill is designed for:

- Coding agents.
- Local repository work.
- Development workflows.
- Tool execution.
- Codebase analysis.

Treat as higher risk if it changes files, uses hooks, or installs tools.

### Perplexity

Useful when the skill is about:

- Research workflows.
- Source comparison.
- Web investigation.
- Search strategies.

Usually not compatible with local-code execution workflows.

### Gemini

Useful when the skill is:

- Prompt-based.
- Research-based.
- Multimodal.
- Documentation-oriented.

Compatibility depends on whether the skill requires a specific runtime.

### Cursor / Windsurf / other coding assistants

Useful when the skill is expressed as:

- Repository instructions.
- Rules files.
- Code review criteria.
- Development workflows.
- Agent behavior guidelines.

## Keep it simple

Do not over-document compatibility. Use short notes.

Example:

```yaml
compatibility_notes: >
  Best suited for Claude Code and Codex because it targets coding-agent workflows. ChatGPT can use the ideas as documentation, but should not execute the tool.
```
