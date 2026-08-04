# Indicator Strategy Porting and Activation Gates

Use this reference when implementing an indicator strategy discovered through a video, public backtest report, strategy marketplace, or paid Pine source.

## Core rule: provenance determines the claim

Keep these artifacts distinct:

1. **Public performance report** — metrics and trades, but not necessarily formulas.
2. **Public video walkthrough** — may disclose indicator names and settings, but can show a different revision than the report.
3. **Authenticated strategy metadata** — may still omit source or require a paid plan.
4. **Audited source** — the only reliable basis for claiming an exact port.

Never call a reconstruction an exact version when its source is unavailable. Name it `candidate`, record the evidence used, and keep funded execution disabled until reproduction clears.

A public report and a video are not automatically the same strategy revision. Compare directionality, trade count, date range, position sizing, stops, and targets before combining their evidence. A video that says “long-only” does not prove that a report containing long and short records uses the same exit/accounting model.

## Evidence recovery ladder

1. Inspect the public report and API response for strategy/backtest IDs, dates, trades, costs, initial capital, direction split, source visibility, and fork/auth requirements.
2. Read the transcript around strategy explanation and settings.
3. If the transcript lacks numbers, download only the relevant video section with `yt-dlp --download-sections`.
4. Extract one frame per second and make contact sheets with `ffmpeg`; identify frames showing input panels.
5. Inspect the clearest individual frames and transcribe only readable labels, values, dropdowns, and checkbox states.
6. Record whether each value came from video, public report, authenticated metadata, or audited source.

If a segmented adaptive-stream download returns a transient CDN 403, retry with a web player client and a progressive MP4 format, then cut locally. Capture the successful retry pattern, not a durable claim that YouTube downloads are broken.

## Candidate implementation boundary

A safe candidate has four separate layers:

```text
Pure causal indicators
    -> completed-candle signal logic
    -> typed config and provenance gate
    -> existing RiskManager / PropFirmGuard / executor
```

Requirements:

- No look-ahead, repainting, future bar, or current-forming-candle access.
- Pure indicator functions are independently testable.
- Same-bar scans are deduplicated.
- Stop and target geometry is deterministic and included in the emitted signal.
- Strategy source/name contains `candidate` until reproduction is complete.
- The strategy uses the existing execution and risk stack rather than bypassing it.

## Fail-closed activation gate

Keep research parameters in config, but make activation impossible while unverified:

```yaml
strategies:
  discovered_strategy:
    enabled: false
    parameters_verified: false
    provenance: video-derived
```

Use schema validation so this state fails startup:

```yaml
enabled: true
parameters_verified: false
```

Instantiation and registry wiring should also require both flags. The funded overlay may contain candidate parameters for reproducibility while execution remains disabled.

## TDD sequence

1. **Config contract RED** — test account size, firm rules, operational limits, one-position isolation, phase target, minimum days, and activation state.
2. **Sizer RED** — calculated volume below broker minimum must raise a typed rejection instead of clamping upward.
3. **Indicator RED** — constant-series invariants and required output columns.
4. **Signal RED** — fresh confluence flip, completed-candle handling, stop/target geometry, and same-bar deduplication.
5. **Registry RED** — disabled/unverified strategy is absent; enabled+verified strategy is instantiated.
6. Implement the smallest causal production slice to turn each test green.
7. Run targeted tests, compile, changed-file lint, resolved-config inspection, then the full suite.

When fail-closed sizing breaks an unrelated stacking/order test, do not weaken production behavior. Fix the synthetic fixture so its account/risk/stop geometry computes a representable broker volume. Keep a separate test proving sub-minimum volume is rejected.

## Funding overlay pattern

Use a dedicated overlay instead of repurposing a generic account file. It should:

- preserve other account overlays;
- isolate one symbol and one candidate strategy;
- disable unrelated strategies and non-deterministic signal sources;
- cap open positions, per-symbol positions, per-direction positions, and daily trades;
- set operational stops tighter than firm hard limits;
- record the current phase target and minimum trading days;
- keep strategy activation off until validation passes.

Always resolve the merged config and print the effective safety-critical values. Reading YAML alone can miss defaults, inheritance, or a stale overlay environment variable.

## Reproduction gate

Before changing `parameters_verified` to true:

1. Match the reported period and instrument/timeframe.
2. Reproduce trade count and direction semantics within an explicitly documented tolerance.
3. Match entry/exit timestamps and prices on a representative sample.
4. Reproduce costs, sizing, return, profit factor, and drawdown.
5. Run realistic broker spread/commission/slippage stress.
6. Run out-of-sample, walk-forward, sensitivity, and Monte Carlo checks.
7. Scale risk so simulated drawdown remains materially inside the bot’s operational stop—not merely inside the prop firm’s breach limit.

If audited source remains unavailable, validate and name the implementation as an independent strategy. Do not use the marketplace version number as its identity.
