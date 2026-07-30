# Security policy

## Scope

This repository stores documentation and structured catalog records. It does not install or execute cataloged
software, make runtime calls to listed projects, or provide a trust guarantee for external links.

Relevant reports include:

- a secret, credential, personal path, or private-system reference exposed in this repository or its history;
- a catalog link that redirects to malware, phishing, compromised content, or an unexpected owner;
- a profile that materially understates permissions, destructive behavior, credential access, persistence, or
  another safety risk;
- a weakness in the offline validator or CI configuration that could hide unsafe catalog content.

## Reporting sensitive issues

Do not open a public issue containing a secret, credential, private URL, exploit detail, or personal data. Use the
repository's **GitHub Security Advisories** private reporting channel if it is available. If private reporting is
not enabled, open a public issue containing only a request for a private maintainer contact; do not include the
sensitive details.

For a non-sensitive broken link or classification concern, a public issue is appropriate. Include the profile
path, the affected URL or claim, the observed risk, and primary evidence where safe to share.

## Response expectations

Maintainers will triage the report, remove or generalize exposed data, reassess the entry, and document any
remaining risk. A compromised link may be removed or marked rejected before a complete investigation. Secret
rotation belongs to the affected owner; deleting a value from the current branch does not remove it from Git
history or revoke it.

Do not test a suspected external project against real credentials, personal data, or production systems on behalf
of this repository.
