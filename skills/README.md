# Catalog records

This directory contains the structured, documentation-only AI catalog.

## Layout

| Path | Purpose |
| --- | --- |
| `registry.yml` | Compact central index and allowed vocabulary. |
| `profile-template.yml` | Template for a new proposal; it is not a catalog entry. |
| `candidates/` | New or partially reviewed entries with status `candidate`. |
| `watchlist/` | Entries worth monitoring with status `watchlist`. |
| `accepted/` | Narrowly approved entries with status `approved`. |
| `rejected/` | Rejected entries retained as decision history. |

Use lowercase kebab-case filenames and IDs. Each real profile must have exactly one matching compact entry in
`registry.yml`; the validator rejects duplicate IDs, duplicate sources, duplicate file references, missing files,
orphaned profiles, and registered paths outside the four profile directories. A `registry_file` must be a
canonical repository-relative `.yml` or `.yaml` path directly inside `skills/candidates/`, `skills/accepted/`,
`skills/watchlist/`, or `skills/rejected/`; absolute paths, `..`, nested paths, non-YAML files, symbolic links,
and incomplete profiles are rejected.

## Profile model

Profiles distinguish `artifact_type` from `category`. The type identifies whether the resource is an executable
tool, individual skill, curated index, marketplace, or secondary source. The category describes its subject. This
prevents a marketplace or article from being mistaken for an individual skill.

`source_owner` records the public account or publisher visible at the reviewed source; it does not assert legal
ownership. `content_languages` records languages of reviewed documentation, never inferred programming languages.

Use `unknown` when primary evidence is insufficient. Quote `"yes"` and `"no"` values under `compatibility` and
`data_access`; those values are documentary labels, while permission fields such as `install_allowed` are YAML
booleans.

Values `"yes"`, `likely`, and `possible` declare a capability and therefore activate the semantic risk floors in
[the risk matrix](../docs/risk_matrix.md). `unknown` records insufficient evidence and does not assert that a
capability exists. Profiles must include file, network, credential, persistent-memory, behavior-modification,
shell, hook, write, code-modification, browser-control, and automatic-commit fields.

Copy `profile-template.yml` to `candidates/<id>.yml`, replace every instructional value, and follow
[CONTRIBUTING.md](../CONTRIBUTING.md). Do not install or execute the proposed project during catalog review.
