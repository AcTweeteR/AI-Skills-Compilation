# GitHub growth and community report

## Executive assessment

AI Skills Compilation has a credible differentiator: it is an evidence and risk catalog, not a collection measured
by link volume. The strongest growth strategy is therefore to make trust visible, contribution easy, and review
quality repeatable. Stars are useful for discovery but are not evidence of accuracy, and this report makes no
forecast or deadline for reaching a star count.

This work builds on the separate public-readiness PR. It does not replace its security, licensing, schema, or
open-source preparation.

## Improvements implemented

| Change | Design decision | Expected impact |
| --- | --- | --- |
| First-visit README | Lead with one sentence, a local banner, verifiable badges, quick start, and safety boundary. | Visitors can understand purpose and next action within the first screen. |
| Featured Reviews | Highlight documentation quality while keeping status and risk visible. | Demonstrates the review standard without implying endorsement. |
| Eight generated views | Navigate by use case, AI, category, source owner, status, risk, content language, and review date. | More entry points without duplicating profile content. |
| Source metadata | Add public source account and reviewed content language only. | Supports discovery without inventing legal ownership or implementation languages. |
| Issue forms | Separate quick suggestions, full reviews, bugs, docs, questions, and features. | Lower contributor uncertainty and better issue quality. |
| Pull request checklist | Put evidence, safety, synchronization, and validation at review time. | Fewer incomplete or unsafe submissions. |
| Community documents | Add support routing, roadmap, changelog, vision, rationale, and recommended labels. | Clear expectations for users, contributors, and maintainers. |
| Offline quality checks | Extend existing validation to all YAML, Markdown structure, HTML/local links, and generated views. | Stronger CI without sending catalog data to another service. |
| Contribution example | Provide one explicitly fictional, schema-valid profile. | Shows the expected result without endorsing or duplicating a real tool. |

## Comparable repositories reviewed

The review examined public documentation patterns; no text, branding, catalog entries, or claims were copied.

- [sindresorhus/awesome](https://github.com/sindresorhus/awesome) demonstrates visible navigation, a separate
  contribution path, and strict scope. This project adopts clear navigation and contribution routing, but not
  breadth as a success metric.
- [f/awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts) demonstrates an immediate value
  proposition and a low-friction contribution action. This project adopts fast orientation, but rejects unverified
  social proof and does not add a website, runtime, or automatic content synchronization.
- [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) demonstrates strong
  categorization and an explicit quality position. This project adopts visible selection principles, but treats
  entry count and popularity as discovery signals rather than proof of safety.

The resulting identity is deliberately institutional and neutral: compact review records, explicit uncertainty,
and risk-aware navigation rather than promotional ranking.

## Improvements deliberately not implemented

- **Automatic topic or label mutation:** repository metadata is a maintainer governance decision and may require
  broader permissions. Recommendations are documented below.
- **Funding accounts:** no verified account was provided. `FUNDING.yml` remains intentionally unconfigured.
- **External Markdown, analytics, link-check, or badge services in CI:** they add network and supply-chain
  dependencies without enough benefit for seven profiles.
- **Automatic external project checks:** CI must not download or execute cataloged software.
- **Popularity rankings, “best” labels, or compatibility scores:** the current evidence cannot support them.
- **Bulk import or automatic aggregation:** it would undermine review quality and create unbounded maintenance.
- **Website, search backend, database, or API:** static GitHub navigation is sufficient at current scale.
- **Invented testimonials, usage numbers, company claims, or growth forecasts:** none are needed to communicate
  the project's real strengths.

## Current strengths

- Documentation-only and offline-first trust boundary.
- Structured profiles covering compatibility, data access, risk, evidence, and safe-use limits.
- Negative and rejected decisions are retained, reducing repeated research.
- Central registry and generated navigation are checked for drift.
- Conservative vocabulary makes uncertainty visible.
- Community paths now distinguish a quick suggestion from an evidence-backed review.

## Current weaknesses

- Only seven real profiles, concentrated in coding-agent discovery and context tooling.
- Review evidence is currently recorded by a single reviewer identity and would benefit from broader peer review.
- Reviewed documentation is English-only.
- External freshness is manual; source ownership and behavior can change after review.
- No established release cadence or historical adoption data.
- The high-level `artifact_type` vocabulary does not yet model MCPs, agents, frameworks, and prompts separately;
  adding types before real entries require them would be speculative.

## Opportunities

- Become the neutral comparison layer between large indexes, marketplaces, and individual executable tools.
- Publish careful reviews in underserved areas such as MCP permissions, agent persistence, and prompt-only risk.
- Attract security, documentation, and developer-tool contributors through bounded evidence tasks.
- Use review freshness and correction history as stronger reputation signals than raw catalog size.
- Build relationships with upstream maintainers by inviting factual corrections without granting promotional
  control over the review.

## Quick wins for maintainers

1. Merge and verify the public-readiness PR before this growth PR so the two diffs remain independent.
2. Add the recommended labels in [recommended_labels.md](recommended_labels.md).
3. Set a concise GitHub description: “Evidence-first catalog for comparing AI skills, agents, MCPs, prompts,
   frameworks, and tools by compatibility and risk.”
4. Add reviewed repository topics from the list below.
5. Enable GitHub private vulnerability reporting if it is not already enabled.
6. Pin the Repository Suggestion issue form or a short contribution issue when the first external contributors
   arrive.
7. Select two or three evidence-refresh tasks as `good-first-issue`; do not manufacture issues solely for optics.

## Recommended GitHub topics

Apply manually after maintainer review:

`ai-tools`, `ai-agents`, `agent-skills`, `mcp`, `model-context-protocol`, `prompts`, `llm`, `llm-tools`,
`developer-tools`, `codex`, `claude-code`, `chatgpt`, `gemini`, `security`, `curated-list`

The README already uses the principal search vocabulary in headings and introductory text. Avoid repeating keyword
lists in prose; natural, precise language is more credible and readable.

## Reputation strategy by community milestone

These are capability gates, not promises or reasons to lower acceptance criteria.

### Toward 100 stars — prove the core loop

- Keep the README and suggestion path exceptionally clear.
- Respond quickly and neutrally to the first factual corrections and suggestions.
- Publish a small number of exemplary reviews across distinct resource types.
- Create only real, bounded documentation or evidence tasks for first-time contributors.
- Track which navigation paths users mention in issues; do not add analytics yet.

### Toward 500 stars — establish review cadence

- Define review freshness expectations by risk and source volatility.
- Recruit at least one additional reviewer for high-risk or specialized entries.
- Start concise release notes when meaningful catalog batches justify them.
- Document recurring acceptance and rejection patterns as policy links, not duplicated prose.

### Toward 1,000 stars — strengthen governance

- Formalize maintainer roles, review ownership, and conflict-of-interest disclosure.
- Require peer review for `approved` changes and critical-risk reassessments.
- Measure stale reviews, correction time, contributor return rate, and unresolved `needs-review` work.
- Expand resource-type vocabulary only where a meaningful body of entries demonstrates the need.

### Toward 5,000 stars — scale curation, not ingestion

- Introduce domain reviewers for MCPs, agents, prompts, frameworks, and security-sensitive tools.
- Consider cached external link monitoring that never downloads or executes cataloged code.
- Publish methodology summaries and correction history so downstream users can evaluate the catalog process.
- Maintain a capacity limit: new entries should not outpace evidence refresh and review staffing.

### Toward 10,000 stars — operate as durable public infrastructure

- Establish transparent governance, maintainer succession, and a documented dispute process.
- Maintain versioned schema and methodology changes with migration notes.
- Support translations only with accountable native-language reviewers and freshness ownership.
- Explore a read-only generated website or API only if GitHub navigation is demonstrably insufficient.
- Preserve vendor neutrality through disclosure, independent review, and separation between funding and catalog
  decisions.

## Recommended next actions

Prioritized by effort-to-impact ratio:

1. Merge the prerequisite public-readiness PR and rebase this work onto `main`.
2. Apply the repository description, topics, labels, and private reporting setting manually.
3. Invite factual review of the existing seven profiles before adding new ones.
4. Open two genuine evidence-refresh issues with complete acceptance criteria.
5. Reassess navigation after the catalog contains enough varied entries to reveal real gaps.

The project should resist any growth tactic that makes the catalog look larger while making its claims harder to
verify or maintain.
