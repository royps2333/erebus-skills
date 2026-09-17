# Contributing

Open an issue describing the use case, or a focused pull request with the problem,
change and verification. A skill should supply non-obvious reusable guidance and
work independently of the author's environment.

- Keep `SKILL.md` concise, with `name` and `description` YAML frontmatter.
- Put conditional detail in linked references and reusable code in scripts.
- Use synthetic fixtures. Do not submit tokens, personal conversations, real
  recipient IDs, private URLs, internal paths or confidential incident records.
- Separate observed incidents, reproduced failure modes, historical repairs and
  unresolved hypotheses. “No change needed” is a valid diagnostic result.
- Explain what tests prove and what remains untested. Don't replace demonstrated
  behavior with test counts or wording-only checks.
- Run `python3 -B scripts/validate.py` and describe any additional validation.

Maintainer review and passing checks precede merge. Small fixes can share a release;
new skills should include their own examples, boundaries and relevant tests.
All contributions are submitted under this repository's MIT license.
