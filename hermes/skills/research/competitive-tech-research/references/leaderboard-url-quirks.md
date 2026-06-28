# Leaderboard URL & Schema Quirks

Last verified: June 2026. These are the small details that make or break a scrape.

## Artificial Analysis (artificialanalysis.ai)

- **URL filter params work**: `?weights=open`, `?price=free`, `?reasoning=reasoning`, `?size=large`. Click the filter button or hit the URL directly.
- **Render**: Next.js SPA. Use Shape 2 (browser_console).
- **Table extraction pattern**:
  ```js
  Array.from(document.querySelectorAll('table tr')).slice(1, 260).map(tr =>
    Array.from(tr.querySelectorAll('td')).map(td =>
      td.innerText.trim().replace(/\s+/g,' ')
    )
  ).filter(r => r.length >= 5)
  ```
- **Column order**: `[Model, Context, Creator, AA Intelligence Index, $/1M, tok/s, latency, total response, Further Analysis]`.
- **"*" suffix**: `45*` means a newer version not yet in the full benchmark suite. Use the non-star number if you need a stable comparison.
- **Paid auth gate**: `/api/v2/data/llms/models` returns 401. Use the SPA scrape instead.

## LMSYS / LMArena (lmarena.ai)

- **JSON endpoint blocked**: `/api/leaderboard/data` returns 403. Use Shape 2.
- **No URL filters**. Filter after extraction (by creator / size).
- **ELO scores fluctuate** — cite with the date you fetched.

## Vellum (vellum.ai/llm-leaderboard)

- **No JSON endpoint**. SPA, iframe-rendered.
- **Tables are well-structured** — extract the `<tbody>` directly via `document.querySelectorAll('tbody tr')`.

## OpenRouter (openrouter.ai)

- **List endpoint**: `https://openrouter.ai/api/v1/models` — 339 models, JSON. Schema: `data[].id`, `pricing.prompt`, `pricing.completion`, `context_length`, `architecture.input_modalities`.
- **Per-model detail**: `https://openrouter.ai/api/v1/models/{id}/endpoints`. Schema: `data.endpoints[]` — each has `provider_name`, `quantization`, `pricing`, `uptime_last_30m`.
- **`:free` suffix endpoint trap**: `/api/v1/models/meta-llama/llama-3.3-70b-instruct:free/endpoints` does NOT return the free endpoint — it returns the endpoints of the base model `meta-llama/llama-3.3-70b-instruct`. The `:free` is a router-level price override applied at request time; the endpoint introspection API doesn't reflect it. To confirm a model has a free tier, check the listing for an `id` ending in `:free` — don't trust the per-endpoint pricing JSON.
- **Free filter**: `pricing.prompt == "0"` AND `pricing.completion == "0"`. Don't forget to also check `pricing.image` and `pricing.request` — some "free" models charge for vision input.
- **`:free` suffix**: free-tier aliases share the base model's endpoints. The free endpoint exists but the API endpoint data doesn't show `:free` specifically — the `:free` is a router-level price override.

## HuggingFace

- **Hub API**: `https://huggingface.co/api/models?search={query}&sort=downloads&direction=-1&limit=50`.
- **Model card**: `https://huggingface.co/{org}/{repo}/raw/main/README.md` — markdown with embedded benchmark tables. Look for `|`-prefixed lines containing MMLU/GPQA/AIME.
- **License**: `https://huggingface.co/{org}/{repo}/raw/main/LICENSE` — first 200 bytes usually identify it. Apache 2.0 starts with "                                 Apache License", MIT starts with "MIT License", Llama community license has "LLAMA" in the first KB.
- **Gated models**: Llama 4 returns 401 from the README URL when not logged in. Use `?gated=true` filter on the search to find these and warn the user.

## Aider polyglot

- **Raw data**: `https://raw.githubusercontent.com/Aider-AI/aider/main/aider/website/_data/polyglot_leaderboard.yml` — YAML, one entry per benchmark run.
- **Schema**: `model`, `date`, `pass_rate_1`, `pass_rate_2`, `total_cost`, `seconds_per_case`, `command` (the exact `aider --model ...` invocation), `edit_format`.
- **Dedupe**: many models have multiple runs (different `edit_format`, different dates). Keep the **latest date** per model. If a model has runs in both `whole` and `diff` formats, take the higher score.
- **Date parsing gotcha**: YAML's `2025-02-25` parses as year-only in some loaders (becomes `2025`). When in doubt, use the string directly.
- **Test count**: 225 cases per run, EXCEPT for some `whole` format runs that use 133. Filter by `total_tests == 225` for fair comparison.

## Ollama (ollama.com)

- **`/api/tags`**: only the featured/curated list, ~30-40 models. For the full library, use `ollama.com/library` HTML (Shape 2). For the cloud-hosted subset, use `ollama.com/search?c=cloud` HTML (Shape 2).
- **`/search` capability filters** — all return HTML, all use Shape 2 (browser_console scrape):
  - `?c=cloud` — models Ollama serves on its cloud (free + Pro $20/mo + Max $100/mo). Includes frontier proprietary models (GLM-5.2 max, MiniMax-M3, Kimi-K2.7-Code, Gemini-3-flash-preview) that you cannot `ollama pull` locally.
  - `?c=tools` — only models with native tool-calling support. **Critical filter for picking agent-loop models.** Surfaces `lfm2.5:8b`, `qwen3-coder:30b`, `gpt-oss:20b/120b`, `nemotron-3-ultra`, `glm-5.2`, etc. Much faster than guessing tags.
  - `?c=vision` — multimodal models.
  - `?c=thinking` — chain-of-thought reasoning models.
  - `?c=embedding` — embedding models (separate from chat).
  - These combine (click multiple checkboxes in the browser UI; or scrape multiple URLs and intersect). The fastest way to find "tool-use + thinking + cloud" is to scrape all three and intersect the slug sets.
- **`/library`**: the full local-downloadable library. Each listitem has model slug, tags (`8b`, `70b`, `405b`), `Pulls` count, and `Updated` relative date.
- **Pulls in raw HTML**: each listitem has `X.XM Pulls` text. Extract with `browser_console` or `read_file` on the HTML.
- **Sizes in raw HTML**: tag chips like `8b`, `70b`, `405b`. Extract via `dom.querySelectorAll('li a')` then split on tag chips.
- **Pricing**: `ollama.com/pricing` — three plans: Free ($0), Pro ($20/mo or $200/yr), Max ($100/mo). Free tier runs locally forever; Pro/Max buy cloud quota + access to bigger hosted models.
- **Exact per-tag disk size via the Docker registry v2 OCI manifest** — `ollama.com/api/show/{tag}` returns POST-gated HTML or 404; the registry v2 endpoint is a clean GET and gives exact layer sizes:
  ```bash
  curl -sL https://registry.ollama.ai/v2/library/{name}/manifests/{tag} \
    -H "Accept: application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.v2+json" \
    | python3 -c 'import sys,json; d=json.load(sys.stdin); print(sum(l["size"] for l in d.get("layers",[]))/1e9, "GB")'
  ```
  Use this when the user has tight disk (e.g. <10 GB free) and you need to know if a model will fit. Confirmed working as of June 2026 for: `gpt-oss:20b` (~13.79 GB), `gemma4:26b` (~17.99 GB), `qwen3:8b` (~5.23 GB), `llama3.3:70b` (~42.52 GB), `gpt-oss:120b` (~65.37 GB). Layer sizes include the full safetensors bundle — match what `ollama pull` actually downloads.

## GitHub raw URLs

- **Pattern**: `https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}`.
- **HTTP 200 ≠ file exists**: GitHub returns the 404 page with HTTP 200 for some misspellings. Always check `size_download` in the curl output.
- **Branch detection**: `main` for newer repos, `master` for older. Check the repo's default branch via `https://api.github.com/repos/{owner}/{repo}` first.
- **Private repos**: 404 even for raw URLs. Use the GH API with auth.

## Browser-rendered SPA detection

If `curl -sI URL` returns `HTTP 200` but the body contains `__NEXT_DATA__`, `<script id="app">`, `<div id="root">`, or shell-like content, it's an SPA — switch to Shape 2.

If `curl -sI URL` returns `HTTP 200` but body has `<html><head>...<title>404</title>...`, the endpoint moved — search for the new URL via `web_search` or `https://huggingface.co/api/datasets/{name}` for datasets.

## Reddit (reddit.com) — blocked, don't bother

- `reddit.com/r/{sub}/search.json` returns HTTP 403 even with a custom User-Agent and proper rate limiting.
- `browser_navigate` to a Reddit URL gets redirected to a `?solution=...&js_challenge=1` page with just a "File a ticket" link as the DOM — no actual content.
- For community sentiment on LLM models, use instead: Hacker News (via the `hackernews-frontpage` skill or Algolia API), LMArena text feedback, HF model discussions, OpenRouter rankings (real adoption signal), and the lab's own Discord/Twitter announcements.

## Headless browser limitations on JS-rendered leaderboards

- `browser_navigate` to a SPA does fetch the rendered DOM in the snapshot, but for tables >100 rows you'll get truncated output ("[... 4839 more lines truncated, use browser_snapshot for full content]" or similar).
- The robust pattern is `browser_console` with an IIFE that returns `JSON.stringify(...)` of the rows array — the result is then parseable as JSON in the next turn.
- For Artificial Analysis specifically, click the "Expand columns" button or apply `?weights=open` filter before extracting — the default view has limited columns and includes closed models.
- For clickable filters that don't reflect in the URL, prefer navigating to the filtered URL directly (`?weights=open`, `?c=cloud`) over clicking the button — saves a round-trip.