# Review policy

This policy defines how to evaluate AI skills, agents, tools, prompt packs, workflows, and repositories before adding them to the registry.

## Main principle

Listing a repository here is not approval to install, execute, or integrate it.

Every entry starts as `candidate` unless there is already a documented review.

## Review checklist

For every new repository, check:

1. What problem does it solve?
2. Is it useful for ChatGPT, Codex, or both?
3. Is it documentation-only, prompt-only, or executable?
4. Does it require installation?
5. Does it execute shell commands?
6. Does it write to files or modify code?
7. Does it use Git hooks or background processes?
8. Does it access the network?
9. Does it store memory or persistent state?
10. Does it require secrets, tokens, cookies, API keys, or OAuth access?
11. Is the repository maintained?
12. Are there open issues about safety, malware, data loss, or broken behavior?
13. Can the useful idea be copied as documentation instead of installing the tool?

## Status decisions

### candidate

Use this for new or partially reviewed items.

Default for all new repositories.

### watchlist

Use this when the concept is interesting but the tool should not be used yet.

Common reasons:

- Too new.
- Not enough documentation.
- Useful idea but risky implementation.
- Needs later review.

### approved

Use this only when the safe use case is narrow and clearly documented.

Approval must include:

- Approved use case.
- Risk level.
- Limitations.
- Whether installation is allowed.
- Whether execution is allowed.
- Whether sandbox testing is required.

### rejected

Use this when the tool should not be used.

Common reasons:

- Hidden or excessive automation.
- Requires risky permissions.
- Poor transparency.
- Writes or modifies code without clear boundaries.
- Unclear license.
- Low value compared with risk.
- Abandoned or unreliable.

## Default safety decisions

| Question | Default answer |
| --- | --- |
| Install allowed? | No |
| Execution allowed? | No |
| Sandbox required? | Yes |
| Human review required? | Yes |
| Approved for other projects? | No |

## Repository review output

Each review should end with a practical decision:

```yaml
recommended_status: candidate | watchlist | approved | rejected
risk_level: low | medium | high | critical
recommended_for_chatgpt: yes | no | limited
recommended_for_codex: yes | no | limited
install_allowed: true | false
execution_allowed: true | false
requires_sandbox: true | false
reason: short explanation
```

## Integration policy

Approval here does not authorize integration into another repository.

Real project integration requires:

1. Separate branch.
2. Separate review.
3. Clear rollback path.
4. No secrets in code.
5. Explicit human approval.
