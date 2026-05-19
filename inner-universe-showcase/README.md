# Minotaur Grand Mentor Inner Universe Showcase

This folder is a curated public snapshot of current local engineering work.

It is meant to show breadth without exposing private runtime material:

- quantitative research systems
- data-source adapters and validation logic
- backtesting and reporting workflows
- agent automation and local orchestration
- safety boundaries for credentials, private transcripts, logs, and local-only datasets

## Projects

| Project | What It Shows |
| --- | --- |
| `short_term_radar_mvp/` | Taiwan equity radar system with data adapters, scoring, stage gating, backtesting, reports, and tests. |
| `z3b-prime-center-third-buy/` | Multi-timeframe quantitative model prototype with rule engine, configs, docs, scripts, and tests. |
| `z3b-core-v2-docs/` | Model-family research notes and specification documents. |
| `private-discord-codex-bridge/` | Sanitized private Discord bot bridge that routes approved messages into local Codex automation. |

## Public Cleanup Rules Used

The copy in this folder excludes:

- real `.env` files and credentials
- logs, transcripts, local session state, and downloaded attachments
- raw/processed data, parquet datasets, temp folders, and cache directories
- generated binary/service artifacts
- dependency folders such as `node_modules`

The result is intended as a portfolio artifact, not a full production runtime clone.
