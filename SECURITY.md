# Security Policy

This repository is public. Do not commit private runtime material.

## Never Commit

- `.env` files with real values
- API keys, Discord bot tokens, OpenAI keys, broker credentials, cookies, passwords, or certificates
- Discord transcripts, local Codex session ids, message logs, or downloaded private attachments
- raw/processed market data, parquet datasets, broker runtime outputs, caches, or temporary test folders
- `node_modules`, Python bytecode, local virtual environments, binaries, or machine-specific service artifacts

## Allowed Public Material

- source code with placeholder config only
- documentation, architecture notes, and sanitized examples
- small synthetic/sample datasets that do not contain private account, user, or credential data
- generated reports that are safe for public portfolio review

## Local-Only Workspaces

The canonical private workspace remains:

`C:\Users\User\Documents\New project 4`

Only curated files copied into this repository should be treated as public.

## If Something Sensitive Is Found

Remove it from the public branch immediately, rotate the affected credential, and inspect Git history before assuming the exposure is gone.
