---
name: execute-task
description: >-
  Executes tasks specified in .agents/current_task.md strictly following project guidelines,
  enforcing zero scope creep, performing verification, and completing with an automatic git commit & push.
---

# Execute Task Skill

Use this skill to execute technical tasks formulated in `.agents/current_task.md`.

## Instructions for Execution Agent:

1. **Read Current Task:**
   - Always open and read `.agents/current_task.md` first.
   - Extract the goals, files to modify/create, constraints, and acceptance criteria.

2. **Strict Scope Discipline (Zero Scope Creep):**
   - Implement **ONLY** what is explicitly written in `.agents/current_task.md`.
   - Do NOT rewrite or "refactor" unrelated files or functions.
   - Do NOT add unrequested third-party integrations or features.
   - Preserve existing code and adhere strictly to framework best practices (e.g., aiogram 3.x routers/middlewares/filters, async SQLAlchemy 2.0).

3. **Verification:**
   - Verify all imports, syntax, and run linting/testing where applicable (e.g. `python -m py_compile ...`).
   - Ensure no hardcoded secrets exist in tracked files (use `.env` and `pydantic-settings`).

4. **Git Finalization (Mandatory):**
   - Stage all relevant changes: `git add .`
   - Commit with a descriptive message according to the task:
     `git commit -m "feat/fix: <task description>"`
   - Push to GitHub:
     `git push origin main`

5. **Report to User:**
   - List all created/modified files.
   - Provide a concise summary of executed work matching each requirement in `.agents/current_task.md`.
   - Confirm that changes have been committed and pushed to GitHub.
