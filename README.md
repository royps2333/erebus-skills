# Erebus Skills

Focused agent skills for evidence-based engineering: establish what happened,
choose a scoped response, and verify the result without overstating it.

## Available skills

| Skill | Use it for |
| --- | --- |
| [Telegram Delivery Diagnostics](skills/telegram-delivery-diagnostics/SKILL.md) | Investigating missing or duplicate bot replies, uncertain sends, and retry behavior; recognizing resolved or unproven incidents. |

## Install one skill

With the [Skills CLI](https://github.com/vercel-labs/skills):

```sh
npx skills add royps2333/erebus-skills --skill telegram-delivery-diagnostics
```

Select your supported agent when prompted. To list the catalog without installing:

```sh
npx skills add royps2333/erebus-skills --list
```

For a download without cloning the library, use the skill ZIP attached to the
[releases](https://github.com/royps2333/erebus-skills/releases). Extract the whole
skill folder into your agent's skill directory, preserving references and scripts.
A standalone SKILL.md is not the complete package. Release archives include MIT
license text. For reproducibility, use a tagged release and verify its SHA-256.

For Git users who want only this skill checked out:

```sh
git clone --depth 1 --filter=blob:none --sparse https://github.com/royps2333/erebus-skills.git
cd erebus-skills
git sparse-checkout set skills/telegram-delivery-diagnostics
```

Sparse checkout limits working-tree content; this remains a repository clone.

## What is verified

The first skill includes a Python standard-library simulator and nine offline
failure/restart tests. They demonstrate the tradeoff between replaying and holding
uncertain sends. They do not establish production reliability or exactly-once
Telegram delivery. The skill documents the fixture's limits and the API references.

```sh
python3 -B scripts/validate.py
```

Agent behavior varies. Independent agent evaluation is not claimed for this
initial release. Apply the skill to the evidence and permissions of your own task.

## Maintenance

Skills live in independent folders under `skills/`. Shared validation and catalog
maintenance live at repository level. Changes use GitHub Flow: focused branch,
pull request, checks and review, then merge. Releases have a repository tag and
separate skill archives. A release does not install or update anything for users.

See [CONTRIBUTING.md](CONTRIBUTING.md) for scope and verification expectations.
Licensed under [MIT](LICENSE). Maintained by royps2333 with AI-assisted development.
