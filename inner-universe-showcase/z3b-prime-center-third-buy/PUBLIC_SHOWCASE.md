# Z3B Prime Center Third-Buy - Public Showcase Notes

## One-Line Summary

A multi-timeframe quantitative trading model prototype built around 1H structure gating, 15m entry confirmation, state-machine rules, signal persistence, and execution-profile configuration.

## Engineering Highlights

- Python package layout with `src/`, `tests/`, `config/`, `scripts/`, and model documentation.
- Strict rule modeling for swing points, centers, signal routing, stop/target validation, and execution profiles.
- Separate round-lot and odd-lot Taiwan equity configuration examples.
- Synthetic sample data for deterministic local tests and demos.
- Test coverage for strategy rules, state machine behavior, center engine logic, data loading, execution profiles, and user-spoken rule alignment.

## Security / Public Scope

This public copy excludes real intraday parquet datasets, private reports, caches, logs, temporary pytest folders, and local machine artifacts. Only code, specs, configs, tests, and small sample CSV files are included.

## Good Interview Files

- `src/z3b_prime/`
- `tests/`
- `config/config.example.yaml`
- `config/sample.synthetic.yaml`
- `scripts/run_ab_preselect_top50_full_backtest.py`
- `docs/`
- `RULES.md`
