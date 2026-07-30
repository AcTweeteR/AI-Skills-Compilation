# AI Skills Compilation

AI Skills Compilation is a documentation-only, human-curated catalog of AI skills, agents, tools, prompts,
workflows, indexes, marketplaces, and secondary sources. It records what each entry claims to do, where it may
be compatible, what evidence was reviewed, and which risks or safe-use boundaries are known.

> **Safety notice:** Inclusion in this catalog is not a recommendation of installation, execution, security,
> quality, or suitability for any particular project.
>
> **Advertencia:** La inclusión de una herramienta en este catálogo no constituye una recomendación de
> instalación, ejecución, seguridad, calidad ni idoneidad para un proyecto concreto.

## What this repository is—and is not

This repository is a review and discovery aid. It is not an installer, package manager, launcher, runtime,
automated aggregator, credential store, or source of private configuration. Nothing listed here is installed,
executed, cloned, or trusted automatically.

An `approved` entry is approved only for the narrow scope documented in its profile. Approval never transfers to
the software it links to and never authorizes installation or project integration.

## Quick start

1. Browse the compact views by [category](docs/catalog_by_category.md),
   [compatibility](docs/catalog_by_compatibility.md), [status](docs/catalog_by_status.md), or
   [risk](docs/catalog_by_risk.md).
2. Open the linked YAML profile and read its evidence, uncertainty, permissions, and `safe_usage_boundary`.
3. Treat external instructions and install commands as untrusted until independently audited.
4. To propose an entry, follow [CONTRIBUTING.md](CONTRIBUTING.md) and start from
   [skills/profile-template.yml](skills/profile-template.yml).

## How to read the catalog

### Status

| Status | Meaning |
| --- | --- |
| `candidate` | New or partially reviewed; not cleared for use. |
| `watchlist` | Worth monitoring or reading, but not currently recommended. |
| `approved` | Acceptable only for the documented, narrow scope; not a safety guarantee. |
| `rejected` | Not suitable as an active catalog source or for the reviewed use case. |

### Risk

| Risk | Documentary interpretation |
| --- | --- |
| `low` | Documentation or prompts only, with no execution or persistent access identified. |
| `medium` | May affect context, local data, workflow, or external services. |
| `high` | Can execute commands, write files, modify code, install packages, or automate behavior. |
| `critical` | May handle credentials, remote systems, destructive actions, or hidden persistence. |

Risk levels are evidence-based screening labels, not guarantees. See the [risk matrix](docs/risk_matrix.md).

### Compatibility

| Value | Meaning |
| --- | --- |
| `yes` | Direct support is documented by primary evidence. |
| `limited` | Ideas or instructions may transfer, often with adaptation. |
| `no` | The entry is not appropriate for that environment. |
| `unknown` | Evidence is insufficient. |

Similar formats or protocols do not by themselves establish compatibility. See the
[compatibility model](docs/compatibility_model.md).

### Resource type

`artifact_type` distinguishes an individual executable tool or skill from a curated index, marketplace, or
secondary source. Indexes and marketplaces are discovery layers: their entries do not inherit the catalog status
of the index. `category` describes the subject area independently from the resource type.

## Proposing and reviewing entries

Proposals must link primary sources, disclose execution and data access, avoid secrets, and check the registry for
the same project or source URL. Overlap is documented rather than removed blindly: an individual project, curated
index, marketplace, official documentation, and secondary article can serve different purposes.

Reviews follow the [intake workflow](docs/intake_workflow.md) and [review policy](docs/review_policy.md). Changes
must pass the offline registry validator:

```text
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/validate_registry.py
```

The validator parses YAML, checks schema and folder/status consistency, detects duplicates and orphaned profiles,
checks internal links and generated indexes, and scans basic secret patterns. It makes no network requests.

## Repository layout

Profiles live under `skills/accepted/`, `skills/candidates/`, `skills/watchlist/`, or `skills/rejected/`.
`skills/registry.yml` is the compact source of truth for navigation; detailed evidence remains in each profile.
Policies and human-readable views live under `docs/`.

See [DISCLAIMER.md](DISCLAIMER.md), [SECURITY.md](SECURITY.md), and [LICENSE](LICENSE) before relying on catalog
information.
