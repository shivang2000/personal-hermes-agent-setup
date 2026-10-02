# Small-equity XAUUSD sizing and feasibility

Use this when a user asks whether an XAUUSD strategy tested on a large account can run on a very small balance.

## Separate four different quantities

Do not conflate:

1. **Backtest initial equity** — may be inferred from `net_profit / (net_profit_pct / 100)` when both are reported.
2. **Notional exposure** — `lots × contract_size × price`.
3. **Margin required** — depends on symbol contract and broker leverage.
4. **Loss at stop** — the binding safety quantity; depends on stop distance, contract size, lots, spread, commission and slippage.

Inferring backtest initial equity does not reveal margin, lot sizes or risk-per-trade. Treat those as unavailable until the authenticated strategy configuration/trade ledger is inspected.

## Runtime broker facts are authoritative

Query MT5 symbol metadata before sizing:

- `volume_min`
- `volume_step`
- `volume_max`
- `trade_contract_size`
- `trade_tick_size`
- `trade_tick_value`
- leverage/margin rate
- digits, stops level and current spread

Never hard-code the standard Gold contract as fact for every broker. For explanation only, a common XAUUSD contract is 100 oz per 1.00 lot, so 0.01 lot is about 1 oz and a $1 Gold move is about $1 P/L at 0.01 lot.

## Feasibility formula

For a simple linear contract:

```text
risk_dollars = equity × risk_pct / 100
raw_lots = risk_dollars / (stop_distance_price × contract_size)
```

Prefer tick-value-based sizing in production because it respects broker symbol specifications and account currency.

Example under the common 100-oz contract:

```text
equity = $50
risk = 0.2% = $0.10
stop distance = $10
raw lots = 0.10 / (10 × 100) = 0.0001
```

If the broker minimum is 0.01, the requested risk cannot be represented. The correct result is **reject/skip the trade**, not round up.

## Critical minimum-lot rule

This pattern is unsafe for small accounts:

```python
volume = max(min_lot, calculated_volume)
```

It silently converts a safely sized sub-minimum order into an oversized order. Use an explicit feasibility gate:

```python
if calculated_volume < broker_min_volume:
    raise RiskLimitExceeded(
        "required_volume_below_broker_minimum",
        calculated_volume,
        broker_min_volume,
    )
```

Then quantize **down** to `volume_step`; never quantize upward beyond the risk budget. Recompute worst-case stopped loss after quantization and reject if it exceeds the cap.

## Decision table

| Broker XAU minimum | Typical implication for a $50 balance |
|---|---|
| 0.01 | Usually unsafe/unrepresentable for H1 ATR stops |
| 0.001 | Often still 1–several percent risk per ordinary H1 stop |
| 0.0001 | May represent sub-1% risk; verify contract and costs |

A cent/nano account can make a strategy mechanically representable, but does not validate profitability.

## Scaling public backtests

A proportional return/drawdown illustration is acceptable only when labeled hypothetical. Lot rounding, fixed commissions, minimum volume, leverage, nonlinear compounding and different data mean a small account will not reproduce the percentage curve automatically.

Use the public result to estimate what perfect proportional scaling would look like, then immediately apply the broker feasibility gate. Do not promise that result.

## Required tests before enabling a small account

1. Calculated lot below minimum is rejected, never clamped up.
2. Lot-step quantization rounds down.
3. Post-quantization worst-case loss including costs stays under the risk budget.
4. Insufficient margin rejects before order submission.
5. A wide spread or stops-level violation rejects.
6. Account balance/equity and symbol metadata come from live MT5 state.
7. Daily/overall halt state persists across restart.
8. Closed-bar strategy logic remains identical across account sizes; only sizing changes.

## Recommended output structure

Answer the user in this order:

1. inferred backtest equity and its confidence;
2. hypothetical proportional return/drawdown;
3. minimum-lot and margin feasibility;
4. concrete stop-loss examples;
5. safe implementation rule (`reject`, not `round up`);
6. viable alternatives such as cent/nano execution or signal-only validation.
