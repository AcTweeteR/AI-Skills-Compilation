# Repository intake workflow

Use this workflow whenever a new repository is added to the AI skills registry.

## Input

The user provides one or more repository URLs, for example:

```text
https://github.com/owner/repository
```

## Output

For each repository, create or update a concise skill profile that explains:

1. What it does.
2. Why it may be useful.
3. Which AI systems it is compatible with.
4. Whether it is prompt-only, documentation-only, or executable.
5. Whether it needs installation.
6. What permissions or data access it may require.
7. Main risks.
8. Recommended status.
9. Safe usage boundary.
10. Next action.

## Compatibility targets

Always evaluate compatibility with:

- ChatGPT
- OpenAI Codex
- Claude
- Claude Code
- Perplexity
- Gemini
- Cursor
- Windsurf
- Other relevant AI tools, if clearly applicable

## Review style

Keep the result practical and readable.

Good summary:

```text
A coding-agent workflow that helps maintain project memory and task context. Best suited for Claude Code and Codex. ChatGPT can use the ideas as documentation, but direct installation is not recommended until sandbox-tested.
```

Bad summary:

```text
This is an innovative framework that enhances AI productivity through advanced contextualized workflows.
```

## Default classification

New repositories start as:

```yaml
status: candidate
install_allowed: false
execution_allowed: false
requires_sandbox: true
```

## Decision values

Use simple compatibility values:

```yaml
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

## Final recommendation

End every review with one of these:

- Accept as documentation/reference.
- Keep as candidate.
- Move to watchlist.
- Reject.
- Test only in sandbox.

Do not recommend direct installation unless the repository has been reviewed carefully and the use case is narrow.
