# Minotaur Grand Mentor / Inner Universe Showcase

This repository is organized into two clearly separated public areas.

## 1. VTuber Archive

`vtuber-archive/` contains the original Minotaur Grand Mentor VTuber work:

- PNGTuber and Live2D-ready asset planning
- OBS overlay and dashboard
- character bible, prompts, task board, validation tools, and handoff notes

Status: archived for now. The project is preserved, but it is not the current development focus.

## 2. Inner Universe Showcase

`inner-universe-showcase/` is the current public portfolio area. It is a security-scrubbed selection of local work prepared for interview review.

Included projects:

- `inner-universe-showcase/projects/short_term_radar_mvp/` - Taiwan equity short-term radar with scoring, stage gating, official-source collectors, backtesting, reports, and tests.
- `z3b-prime-center-third-buy/` - multi-timeframe quantitative trading model prototype with rule definitions, strategy engine code, tests, configs, and sample data.
- `z3b-core-v2-docs/` - research/spec notes for the Z3B model family.
- `private-discord-codex-bridge/` - sanitized private Discord-to-local-Codex bridge code showing local automation orchestration patterns.

## Security Boundary

This public version intentionally excludes:

- real `.env` files, API keys, bot tokens, cookies, credentials, and certificates
- Discord transcripts, local session state, logs, and downloaded attachments
- raw/processed market data, parquet datasets, caches, temp folders, and broker runtime files
- `node_modules`, Python bytecode, generated test caches, daemon binaries, and local machine-only files

See `SECURITY.md` for the public publishing rules used for this cleanup.

## Interview Reading Path

Start with:

1. `inner-universe-showcase/README.md`
2. `inner-universe-showcase/projects/short_term_radar_mvp/README.md`
3. `inner-universe-showcase/z3b-prime-center-third-buy/README.md`
4. `inner-universe-showcase/private-discord-codex-bridge/README.md`

This repository is for research, engineering demonstration, education, and entertainment only. It is not investment advice and does not contain production trading credentials.
