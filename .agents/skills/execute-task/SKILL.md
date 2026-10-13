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

3. **Strict Security Directive (Zero Hardcoded Secrets):**
   - **NEVER** write real bot tokens, API keys, credentials, or sensitive data into Python source code, Settings default values, or tracked files.
   - All secrets MUST be loaded exclusively from the local `.env` file via `pydantic-settings` or `os.getenv`.
   - In `Settings` classes, declare `BOT_TOKEN: str = ""` (or without default). Never put real tokens as fallback values.
   - Ensure `.env` and `*.db` are strictly ignored by `.gitignore` and NEVER staged or committed.

4. **Verification:**
   - Verify all imports, syntax, and run linting/testing where applicable (e.g. `python -m py_compile ...`).
   - Check with `git diff` or `grep` that no secret or token has been accidentally introduced into tracked files.

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
