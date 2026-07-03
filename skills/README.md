# Skills registry

This folder contains the structured catalog of AI skills, agents, prompts, workflows, and external repositories.

## Files and folders

```text
skills/
├── README.md
├── registry.yml
├── accepted/
├── candidates/
└── rejected/
```

## Recommended process

1. Add new repositories as `candidate`.
2. Create a detailed profile under `skills/candidates/`.
3. Review usefulness and risk.
4. Move or duplicate the final profile into:
   - `skills/accepted/`
   - `skills/rejected/`
   - or keep it as `watchlist` in `registry.yml`.

## File naming convention

Use lowercase names with hyphens:

```text
skills/candidates/example-skill.yml
skills/accepted/safe-prompt-pack.yml
skills/rejected/risky-agent.yml
```

## Minimum entry fields

Every skill entry should include:

- `id`
- `name`
- `source`
- `status`
- `category`
- `summary`
- `recommended_for_chatgpt`
- `recommended_for_codex`
- `risk_level`
- `install_allowed`
- `execution_allowed`
- `requires_sandbox`
- `review_notes`

## Default posture

New skills are not trusted. They remain candidates until reviewed.
