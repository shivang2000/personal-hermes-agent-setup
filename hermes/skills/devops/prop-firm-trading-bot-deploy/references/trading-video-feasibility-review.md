# Trading-Video Strategy Feasibility Review

Use this reference when a user asks whether a YouTube trading-bot video is feasible, profitable, or suitable for an existing funded/MT5 system.

## 1. Inspect the source before judging

1. Retrieve video metadata: title, creator, date, duration, description, chapters, and links.
2. Extract captions. If YouTube captions are unavailable or rate-limited, download audio and use an available local speech-to-text model. Treat low-quality transcription as approximate.
3. Inspect screenshots/frames only when the transcript omits parameters shown on screen. Avoid downloading full video when a narrow section is enough.
4. Prefer official broker/API documentation over the creator's description for current integration and order permissions.

## 2. Separate three different claims

Do not collapse these into one "AI bot" claim:

- **Research assistant:** an LLM reads live/historical data and explains it.
- **Strategy generator:** an LLM searches parameters or emits Pine/Python code; runtime trading is deterministic.
- **Autonomous execution system:** a service handles authentication, risk, orders, fills, reconciliation, and failure recovery.

A video can prove the first while providing no evidence for the second or third.

## 3. Reconstruct the strategy as a specification

Extract, or explicitly mark missing:

- market, broker, venue, symbol universe, direction
- timeframe and session timezone
- exact entry/exit rules and indicator parameters
- bar-close vs intrabar timing and repaint/look-ahead behavior
- stop, target, trailing, re-entry, pyramiding
- position sizing and compounding
- spread, commission, slippage, swaps/funding
- test date range, sample size, market regimes

If exact Pine/Python code is unavailable, engineering feasibility may still be high, but profitability is **not reproducible**.

## 4. Grade evidence, not marketing

Evidence hierarchy, strongest first:

1. independently reproduced broker-data backtest with realistic costs
2. clean out-of-sample/walk-forward result
3. timestamped forward-test trade ledger
4. broker statement reconciled to signals and fills
5. creator's TradingView screenshot
6. headline return or selected winning trades

Require at least: trade count, test period, profit factor, drawdown, expectancy, costs, and sizing. A huge return without period/sizing is not decision-useful. An optimized winner selected from thousands of variants has selection bias even when TradingView reproduces the same result.

## 5. Test compatibility with the target account

Compare the strategy's historical drawdown and loss clustering against the bot's tighter internal limits, not only the prop firm's breach threshold. A 28% backtest drawdown is incompatible with a 6% funded-account limit unless risk is reduced and the re-scaled strategy is re-tested.

For low-win-rate/high-R strategies, expect long losing streaks. For short-volatility options strategies, model gap/tail risk and transaction costs rather than relying on win rate.

## 6. Choose the right implementation boundary

### Deterministic indicator strategy

Implement directly in the strategy engine:

```text
broker candles -> deterministic indicators -> Signal -> RiskManager -> executor
```

Do not relay internal technical signals through YouTube audio, TradingView, or Telegram unless those systems are genuinely external sources.

### LLM-assisted broker analysis

Keep the LLM advisory:

```text
broker data -> deterministic calculations -> LLM explanation -> risk validation -> approval/executor
```

Never let the LLM be the sole authority for quantity, final price, margin, fill status, or account state.

### Different broker/asset class

Use a separate broker adapter and risk boundary. MT5 CFDs and Zerodha NSE/NFO options differ in authentication, symbols, expiries, lot sizes, margin, multi-leg execution, charges, and reconciliation. Share domain events where useful; do not merge execution semantics.

## 7. Multi-leg options minimum controls

For Iron Condors and similar structures:

- normalize the option chain and instrument master
- calculate Greeks, payoff, margin, and maximum loss locally
- enforce liquidity/open-interest/spread thresholds
- place protective wings before short legs
- verify every fill and hedge/unwind on partial failure
- use idempotency tags and restart reconciliation
- account for brokerage, statutory charges, slippage, and expiry behavior
- authenticate according to the broker's session lifecycle

A suggested strategy with a declared "max loss" is not executable evidence until these controls are implemented.

## 8. Investigate public strategy databases reproducibly

When a creator links a public strategy browser or leaderboard, use it as a lead generator, not as proof.

1. Inspect browser network resources to find the JSON search endpoint instead of manually reading cards.
2. Inspect the page's own filter-building JavaScript for exact query names. Do not guess snake_case when the API uses camelCase.
3. Query on symbol, timeframe, minimum trades, maximum drawdown, profit factor, and a risk-adjusted sort axis. Example shape:

```text
/strategies/search?symbol=XAUUSD&timeframe=1h&minTrades=300&maxDrawdownPct=10&minProfitFactor=1.3&sort=sharpe&limit=50&offset=0
```

4. Preserve strategy ID, result ID, name, version, `forkedFromStrategyId`, creation time, test interval, bars, trades, gross profit/loss, net return, drawdown, profit factor, Sharpe, Sortino, and win rate.
5. Compare these fields directly with the video. A matching name/indicator family is not necessarily the creator's original strategy: a result created after publication or carrying `forkedFromStrategyId` is a later fork.
6. Treat authenticated `fork.json`, Pine, or strategy-source download as the reproduction boundary. Public KPI cards without source/config are evidence of a reported backtest, not enough to port or validate it.
7. Reject "best profit" as the default ranking for funded accounts. It frequently surfaces leverage-heavy results with drawdowns far beyond the account limit and tiny samples. Start with minimum sample size and sort by Sharpe/Sortino; inspect drawdown and costs before return.
8. If risk is linearly scaled to estimate prop-limit compatibility, label it as triage only. Lot rounding, compounding, path dependence, spread, and stop behavior break exact proportionality. Re-run the strategy at the proposed size before approving it.
9. Check whether duplicated cards share identical metrics/result families; repeated forks do not increase independent evidence.

## 8b. Read-only Trader.dev investigation through Codex MCP

The public `/browse` page is a catalogue, not the MCP endpoint. Use the provider-published MCP transport and keep the first pass read-only:

```bash
codex mcp add trader-dev -- npx -y mcp-remote https://mcp.trader.dev/sse
codex mcp get trader-dev
```

Codex may discover both read and mutating tools. Do not solve non-interactive approval failures with unrestricted host access. In `~/.codex/config.toml`, pre-approve only the audit tools needed for the investigation:

```toml
[mcp_servers.trader-dev.tools.whoami]
approval_mode = "approve"

[mcp_servers.trader-dev.tools.login]
approval_mode = "approve"

[mcp_servers.trader-dev.tools.get_strategy]
approval_mode = "approve"

[mcp_servers.trader-dev.tools.get_backtest_result]
approval_mode = "approve"

[mcp_servers.trader-dev.tools.get_equity_curve]
approval_mode = "approve"

[mcp_servers.trader-dev.tools.get_trades]
approval_mode = "approve"

[mcp_servers.trader-dev.tools.parse_strategy_inputs]
approval_mode = "approve"

[mcp_servers.trader-dev.tools.search_strategies]
approval_mode = "approve"

[mcp_servers.trader-dev.tools.compare_backtests]
approval_mode = "approve"
```

Leave create/update/fork/deploy/order/exchange/alert/optimization tools unapproved. `codex exec` with an effective `approval: never` otherwise reports `user cancelled MCP tool call` even for reads; per-tool approval is the narrow fix.

Trader.dev application authentication is separate from MCP transport discovery. The durable flow is:

1. Call `login` to obtain the provider's API-key URL.
2. Have the user authenticate in the browser.
3. Never ask for the displayed `pk_…` key in a shared chat.
4. Transfer/store it through a local secret path with mode `0600` or an approved secret store.
5. Call `authenticate` without logging the key, then perform all strategy reads in the same authenticated MCP lifecycle unless persistence has been verified.

If authentication is unavailable, preserve the exact blocker and fall back only to public KPI endpoints. Do not represent public cards as source/config evidence, and do not infer repainting or execution assumptions without code and the trade ledger.

## 9. Standard conclusion format

Return separate verdicts:

- **Engineering feasibility:** high/medium/low
- **Evidence of profitability:** established/weak/none
- **Target-account compatibility:** acceptable/needs re-scaling/incompatible
- **Best architecture:** direct strategy, advisory copilot, or separate broker service
- **Missing artifacts:** exact code, parameters, data, ledger, credentials, or broker access

Never translate a creator's backtest screenshot into a promise of future profitability.