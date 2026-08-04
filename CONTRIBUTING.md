# Contributing

Contributions should make the catalog clearer, more trustworthy, or easier to maintain. Adding more links is not
an objective by itself.

## Choose the fastest useful path

| Your goal | Use this path | Typical time |
| --- | --- | --- |
| Put one public project on the maintainer radar | [Repository Suggestion](https://github.com/AcTweeteR/AI-Skills-Compilation/issues/new?template=repository_suggestion.yml) | Under 10 minutes |
| Share evidence you already reviewed | [New Skill Review](https://github.com/AcTweeteR/AI-Skills-Compilation/issues/new?template=new_skill_review.yml) | Depends on evidence |
| Add or update a complete YAML profile | Pull request using the profile template | Depends on review depth |
| Fix wording, navigation, or validation | Focused issue or pull request | Depends on scope |

A quick suggestion does not need a completed security review. It needs one primary public URL, the correct resource
type if known, a concrete use case, known permissions or risks, and disclosure of your relationship to the source.

## Ten-minute repository suggestion

1. Search [`skills/registry.yml`](skills/registry.yml), open issues, and pull requests by name and source URL.
2. Open the [Repository Suggestion form](https://github.com/AcTweeteR/AI-Skills-Compilation/issues/new?template=repository_suggestion.yml).
3. Link the original repository or official documentation—not an article that merely mentions it.
4. Explain one distinct use case and any known file, network, credential, memory, shell, hook, or write access.
5. Disclose whether you maintain or contribute to the source, then submit.

Maintainers may close a suggestion as duplicate, request more evidence, or decide that the source does not justify
the recurring maintenance cost of a profile.

## Complete profile workflow

1. Copy [`skills/profile-template.yml`](skills/profile-template.yml) to `skills/candidates/<id>.yml`.
2. Replace every instructional value. Use lowercase kebab-case for the filename and `id`.
3. Use the public source account for `source_owner`. Record reviewed documentation languages under
   `content_languages`; do not infer programming languages.
4. Fill every AI target with `"yes"`, `limited`, `"no"`, or `unknown`. Direct support needs primary evidence.
5. Document data access, concrete risk reasons, evidence checked, uncertainty, safe-use boundary, and next action.
6. Add one compact matching record to `skills/registry.yml` in the documented order.
7. Regenerate navigation and run the checks below.

The [fictional worked example](docs/examples/candidate-profile.yml) demonstrates structure without recommending a
real project. Do not copy its compatibility or risk decisions into a real review.

## Classification rules

`artifact_type` and `category` answer different questions:

- `artifact_type` says whether the source is an executable tool, individual skill, curated index, marketplace, or
  secondary source.
- `category` says what subject it covers.

Frameworks, MCPs, agents, official documentation, and prompt collections should be described precisely in the
profile even when the current high-level type vocabulary groups them under a broader type. Propose a schema change
only when real entries demonstrate a recurring distinction that navigation needs.

New profiles start as `candidate`. Only maintainers move them to `watchlist`, `approved`, or `rejected` after a
documented decision. Folder and status must agree:

| Folder | Status |
| --- | --- |
| `skills/candidates/` | `candidate` |
| `skills/watchlist/` | `watchlist` |
| `skills/accepted/` | `approved` |
| `skills/rejected/` | `rejected` |

`approved` never means “safe to install.” It means only that the profile's narrow documented use was accepted.

## Evidence and safety rules

- Prefer original repositories and official documentation. Use secondary sources only for context or discovery.
- Use `unknown` when evidence is insufficient; never infer compatibility from a similar format or protocol.
- Do not execute, install, or copy commands from a cataloged project solely to prepare a contribution.
- Never include secrets, tokens, cookies, keys, private paths, private endpoints, family information, private
  repository names, client data, or realistic-looking credentials.
- Do not submit malware, stolen credentials, destructive tooling, evasion instructions, or promotional spam.
- Explain overlap instead of removing a source merely because an index, marketplace, and individual project cover
  related ground.

## Local checks

Run these validation commands from the repository root, using the repository's existing environment.

*   **Unit tests**: `python -m unittest discover -s tests -v`
    *   Expected outcome: All tests pass, reporting `OK` or similar.
*   **Registry validation**: `python scripts/validate_registry.py`
    *   Expected outcome: The script completes without errors, indicating successful validation.


The validator is offline. It parses repository YAML, validates profile schema and navigation, checks Markdown and
internal links, rejects duplicates and orphaned profiles, and scans common secret patterns. It never contacts or
runs cataloged projects.

## Pull request checklist

- [ ] One focused purpose and no unrelated cleanup.
- [ ] Primary evidence linked and relationship disclosed where relevant.
- [ ] Duplicate and overlap search completed.
- [ ] Compatibility, access, and risk claims are evidence-backed or `unknown`.
- [ ] Registry, profile, folder, status, and generated navigation agree.
- [ ] No secrets or private information.
- [ ] Tests and validator pass.
- [ ] Documentation impact and remaining uncertainty are explained.

The repository's pull request template repeats the merge-critical checks so reviewers can evaluate a contribution
without reconstructing its intent.
