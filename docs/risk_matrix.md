# Risk matrix

Use this matrix to classify every skill, repository, tool, agent, workflow, or prompt pack.

## Low risk

Use `low` when the item is documentation-only or prompt-only and does not require execution.

Typical signs:

- Markdown files only.
- Prompt examples only.
- No install step.
- No shell commands.
- No credentials.
- No network access.
- No persistent memory.
- No file writes.

Default action:

```yaml
install_allowed: false
execution_allowed: false
requires_sandbox: false
```

## Medium risk

Use `medium` when the item may affect workflow, local context, project files, or external services, but does not appear to have high-risk automation.

Typical signs:

- Requires a local configuration file.
- Stores memory or notes.
- Reads local files.
- Uses network APIs without sensitive credentials.
- Changes assistant behavior through instructions or context.
- Writes non-code files without executing commands.
- Has optional scripts but they are not central to use.

Default action:

```yaml
install_allowed: false
execution_allowed: false
requires_sandbox: true
```

## High risk

Use `high` when the item can execute commands, modify code or security-sensitive configuration, install packages,
create hooks, control a browser, commit automatically, or automate development behavior.

Typical signs:

- Shell commands.
- Package installation.
- Git hooks.
- Background agents.
- Source-code or security-sensitive configuration writes.
- Code modification.
- Automatic commits.
- Browser automation.
- Tool calling with broad permissions.
- Unclear installation scripts.

Default action:

```yaml
install_allowed: false
execution_allowed: false
requires_sandbox: true
```

## Critical risk

Use `critical` when the item may affect secrets, credentials, remote systems, destructive operations, or hidden persistence.

Typical signs:

- API keys, OAuth tokens, cookies, SSH keys, or password handling.
- Remote command execution.
- Destructive commands.
- Exfiltration risk.
- Obfuscated code.
- Dependency confusion risk.
- Hidden background services.
- Self-updating behavior.
- Production integration without clear boundaries.

Default action:

```yaml
install_allowed: false
execution_allowed: false
requires_sandbox: true
```

## Escalation rules

The validator applies these minimums whenever a capability is declared as `"yes"`, `likely`, or `possible`.
`unknown` means that evidence is insufficient and does not itself declare the capability; reviewers should keep
uncertain new entries at least `medium` until the evidence is resolved. A higher classification is always valid.

| Feature | Minimum risk |
| --- | --- |
| Persistent memory | medium |
| Reads local files | medium |
| Network access | medium |
| Writes local non-code files | medium |
| Modifies assistant/agent behavior | medium |
| Executes shell commands | high |
| Modifies source code | high |
| Uses Git hooks | high |
| Browser control or automation | high |
| Automatic commits | high |
| Installation, execution, or project-integration permission enabled | high |
| Runs in background | high |
| Credential access or handling capability | high |
| Remote execution | critical |
| Destructive file operations | critical |
| Obfuscated code | critical |

All three values that assert or reasonably indicate a capability (`"yes"`, `likely`, and `possible`) are treated
the same for the floor check so uncertainty cannot be used to understate risk.

Use `critical` above that automated floor when evidence shows actual sensitive credentials, remote-system impact,
destructive behavior, exfiltration risk, or hidden persistence. The automated minimum is not a ceiling.

## Practical interpretation

A repository can be useful and still be too risky to install.

For many tools, the safest approach is to extract the idea into documentation or prompts instead of running the original project.
