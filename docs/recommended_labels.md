# Recommended GitHub labels

These labels are documented for maintainers to create or update manually. Automation does not change repository
labels because label names, colors, and descriptions are repository governance decisions.

| Label | Suggested purpose |
| --- | --- |
| `documentation` | README, policy, navigation, or wording improvement. |
| `approved` | Work concerning an approved profile or decision. |
| `candidate` | New or partially reviewed catalog entry. |
| `watchlist` | Monitoring or reassessment of a watchlist entry. |
| `rejected` | Decision history or reconsideration of a rejected entry. |
| `needs-review` | Evidence or maintainer decision is still required. |
| `duplicate` | Existing profile, source, issue, or pull request already covers the proposal. |
| `high-risk` | Entry can execute commands, modify code or sensitive configuration, use credentials, control browsers, or automate commits. |
| `good-first-issue` | Small, bounded task with clear acceptance criteria and no specialized access. |
| `help-wanted` | Maintainers explicitly welcome community assistance. |

Recommended use rules:

- Apply status labels to catalog work, not to the external project's claimed maturity.
- Use `high-risk` for triage visibility; the profile's `risk_level` remains the source of truth.
- Reserve `good-first-issue` for tasks that can be completed safely from public documentation.
- Do not apply `duplicate` without linking the earlier item.
