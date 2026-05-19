# Private Discord Codex Bridge

This is a sanitized public slice of a private Discord assistant bridge.

## What It Demonstrates

- Discord bot access control by approved user and channel ids
- optional DM handling for approved users
- queueing and timeout control for local Codex jobs
- per-channel Codex session continuity
- attachment receive/send guardrails
- OpenAI fallback mode with local Codex fallback
- Windows-friendly service/watch scripts in the private version

## What Is Not Published

- real `.env`
- Discord bot token
- OpenAI API key
- approved user/channel ids
- transcripts
- local Codex session store
- logs
- downloaded attachments
- daemon binaries and local Windows service artifacts
- `node_modules`

## Files Included

- `src/index.js`
- `src/codexBridge.js`
- `package.json`
- `package-lock.json`
- `.env.example`

The included `.env.example` is a placeholder template only. Do not put real tokens in public commits.
