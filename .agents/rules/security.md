# Security Policy: Zero Hardcoded Secrets

1. **NO SECRETS IN CODE:**
   - Under no circumstances should real Telegram Bot tokens, API keys, passwords, or personal credentials be placed directly into Python source code (`.py`), JavaScript/TypeScript files (`.ts`, `.tsx`, `.js`), JSON configs, or markdown documentation.
2. **USE ENVIRONMENT VARIABLES:**
   - Always load tokens exclusively from `.env` using `pydantic_settings.BaseSettings` or `os.getenv`.
   - In Pydantic Settings classes, declare fields with empty or placeholder defaults:
     ```python
     BOT_TOKEN: str = ""
     ADMIN_IDS: list[int] = []
     ```
   - Never provide a real secret string as a default value.
3. **GIT SAFETY:**
   - `.env`, `.env.local`, `*.db`, and `*.sqlite3` must remain strictly ignored in `.gitignore`.
   - Never stage or commit `.env`.
