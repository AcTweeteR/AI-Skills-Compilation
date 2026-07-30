# Contributing

Contributions improve a documentation-only safety catalog. They must not turn the repository into an installer,
runtime, package manager, launcher, or automatic code aggregator.

## Before proposing an entry

1. Search `skills/registry.yml` by project name, normalized URL, and likely aliases.
2. Decide whether the source is an individual skill, executable tool, curated index, marketplace, official
   documentation, framework, MCP, agent, or secondary source.
3. Prefer the original repository or official documentation. Secondary articles may support discovery but must
   not replace primary evidence.
4. Explain why an apparently overlapping source adds a distinct perspective. Do not copy all entries from an
   index or marketplace.

## Required information

Copy `skills/profile-template.yml` into `skills/candidates/<id>.yml` and provide evidence-backed values for:

- identity, public HTTPS source, artifact type, category, and plain-language summary;
- main features and best use case;
- per-environment compatibility and compatibility notes;
- useful and unsuitable use cases;
- risk level and concrete risk reasons;
- installation, execution, sandbox, and integration decisions;
- local file, network, credential, memory, shell, hook, write, and code-modification access;
- review date, reviewer identity or role, evidence checked, notes, safe-use boundary, and next action.

Use `unknown` when evidence is insufficient. Quote compatibility or data-access values of `"yes"` and `"no"` so
YAML parsers do not convert them to booleans. Do not claim compatibility merely because formats look similar.

## Allowed states and review process

New proposals start as `candidate`. Maintainers may move a profile to `watchlist`, `approved`, or `rejected` after
documenting the evidence and decision boundary. Folder and `status` must match:

| Folder | Status |
| --- | --- |
| `skills/candidates/` | `candidate` |
| `skills/watchlist/` | `watchlist` |
| `skills/accepted/` | `approved` |
| `skills/rejected/` | `rejected` |

`approved` means only that a narrow documented use—often read-only discovery—was accepted. It never authorizes
installation, execution, or integration into another project.

## Safety and content rules

Never include secrets, tokens, cookies, credentials, private keys, personal paths, private endpoints, internal
project names, family information, private repository references, or realistic-looking example credentials. Do
not submit malware, stolen credentials, destructive tooling, evasion instructions, or content intended to harm
systems or people.

Do not execute, install, or copy commands from a cataloged project while preparing a contribution. Summarize
external installation instructions only when they are relevant evidence of risk.

## Local checks

Install the single pinned development dependency, then run:

```text
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/validate_registry.py --write-indexes
python scripts/validate_registry.py
```

Review the generated indexes and the complete diff before opening a pull request. The validator performs no
network requests; external link availability requires separate human review.
