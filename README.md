# Autonomous AI YouTube Content Assistant

A fully automated YouTube content assistant that manages your channel from trend research to video publishing.

## Features
- Daily video generation (1 Short + 1 Long-form)
- Automated trend research
- Original script writing
- Professional voiceovers
- Video editing and publishing
- Analytics tracking
- Continuous learning and improvement

## Getting Started

See `GETTING_STARTED.md` for full setup instructions.

## Configuration

Copy the example environment file and fill in your own values:

```bash
cp .env.example .env
```

Never commit the `.env` file — it is already listed in `.gitignore`.

## Security Best Practices

- **Never hard-code API keys** in source files.
- Use `.env` for local secrets and inject environment variables in CI/CD.
- `.env` is listed in `.gitignore` so it will not be committed accidentally.
- Use `.env.example` as a template with placeholder values only.
- Rotate any API key that has been accidentally exposed in chat, logs, or version control.
- Use the `config.py` helper to access environment variables safely at runtime.
