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
and orphaned profiles.

## Profile model

Profiles distinguish `artifact_type` from `category`. The type identifies whether the resource is an executable
tool, individual skill, curated index, marketplace, or secondary source. The category describes its subject. This
prevents a marketplace or article from being mistaken for an individual skill.

Use `unknown` when primary evidence is insufficient. Quote `"yes"` and `"no"` values under `compatibility` and
`data_access`; those values are documentary labels, while permission fields such as `install_allowed` are YAML
booleans.

Copy `profile-template.yml` to `candidates/<id>.yml`, replace every instructional value, and follow
[CONTRIBUTING.md](../CONTRIBUTING.md). Do not install or execute the proposed project during catalog review.
