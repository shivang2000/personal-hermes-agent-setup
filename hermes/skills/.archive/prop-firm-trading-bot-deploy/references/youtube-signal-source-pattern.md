# YouTube Live Signal Source Pattern

## Context

Built 2026-07-24 for trading-bot-v2 (`/Users/shivang/dev/advanced-trading-bot/trading-bot-v2`).
User wanted to extract trade signals from a YouTube live streamer's audio and feed them into
the existing MT5 execution pipeline alongside Telegram channel signals.

## Core architecture: "synthesized message" delegation

The key insight: the existing bot already has a `SignalParser.process_message()` path that
handles Telegram messages → Claude API → structured `Signal` → `SignalEvent` on EventBus →
Risk → MT5. Instead of writing a second Claude parser for YouTube, **synthesize a fake
Telegram message** from the transcript and feed it to the SAME `process_message()`.

```
YouTube Live
  ↓ yt-dlp -g → HLS manifest URL
  ↓ ffmpeg → 16kHz mono s16le PCM (5s chunks)
  ↓ OpenAI Whisper API → text
  ↓ LiveSignalParser (rolling 60s buffer, 30s debounce, hash dedup)
  ↓ Synthesize: "[YouTube Live | StreamName | XAUUSD]\n<transcript>"
  ↓ SignalParser.process_message()  ← SAME path as Telegram
  ↓ Claude → Signal → SignalEvent → RiskManager → MT5
```

This reuses the parser's extraction logic, regex fallback, amendment detection, geometry validation, and EventBus. It is **not** literally zero-change integration: a Telegram-oriented parser often rejects an unknown `yt:*` pseudo-channel through its channel registry and may stamp every emitted signal as `telegram:*`.

The transport must pass an explicit source policy into the shared parser:

```python
await parser.process_message(
    raw_message_id=raw_id,
    channel_id=f"yt:{stream.id}",
    message_text=synthesized,
    image_bytes=None,
    source=f"youtube:{stream.name}",
    allowed_symbols=set(stream.symbols),
    min_confidence=youtube.safety.confidence_floor,
)
```

The parser must use `allowed_symbols` instead of the Telegram registry when supplied, enforce `min_confidence` before publishing, and preserve `source` in the `Signal`. Add an end-to-end regression proving a YouTube pseudo-channel is admitted, correctly attributed, and reaches `SignalEvent`; a mocked `process_message()` call alone does not prove this.

## Files created

```
src/youtube/
├── __init__.py               (18 LOC)
├── stream_config.py          (127 LOC) — YouTubeConfig + YouTubeRegistry (mirrors channel_config.py)
├── stream_capture.py         (196 LOC) — yt-dlp + ffmpeg subprocess, PCM audio chunks
├── transcriber.py            (149 LOC) — OpenAI Whisper API client, PCM→WAV wrapping
├── live_signal_parser.py     (156 LOC) — rolling buffer, debounce, hash dedup → process_message
└── youtube_listener.py       (192 LOC) — orchestrator, per-stream task lifecycle, backoff

config/youtube_signals.yaml   (52 LOC) — stream config + safety floor
tests/test_youtube_signal_source.py (263 LOC) — 9 unit tests
```

Modified: `src/config/schema.py` (+YouTubeConfig), `src/config/loader.py` (+youtube_signals.yaml merge),
`src/main.py` (+YouTubeListener start/stop/boot log), `pyproject.toml` (+yt-dlp dep).

## Stream capture technique

```bash
# yt-dlp gets the live HLS/DASH manifest URL (not the video)
yt-dlp -g --no-warnings -f bestaudio/best "https://youtube.com/@channel/live"

# ffmpeg decodes audio only (no video transcoding — saves CPU)
ffmpeg -loglevel error -i <manifest> \
  -vn -ac 1 -ar 16000 -f s16le pipe:1
```

- Manifest URLs expire (~6h). Re-fetch on any IO error.
- Audio chunk size: `16000 * 1 * 2 * 5 = 160000 bytes` per 5-second chunk.
- YouTube can go offline between sessions. Listener sleeps + polls, does not crash.
- ffmpeg stderr must be drained or it deadlocks.
- Installing the Python `yt-dlp` dependency is insufficient: the production Docker image must also install the system `ffmpeg` binary (and CA certificates). Verify inside the built image with `ffmpeg -version`, `yt-dlp --version`, and an application import probe.

## Whisper API integration

- **Backend: OpenAI Whisper API** (`whisper-1` model, $0.006/min, ~600ms p50 latency)
- **Local Whisper is too slow** on t3.medium EC2 (2 vCPU / 4GB RAM): 8-15s per 5s chunk on CPU
- **Prompt hint**: pass `prompt="XAUUSD gold bitcoin BUY SELL entry stop loss SL TP target"` —
  Whisper uses it as spelling/audio context, materially improves number recognition
- **PCM→WAV**: Whisper API expects a file format, not raw PCM. Wrap in WAV container:
  ```python
  import io, wave
  buf = io.BytesIO()
  with wave.open(buf, "wb") as wf:
      wf.setnchannels(1)
      wf.setsampwidth(2)
      wf.setframerate(16000)
      wf.writeframes(pcm_s16le)
  return buf.getvalue()
  ```
- Retry with exponential backoff on 429/5xx (3 attempts)

## LiveSignalParser debounce/dedup logic

1. **Rolling buffer**: `deque(maxlen=200)` of `TranscribedChunk` objects
2. **Context window**: only consider chunks from last 60s
3. **Min chunks**: skip if <4 chunks in window (too little audio)
4. **Min chars**: skip if merged text <30 chars (too little signal)
5. **Debounce**: don't re-extract within 30s of last attempt
6. **Hash dedup**: MD5 of merged text — skip if identical to last extraction
7. **Synthesize**: `[YouTube Live | {name} | {symbols}]\n{merged_text}`
8. **Delegate with policy**: call `parser.process_message(..., source="youtube:<name>", allowed_symbols=set(stream.symbols), min_confidence=safety.confidence_floor)`.

## Safety floor for non-deterministic signal sources

YouTube signals are **non-deterministic and un-backtestable** end-to-end (you can't replay
the live stream at higher quality than the bot sees in real time). This is materially
different from technical OHLCV strategies (deterministic, walk-forward testable).

The 6 kill switches (all configurable in `youtube_signals.yaml`):

| Switch | Value | Rationale |
|--------|-------|-----------|
| `confidence_floor` | 0.85 | Parser must return ≥ this (vs 0.65 tech, 0.75 Telegram) |
| `confirm_floor` | 0.80 | ClaudeSignalFilter must independently confirm ≥ this |
| `max_lot_per_trade` | 0.01 | Hard cap first 2 weeks regardless of balance |
| `daily_loss_pct` | 1.0 | Auto-pause source at -1% day P&L (vs prop firm's 3-5%) |
| `consecutive_loss_kill` | 5 | Auto-disable source after 5 losses in a row |
| `rolling_loss_pct_kill` | -2.0 | Auto-disable if source P&L < -2% rolling |
| `only_when_technical_flat` | true | No pyramiding with technical signals |
| `max_open_positions_from_source` | 1 | Hard cap concurrent YT-sourced positions |

**Configuration is not enforcement.** Before deploy, search production code for every safety field and prove it is consumed at the actual parser/risk/order choke point. Required enforcement pattern:

- parser floor before `SignalEvent` publication;
- independent confirmation in `RiskManager._on_signal`, fail closed on API errors;
- lot cap after position sizing and before `OrderEvent`;
- flat/source-position/daily-loss checks inside the central risk validator;
- consecutive-loss, rolling-P&L, and daily source-P&L updates from `PositionClosedEvent`;
- persist kill-switch state in the tracking database so a container restart cannot erase a losing streak;
- retain a recognizable `youtube:` marker inside the MT5 order comment so closed positions can be attributed after restart.

A YAML-only safety section must be treated as a deployment blocker.

## "No paper, go funded" override pattern

When the user overrides the validation ladder (no paper trading, straight to funded):

1. **Document the override explicitly** — don't silently comply. State what's different
   about this source vs the previous ones that makes the override riskier.
2. **Tighten the safety floor** — if the user won't validate, the code must be tighter:
   - Lower lot cap (0.01 vs account max)
   - Lower daily loss limit (1% vs prop firm's 3-5%)
   - Higher confidence floor (0.85 vs 0.65)
   - Auto-kill switches (5 consecutive losses, -2% rolling)
3. **Do the one validation you can**: replay a past VOD through the pipeline offline.
   Not paper trading — just signal-source evaluation (precision/recall numbers).
4. **Record in memory**: "User overrode validation for YT source. Safety floor is the
   mitigation." So next session knows why the config is tighter than usual.

## Config file integration

The config loader (`src/config/loader.py`) merges YAML files in order:
```
base.yaml ← channels.yaml ← youtube_signals.yaml ← CONFIG_OVERLAY env var
```

Adding a new YAML file to the loader is a 5-line patch:
```python
youtube_path = config_dir / "youtube_signals.yaml"
if youtube_path.exists():
    youtube_data = _load_yaml(youtube_path)
    if "youtube" in youtube_data:
        base["youtube"] = youtube_data["youtube"]
```

## Testing approach

If pytest fails during bootstrap with `ModuleNotFoundError: No module named 'superclaude.pytest_plugin'`, `-p no:` is too late because the stale entry point loads before argument handling. Temporarily move the stale dist-info directory, run the canonical suite, and restore it with a shell trap:

```bash
set -e
DIST='/Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/superclaude-4.1.9.dist-info'
BACK='/tmp/superclaude-4.1.9.dist-info.test-run'
restore(){ if [ -d "$BACK" ]; then mv "$BACK" "$DIST"; fi; }
trap restore EXIT
if [ -d "$DIST" ]; then mv "$DIST" "$BACK"; fi
python3 -m pytest tests/ -q
```

This preserves real `pytest-asyncio` collection and allows targeted, unit, and full-suite evidence. Inline `asyncio.run()` harnesses are useful for quick diagnosis, but they do not replace the canonical pytest run before deployment.

## Pitfall: "OLD" matching "GOLD"

When testing context-window filtering with old chunks containing "OLD SIGNAL TEXT HERE
BUY GOLD", the assertion `assert "OLD" not in msg_text` fails because "OLD" is a substring
of "GOLD". Use a unique marker like "OLDX" that won't appear in trading vocabulary.

## Channel assessment checklist

Before building a YouTube signal source for any streamer:

1. **Signal density**: how many signals/hour? (watch a 30-min VOD)
2. **Audio clarity**: mumbling kills Whisper accuracy
3. **Chart-text reliance**: does the trader say "BUY 2350" or write it on screen?
4. **Stream cadence**: daily? weekly? monthly? (affects validation feasibility)
5. **Instrument focus**: matches your bot's configured symbols?
6. **Telegram channel overlap**: does the streamer already post signals to Telegram?
   If yes, YouTube is a supplemental path (catches what they say but don't post).

For @TradeLikeMalika: 146k subs, India-based, BTC+Gold focus, streams ~1x every few weeks.
Her Telegram channel was already configured in `channels.yaml`. YouTube is supplemental.