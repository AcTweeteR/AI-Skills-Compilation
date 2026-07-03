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
- Has optional scripts but they are not central to use.

Default action:

```yaml
install_allowed: false
execution_allowed: false
requires_sandbox: true
```

## High risk

Use `high` when the item can execute commands, modify files, change code, install packages, create hooks, or automate development behavior.

Typical signs:

- Shell commands.
- Package installation.
- Git hooks.
- Background agents.
- File writes.
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

Always increase risk if any of these are present:

| Feature | Minimum risk |
| --- | --- |
| Persistent memory | medium |
| Reads local files | medium |
| Writes local files | high |
| Executes shell commands | high |
| Modifies source code | high |
| Uses Git hooks | high |
| Runs in background | high |
| Uses credentials/secrets | critical |
| Remote execution | critical |
| Destructive file operations | critical |
| Obfuscated code | critical |

## Practical interpretation

A repository can be useful and still be too risky to install.

For many tools, the safest approach is to extract the idea into documentation or prompts instead of running the original project.
