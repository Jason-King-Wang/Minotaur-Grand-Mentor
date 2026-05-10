# short_term_radar Package

V2 radar package for daily scans, backtests, baseline comparisons, and Markdown reports.

Core modules:

- `adapters/`: local daily price, revenue, chip, catalyst, and read-only broker market-data adapters.
- `features/`: price-volume, expectation gap, theme group, revenue, chip, catalyst, and risk scoring.
- `scoring/`: score coverage/cap logic, stage classification, and reason generation.
- `backtest/`: forward labels, path max drawdown, metrics, simulator, and baseline strategies.
- `cli/`: scan, backtest, and report commands.

Stage gating:

- `S0`: no usable score.
- `S1`: new observation or watch-only.
- `S2`: early watch, often when revenue is missing.
- `S3`: candidate entry; requires revenue score, sufficient coverage, breakout/volume confirmation, and low risk.
- `S4`: hold/trail or wait pullback.
- `S5`: avoid chasing.

Broker adapter remains read-only. It accepts an already logged-in API object from the caller, fetches market data only, never handles credentials, and exposes no trading/account mutation methods.
