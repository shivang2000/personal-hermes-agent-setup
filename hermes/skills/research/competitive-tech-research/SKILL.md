---
name: competitive-tech-research
description: "Research the current state of a fast-moving external tech field (LLM models, agent frameworks, MCP servers, GPU hardware, IDE plugins, etc.) by parallel-fetching canonical sources and aggregating into a comparison table the user can act on."
version: 1.0.0
tags: [research, leaderboard, llm, benchmarks, comparison, market-research]
triggers:
  - "what X are available"
  - "compare X vs Y"
  - "which X should I use"
  - "research current X landscape"
  - "find free X"
  - "open-source alternatives to X"
---

# Competitive Tech Research

Research the current state of a fast-moving external tech field and produce a comparison table the user can act on. Examples: "what local LLMs exist that I can run for free," "what MCP servers are available," "what's the cheapest GPU cloud," "which Postgres vector DB has the best recall."

The output must be **defensible**: every row traceable to a specific source fetched today, every benchmark number labeled with which benchmark and which version. No paraphrasing from memory.

## When to use this

Use when the user asks about **which tools/models/products exist in a category** and the landscape is **fast-moving** (LLMs, agents, MCP, GPU, vector DBs, IDE plugins, coding CLIs). Do NOT use for:
- Single product deep-dives (read its docs instead)
- Internal codebase questions (use code search)
- Historical / stable topics (Wikipedia is fine)

## The core technique: parallel fetch + source triage

The single biggest mistake is fetching sources serially. Most public tech leaderboards expose their data via **one of five shapes** — identify the shapes, fetch all in parallel, then aggregate.

### Shape 1 — JSON API (best case)
Examples: OpenRouter `/api/v1/models`, Ollama `/api/tags`, HF `huggingface.co/api/models`.
```bash
curl -sL https://openrouter.ai/api/v1/models --max-time 25 -o /tmp/source.json
```
These return JSON you can `json.load()` directly. Fastest path.

### Shape 2 — JS-rendered SPA, scrape via `browser_console`
Examples: Artificial Analysis (`artificialanalysis.ai`), LMSYS Arena (`lmarena.ai`), Vellum (`vellum.ai/llm-leaderboard`), most modern leaderboards. The HTML is a shell — the table renders client-side. Don't waste time on `curl`; you'll get an empty `<div id="__next">`.

Pattern:
1. `browser_navigate` to the URL (optionally with query params to filter, e.g. `?weights=open`)
2. `browser_console` with an IIFE that extracts the table:
```js
JSON.stringify(Array.from(document.querySelectorAll('table tr')).slice(1, 250).map(tr => {
  const cells = Array.from(tr.querySelectorAll('td')).map(td => td.innerText.trim().replace(/\s+/g,' '));
  return cells;
}).filter(r => r.length >= 5))
```
3. Parse the returned JSON in Python via `json.loads()`. Each row is an array of cells, which you can column-map if you grabbed the headers separately.

**Filtering trick**: many leaderboards support URL query params for filters (Artificial Analysis uses `?weights=open`, `?price=free`, `?reasoning=reasoning`). Check the page for filter buttons before clicking them — saves a round-trip.

### Shape 3 — Raw YAML/CSV in the leaderboard's GitHub repo
Examples: Aider (`aider-chat/aider` repo → `aider/website/_data/polyglot_leaderboard.yml`), HF Open LLM Leaderboard (`HuggingFaceH4/open_llm_leaderboard` → `results.csv`).

Always check if the website has a GitHub repo. The repo almost always contains the raw data file the site reads from. Pull directly:
```bash
curl -sL https://raw.githubusercontent.com/Aider-AI/aider/main/aider/website/_data/polyglot_leaderboard.yml -o /tmp/aider.yml
```
Then parse with `yaml.safe_load()`. Use this for the gold-standard benchmark numbers (e.g. Aider polyglot = real engineering, not synthetic MMLU).

### Shape 4 — HuggingFace model card (per-benchmark tables)
Labs publish their own benchmark numbers in `README.md`. Pull directly:
```bash
curl -sL https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507/raw/main/README.md -o /tmp/qwen3.md
```
Then grep for `| Benchmark |` lines or a markdown table that mentions MMLU/GPQA/AIME/etc.

**Useful artifact**: also pull the LICENSE file from the same path — saves a trip:
```bash
curl -sL https://huggingface.co/{ORG}/{REPO}/raw/main/LICENSE -o /tmp/license.txt
head -3 /tmp/license.txt   # Apache 2.0 / MIT / proprietary
```

### Shape 5 — Provider-specific API with model-endpoint detail
Examples: OpenRouter `/api/v1/models/{id}/endpoints`, HuggingFace `huggingface.co/api/models/{repo}`.

Use when you need to know which providers serve a model, what the uptime is, what quantization it runs at, the real context window.

## Workflow (11 steps, designed for parallelism)

1. **Audit the user's actual environment first** — before theorising about "which model should you use," inspect their machine and codebase:
   - **Hardware**: `system_profiler SPHardwareDataType` (macOS), `lscpu` + `free -h` (Linux), `nvidia-smi` (Linux GPU).
   - **Disk free** (NOT just RAM — a user with 18 GB RAM but 10 GB free disk cannot add local models after even one is installed): `df -h /System/Volumes/Data` (macOS) or `df -h /` (Linux).
   - **Local LLM runtimes already installed**: `which ollama; ollama list` (with `du -sh ~/.ollama` for blob store size), `which llama.cpp; ls ~/.cache/llama.cpp`, `which lm studio`, `mlx --version`.
   - **What model they're currently using for inference** — likely stated in the prompt or visible in their active project files.
   - **Subscriptions they already have** that include LLM access (Claude Pro/Max via termbridge? ChatGPT Plus? Ollama Pro/Cloud? GitHub Copilot? Cursor? Cursor Pro?).
   - **Hermes config if they use Hermes** — read `~/.hermes/config.yaml`. If `base_url: http://localhost:11434/v1` with `model: {something}:cloud`, they're already on Ollama Cloud; subscribing to Ollama Pro and changing the default model name is the cheapest possible swap.
   - **What their projects actually call** — `grep -r "openai\|anthropic\|gemini\|ollama\|chat.completions\|messages.create" --include="*.py" --include="*.ts" --include="*.go"` in their dev directory. The answer determines the workload shape.
   *Why this matters*: A "best LLM for coding" recommendation that ignores the user already having `ornith:latest` (Qwen3.5 9B) installed and 18GB unified RAM but only 9.9 GB free disk is theoretical nonsense. Audit both RAM and disk first, then the recommendation lands.
2. **Identify the canonical sources** for the category. Use `web_search` if unsure; otherwise recall from `references/sources-by-domain.md` (see below).
3. **Batch-fetch all sources in parallel** in a single tool block — curl endpoints, browser_navigate to leaderboards, github raw URLs. Don't wait for one to finish before starting the next.
4. **Tri-age failures immediately**. If `curl` returns HTML when you expected JSON, that's a SPA — switch to Shape 2. If `browser_navigate` returns a "404 - Hugging Face" page, the endpoint moved — search for the new URL. If `curl` returns HTTP 200 with a body containing `js_challenge` or `_NEXT_DATA__`, it's a JS-challenge wall — switch to browser_navigate. Do NOT retry the same shape 3 times.
5. **Inspect each source's actual schema**. Print the first 1-2 entries to see what fields exist. Benchmark scores may be in a `benchmarks` object, an `intelligence_index` column, a YAML key called `pass_rate_2`, etc.
6. **Build the unified comparison schema**: pick columns that appear across most sources (name, creator, license, price, primary benchmark, size/context, modality). Drop columns that only one source has.
7. **De-dupe models**: many leaderboards list the same model under different names (Qwen3-235B-A22B vs Qwen3-235B-A22B-Instruct-2507). Normalize by stripping suffixes.
8. **Sort and filter by user intent**. They asked "which is best for X" — X is usually cost, capability, local-runnable, or free-tier-availability. Filter the table before showing it.
9. **Cross-verify the top picks**. If AA says model X has intelligence 44 and OpenRouter says model X is $0.18/M, cite both. If HF model card says 86.6 MMLU-Pro and Aider says 59.6 polyglot, those are different benchmarks — show both.
10. **Include the negative space**: which big names are MISSING from the leaderboard? Often that signals a licensing/cost change. Also: which models appear under "open weights" but are actually proprietary hosted models with no public weight download? Cross-check license on the HF model card.
11. **Deliver a tiered decision tree mapped to the audited environment**. End with "if you have X hardware / Y use case / Z budget, route to W" — and explicitly say what's local-first, what's cloud-only, and what should be skipped. Use the tiered pattern in `references/model-fit-decision-tree.md` for the shape.

## Output shape (always)

A markdown reply with these sections:
- **TL;DR table** — 3-5 rows of the user's actual options for the most likely use case
- **Full comparison table** — sorted by the primary benchmark, with explicit columns: model, creator, license, primary benchmark score, $/1M, context, hardware req
- **Per-benchmark detail table** — the gold-standard benchmark numbers from the lab's own model card
- **Source list** — every URL you fetched, with a one-line note on what you got from it
- **Decision tree** — "if X then use Y; if Z then use W"
- **Caveats** — anything you couldn't verify, stale-by date, etc.

## Pitfalls (encode as warnings)

- **Don't paraphrase benchmarks from memory.** Always cite the specific source. Numbers shift 10-30 points between model versions and leaderboard versions.
- **Watch for "open-weights" vs "free hosted" confusion.** Many leaderboards include proprietary models under "free" or under "open" because they have hosted free tiers. Cross-check license in the HF model card.
- **"Looks open-weights on the leaderboard, isn't" trap.** Artificial Analysis's `?weights=open` filter surfaces some proprietary hosted models alongside truly open models (observed: MiniMax M3 appears at AA Index 44 under that filter despite being proprietary). The criterion AA uses is loose. Always confirm by checking the HF model card for a weight download or by grepping the README for a license + weights-availability statement.
- **"Highest AA Intelligence Index isn't the right pick for tool-use workloads."** For personal-assistant / Hermes / iMessage / cron-agent workloads, the right model is the one explicitly marketed for **tool-call reliability on consumer hardware** (e.g. `lfm2.5:8b` — Ollama describes it as "an edge model built for fast, reliable tool calling on consumer hardware"). Higher AA-Index models like `gpt-oss:120b` or `glm-5.2` are better at reasoning but bigger and slower for tool loops. Always filter by capability first (`ollama.com/search?c=tools`), then pick the smallest that meets the capability bar — speed and reliability beat peak benchmark score for always-on agents.
- **Ollama search capability filters.** `ollama.com/search?c=tools`, `?c=vision`, `?c=thinking`, `?c=embedding`, `?c=cloud` — each returns only models tagged with that capability. Use these to build capability-driven shortlists in seconds: `?c=tools` for agent candidates, `?c=cloud` for Pro-tier candidates, `?c=vision` for multimodal, `?c=thinking` for reasoning-tuned. Combine (click multiple checkboxes in the browser, or scrape multiple URLs) for "tool-use + thinking" or "cloud + tools".
- **Get exact download sizes from the Ollama registry v2 OCI manifest.** `https://ollama.com/api/show/{tag}` returns POST-only HTML or 404s. The reliable path is the Docker registry v2 API: `curl -sL https://registry.ollama.ai/v2/library/{name}/manifests/{tag}` with Accept headers for OCI/distribution manifests. Sum the layer sizes to get the actual disk footprint. This is essential when the user has <10 GB free and you need to know if a 19.87 GB model is going to fit. Example:
  ```bash
  curl -sL https://registry.ollama.ai/v2/library/gpt-oss/manifests/20b \
    -H "Accept: application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.v2+json" \
    | python3 -c 'import sys,json; print(sum(l["size"] for l in json.load(sys.stdin).get("layers",[]))/1e9, "GB")'
  ```
- **Skip Reddit for research.** `reddit.com/r/{sub}/search.json` returns HTTP 403 to bots, and `browser_navigate` to Reddit hits a JS challenge wall ("File a ticket" stub page). Use Hacker News (`hackernews-frontpage` skill or Algolia API), OpenRouter rankings (real adoption signal), LMArena text feedback, and HF model discussions instead.
- **Date your output.** "As of June 2026" belongs in the headline. Aider polyglot data is dated in the YAML `date:` field — show the date, not the model.
- **Quantization lies.** A 120B model at 4-bit fits in 60GB; at fp8 needs 120GB; at bf16 needs 240GB. Always state the quantization you're citing. Model cards vary.
- **"Pass rate" vs "Pass@1" vs "Pass@2"** all mean different things in different benchmarks. Aider polyglot uses `pass_rate_2` (two attempts). Other benchmarks use pass@1.
- **YAML dates parse as year-only** sometimes (e.g. `<2025-02-25` becomes `<12` in some loaders). Don't trust the rendered year — check the raw `date:` field.
- **RAM budgeting on Apple Silicon is not "RAM = VRAM".** M-series chips use unified memory — the OS, apps, browser tabs, and the LLM all share it. A user with "18 GB MacBook Pro" has ~12-15 GB available for the LLM after macOS overhead. Don't recommend a 70B bf16 model on that hardware without a `ollama pull` size check.
- **Disk is the silent killer, not just RAM.** The audit must check **both** `df -h /System/Volumes/Data` and `sysctl hw.memsize`. A user with 18 GB RAM but only 9.9 GB free disk cannot pull any new local model after they've installed even one 5-6 GB model (the Ollama blob store is in `~/.ollama`). The conversation that led to this pitfall: Shivang had 18 GB RAM, only 9.9 GB free disk, `ornith:latest` (5.6 GB) already installed, and the first recommendation (gpt-oss:20b + qwen3-coder + gemma4 local stack) was immediately rejected with "we dont have storage and ram for it". The skill audit step was RAM-only; the user had to push back to make the constraint visible. **Fix: check both, and also sum the Ollama blob directory size** (`du -sh ~/.ollama`) to know the real remaining budget.
- **Tier 0 (cloud-only) when local is impossible.** The standard three-tier framework assumes local is always an option. When the audit reveals "not enough disk + RAM for any new model," the framework collapses to **Tier 1 (cheap/fast cloud for high-volume work) + Tier 2 (frontier cloud for hard work)**, both cloud, no local. The Tier 1 choice typically becomes Groq free tier (500K tok/day free on Llama 3.1 8B Instant, 840 tok/s — beats Ollama cloud on speed) or OpenRouter `:free` aliases. The Tier 2 choice typically becomes Ollama Pro $20/mo (gives access to GLM-5.2 + qwen3-coder-480b-cloud + kimi-k2.7-code on a unified quota) or DeepSeek V3.1 API at $0.18/M. Add this as an explicit branch of the decision tree, not an afterthought.
- **Hermes already pointing at `localhost:11434` = Ollama Cloud swap is a one-liner.** If the user runs Hermes and their `~/.hermes/config.yaml` shows `base_url: http://localhost:11434/v1` with `model: {something}:cloud`, they're already using Ollama Cloud as a free hosted endpoint. Subscribing to Ollama Pro $20/mo and changing `default: minimax-m3:cloud` → `default: glm-5.2` (or whatever frontier model they want) **is literally the entire setup** — no code changes anywhere in their repos, no API key migration, no breaking changes to agent tools. This is the cheapest possible upgrade path for any Hermes user. Detect this in step 1 of the audit by reading `~/.hermes/config.yaml` and looking at the `model:` and `base_url:` fields.
- **Per-project routing beats single-model-for-all-projects.** When the user has many repos with different workload shapes (one for cron agents, one for long-context coding, one for phone-agent, one for trading), a single default model is the wrong answer. Show them a routing table: `~/dev/project-A → Groq llama-3.1-8b-instant`, `~/dev/project-B → Ollama Pro glm-5.2`, `~/dev/project-C → Ollama Pro qwen3-coder:480b-cloud`, etc. Their existing code in each repo just changes one config value (base URL + model name). The trade-off they actually face isn't "which single model is best" — it's "which model is right for this workload, and which subscription covers it."

## Companion files

- `references/sources-by-domain.md` — known-good URLs for LLM/agent/MCP/etc. research. Update when you find new sources or a URL rots.
- `references/leaderboard-url-quirks.md` — which leaderboards need Shape 2 (browser_console), which have Shape 1 (JSON), which have a GitHub raw source. Includes schema field names and gotchas (e.g. Aider YAML date parsing, OpenRouter free-filter logic).
- `references/model-fit-decision-tree.md` — the tier-1-local / tier-2-cloud / tier-3-skip pattern for converting a comparison table into an actionable routing recommendation. Use the tiered shape, not a single-model-wins recommendation.
- `references/tier0-cloud-only.md` — the Tier 0 branch for when local inference is impossible (insufficient disk/RAM, explicit user opt-out). Includes the Hermes `~/.hermes/config.yaml` one-line swap trick for Ollama Cloud → Ollama Pro, the per-project routing table format, and the Groq + Ollama Pro + DeepSeek stack as the default $20/mo setup.
- `references/hermes-model-routing.md` — source-first audit checklist for Hermes model routing, fallbacks, auxiliary/delegation/cron overrides, provider-ID quirks, and credential pools. Use it to separate supported routing behavior from terminology that merely implies semantic task escalation.