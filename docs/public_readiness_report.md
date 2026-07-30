# Public readiness report

## Scope

This audit reviewed the complete tracked repository and Git history available on 2026-07-30. It covered public
documentation, agent instructions, all seven catalog profiles, the central registry, status directories, hidden
repository configuration, internal links, external source availability, YAML parsing, privacy patterns, CI, and
the generated catalog views.

The repository visibility was changed from private to public by explicit owner instruction immediately before the
audit. That action intentionally superseded the original audit prompt's instruction to leave visibility unchanged.
No release was created, and no cataloged skill, agent, MCP, script, installer, or repository was installed,
executed, or cloned.

## Files reviewed

- Root governance and public-facing files: `AGENTS.md`, `README.md`, and all repository files present before the
  audit.
- Catalog model: `skills/README.md`, `skills/registry.yml`, the profile template, and every YAML profile under
  `skills/accepted/`, `skills/candidates/`, `skills/watchlist/`, and `skills/rejected/`.
- Existing policy documents under `docs/`.
- All commits and patches reachable from the local Git history.
- Hidden files and the final untracked-file list.

## Privacy and security findings

No tokens, API keys, passwords, authorization headers, private keys, personal filesystem paths, private IP
addresses, internal domains, Home Assistant references, family data, private repository names, private endpoints,
or personal email addresses were found in the tracked tree or reachable history. Commit metadata contains only the
repository owner's public GitHub username and GitHub-provided `users.noreply.github.com` address.

The words “private”, “token”, “secret”, and similar terms occur in safety policies and risk descriptions. They do
not contain credential values or identify private systems. No history rewrite or secret rotation was required.

## Structural findings and changes

- Moved the instructional profile template out of `skills/candidates/`; it is no longer an apparent orphaned
  candidate.
- Added `artifact_type` so executable tools, individual skills, curated indexes, marketplaces, and secondary
  sources cannot be confused with subject categories.
- Consolidated categories into `agent-memory`, `context-management`, `skill-discovery`, and
  `secondary-reference`.
- Quoted documentary `"yes"` and `"no"` values to prevent YAML 1.1 parsers from converting them to booleans.
- Reduced `skills/registry.yml` to one compact navigation record per profile and updated `last_updated`.
- Ordered tools, indexes, marketplace, and secondary sources predictably, with rejected material last.
- Updated Awesome Codex Skills to its canonical redirected repository URL.

All seven real profiles have unique IDs, unique source URLs, valid statuses, valid risk levels, complete required
fields, matching status directories, and exactly one central registry record. No duplicate profiles were found.
Overlap among curated indexes, the marketplace, and secondary articles was retained because those source types
serve different documented purposes.

## Public documentation added or revised

- Reworked `README.md` with a quick start, visible disclaimer, status/risk/compatibility guidance, resource-type
  distinctions, contribution workflow, and documentation-only boundary.
- Added `DISCLAIMER.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, and an MIT `LICENSE`.
- Added `.gitignore`, `.editorconfig`, and `.gitattributes` for repository hygiene and secret-bearing file
  exclusions.
- Added compact generated views by category, compatibility, status, and risk.
- Updated existing policy documents and repository instructions to match a public catalog.

No prior license or documented preference for a different license existed. The MIT license therefore follows the
audit requirement without attributing copyright to an external project.

## Automated validation

`scripts/validate_registry.py` performs no network requests. It checks:

- safe YAML parsing and required schema fields;
- profile-template conformance without treating the template as a catalog entry;
- allowed statuses, risk levels, artifact types, compatibility labels, and data-access labels;
- unique IDs, source URLs, and registry file references;
- public HTTPS source format without embedded credentials or private hosts;
- folder/status agreement, missing files, orphan profiles, and registry/profile identity agreement;
- predictable registry ordering and current generated indexes;
- internal Markdown file and heading links;
- committed environment files, symbolic links, local paths, private IPs, email addresses, private keys, and common
  credential formats.

PyYAML 6.0.3 is the only third-party runtime dependency and is pinned in `requirements-dev.txt`. It is necessary
because YAML parsing should not rely on a partial custom parser. CI uses read-only permissions, a five-minute
timeout, concurrency cancellation, and official GitHub actions pinned to immutable commit SHAs. CI provisions the
pinned dependency, then validation itself remains offline and never runs cataloged software.

Checks completed locally:

- Python compilation of the validator and tests: passed.
- YAML/schema/catalog validator: passed.
- Seven unit tests: passed.
- Generated-index freshness check: passed.
- Internal-link check: passed.
- Basic current-tree secret scan: passed.
- Reachable-history privacy pattern scan: passed.
- Git whitespace check: passed.
- External HEAD availability check: six sources returned `200`; the rejected Medium source returned `403` to an
  automated request.

## Limitations and residual risks

- Pattern matching cannot prove the absence of every possible secret, encoded value, or sensitive inference.
- GitHub's public visibility was enabled before the audit, as explicitly requested by the owner. The audit found no
  known exposure, but publication preceded this report.
- CI intentionally avoids outbound catalog checks. External ownership, content, redirects, compatibility, and
  safety can change after review.
- The Medium source could not be verified automatically because it returned `403`; it remains rejected and is
  retained only as documented decision history.
- Documentary review does not replace source-code, dependency, runtime, license, or sandbox audits of linked
  projects.

## Recommendation

**READY_WITH_WARNINGS**

The repository is suitable to remain public as a documentation-only catalog. No known sensitive exposure remains,
the catalog and registry are consistent, and CI enforces the principal invariants. Human reviewers should confirm
the public-facing wording, the MIT license choice, the intended handling of the rejected Medium record, and the
documented fact that visibility was changed before merging this work.
