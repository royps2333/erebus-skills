# Security

Report vulnerabilities privately through this repository's Security tab using
“Report a vulnerability”. Do not place credentials or private incident records
in public issues or pull requests. No response-time guarantee is offered.

## Repository and release safeguards

CI uses GitHub-hosted runners, read-only permissions and commit-pinned actions.
Checkout credentials are not persisted. Pull requests cannot publish releases.
The manually dispatched release workflow runs only on main, validates and packages
with read-only permissions, then attests and publishes in a separate job. The
publishing job receives only the artifact and short-lived GitHub permissions.

Release archives contain tracked skill files and the MIT license. Verify both
the SHA256SUMS and GitHub attestation before installation:

```sh
gh attestation verify telegram-delivery-diagnostics-v0.1.1.zip --repo royps2333/erebus-skills
```

The initial v0.1.0 archive predates workflow provenance. Use v0.1.1 or later for
attested releases. Attestation establishes provenance, not absence of defects.

This is currently a sole-maintainer repository. PRs and passing checks are required,
but independent approval cannot be guaranteed. Repository administrators control
settings. These controls do not replace account security or user review of skills.
