# Shared Agent-Learning Framework

This directory stores repository-specific learning as reviewable records. Records are evidence, not authority: `proposed` observations become `validated` only through a later review record or explicit decision.

## Read order

1. Read this file.
2. Read current records in [`decisions/`](decisions/) and [`unresolved/`](unresolved/).
3. Read only role-relevant records in [`lessons/`](lessons/).
4. Verify material conclusions against the referenced commit and repository evidence.
5. Never overwrite another agent's record; add a timestamped record that identifies any conflict.

## Record locations and schemas

| Record | Location | Required title | Required metadata | Template |
|---|---|---|---|---|
| Builder lesson | `lessons/builder/` | `# Agent Lesson Record` | Agent role, Task, Branch, Commit reviewed or produced, Date, Status | [`builder-lesson.md`](templates/builder-lesson.md) |
| Reviewer lesson | `lessons/reviewer/` | `# Reviewer Lesson Record` | Reviewer role, Scope, Branch, Commit reviewed, Date, Status | [`reviewer-lesson.md`](templates/reviewer-lesson.md) |
| Architecture decision | `decisions/` | `# Architecture Decision Record` | Decision owner, Decision, Branch, Commit, Date, Status | [`architecture-decision.md`](templates/architecture-decision.md) |
| Reusable pattern | `patterns/` | `# Reusable Pattern` | Pattern owner, Context, Evidence commit, Date, Status | [`reusable-pattern.md`](templates/reusable-pattern.md) |
| Unresolved question | `unresolved/` | `# Unresolved Question` | Owner, Question, Branch, Commit, Date, Status | [`unresolved-question.md`](templates/unresolved-question.md) |
| Synthesis | `synthesized-lessons.md` | `# Synthesized Lessons` | Synthesis owner, Evidence through commit, Date, Status | [`synthesized-lessons.md`](templates/synthesized-lessons.md) |

Record files use `YYYY-MM-DD-HHMM-short-topic.md`; template files and `synthesized-lessons.md` are exempt. Allowed statuses are `proposed`, `validated`, `rejected`, and `superseded`. A record must distinguish inspected evidence, observed facts, interpretation, and unresolved questions. Never include credentials, private telemetry, personal information, real-client data, or proprietary data.

## Validation

Run:

```powershell
python scripts/validate_agent_learning.py
pytest -q
```

The validator checks required metadata, status values, timestamped and case-insensitively unique record filenames, local Markdown links, repository-relative paths written as inline code, and common secret/private-data signatures. It cannot prove that a conclusion is true or that content is safe; reviewers remain responsible for evidence quality and contextual privacy review.

## Governance

- The record author chooses `proposed` unless review evidence justifies another state.
- A reviewer validates or rejects by creating a new reviewer record; do not silently edit the original conclusion.
- Architecture decisions state alternatives and consequences.
- Patterns require evidence from at least one concrete repository use and define where they do not apply.
- Unresolved questions name an owner or explicitly state that one is needed.
- Only an explicitly assigned synthesis role modifies `synthesized-lessons.md`.
