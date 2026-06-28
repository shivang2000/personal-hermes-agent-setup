# Canonical Sources by Domain

Last verified: June 2026. URLs and schemas rot — re-check on every use.

## LLMs / open-weights models

### Leaderboards (use Shape 2 — JS SPA, browser_console scrape)
- **Artificial Analysis** — https://artificialanalysis.ai/leaderboards/models — most comprehensive modern benchmark (MMLU-Pro, GPQA, AIME, BFCL, SWE-Bench, price/speed/latency). Filter via URL: `?weights=open`, `?price=free`, `?reasoning=reasoning`. 220+ models.
- **LMSYS Chatbot Arena** — https://lmarena.ai — human-preference ELO. Best for "which model do users actually prefer."
- **Vellum LLM Leaderboard** — https://www.vellum.ai/llm-leaderboard — clean UX, good per-task tables.
- **OpenRouter rankings** — https://openrouter.ai/rankings — by usage volume, not quality. Useful as adoption signal.

### Free-tier APIs (Shape 1 — JSON)
- **OpenRouter** — `https://openrouter.ai/api/v1/models` — 339 models, 26 are `:free`. Each has `pricing.prompt` and `pricing.completion`. Filter free: `pricing.prompt == "0"`.
- **OpenRouter per-model endpoints** — `https://openrouter.ai/api/v1/models/{id}/endpoints` — quant, provider, uptime, latency.
- **Ollama library** — `https://ollama.com/api/tags` — what's downloadable, file size, quantization tags. (Featured list, not exhaustive — `ollama.com/library` has the full set.)
- **Ollama cloud models** — `https://ollama.com/search?c=cloud` — the subset of models Ollama serves on its cloud (free tier + Pro $20/mo + Max $100/mo). HTML, Shape 2 (browser_console scrape). Crucially includes frontier proprietary models (GLM-5.2 max, MiniMax-M3, Gemini-3-flash-preview) that you cannot pull locally — this is the bridge between "open-weights local" and "use Ollama as your OpenAI-compatible endpoint."
- **Ollama capability filters** (all Shape 2 HTML) — fast capability-driven shortlists:
  - `https://ollama.com/search?c=tools` — only models with native tool-calling. **Use this first when picking an agent-loop model.**
  - `https://ollama.com/search?c=vision` — multimodal models.
  - `https://ollama.com/search?c=thinking` — chain-of-thought reasoning models.
  - `https://ollama.com/search?c=embedding` — embedding models.
- **Ollama registry v2 OCI manifest** — `https://registry.ollama.ai/v2/library/{name}/manifests/{tag}` with Accept headers for `application/vnd.oci.image.manifest.v1+json` + `application/vnd.docker.distribution.manifest.v2+json`. Sum the `layers[].size` fields for exact disk footprint per tag (e.g. `gpt-oss:20b` = 13.79 GB, `qwen3:8b` = 5.23 GB). The `ollama.com/api/show/{tag}` endpoint is POST-gated; the registry is the clean GET path.
- **Ollama pricing** — `https://ollama.com/pricing` — three tiers: Free ($0, light cloud usage, public models), Pro ($20/mo or $200/yr, 50× free cloud usage, "larger more powerful cloud models", 3 concurrent, private model upload), Max ($100/mo, 10 concurrent, 5× Pro usage). Free tier runs Ollama locally forever — Pro/Max are about Ollama-hosted cloud inference.
- **HuggingFace Hub API** — `https://huggingface.co/api/models?search={query}` — every model on the Hub. Use `?filter=open-llm` or sort by `downloads`.

### Per-model benchmark data (Shape 3 — GitHub raw, Shape 4 — HF model card)
- **Aider polyglot (real engineering, 225 cases)** — `https://raw.githubusercontent.com/Aider-AI/aider/main/aider/website/_data/polyglot_leaderboard.yml`. Fields: `model`, `date`, `pass_rate_1`, `pass_rate_2`, `total_cost`, `seconds_per_case`. Gold standard for coding.
- **Aider edit-format** — same path with `edit_leaderboard.yml`. Earlier benchmark, easier tasks.
- **HF model card** — `https://huggingface.co/{org}/{repo}/raw/main/README.md` — labs publish their own benchmark tables.
- **HF LICENSE** — `https://huggingface.co/{org}/{repo}/raw/main/LICENSE` — Apache 2.0 / MIT / proprietary (always check this for commercial use).

### Older / deprecated but still cited
- **HF Open LLM Leaderboard v2** — moved to a Gradio Space, hard to scrape. Most labs still cite it. Use the HF model card numbers instead — they're usually the same set (MMLU, ARC, HellaSwag, TruthfulQA, GSM8K, IFEval).
- **LMSYS older ELO tables** — useful as historical signal only.

## Agent frameworks / SDKs
- **GitHub awesome lists** — `awesome-llm-agents`, `awesome-agent-frameworks`. Search via `gh search repos "llm agent"` and sort by stars.
- **GitHub topic pages** — `https://github.com/topics/llm-agent`, `https://github.com/topics/agent-framework`.
- **LangChain hub** — `https://api.smith.langchain.com` (gated) / LangChain Hub.
- **Pypi downloads** — `https://pypistats.org/packages/{name}` — best adoption metric.

## MCP servers
- **Official MCP servers** — `https://github.com/modelcontextprotocol/servers` — the canonical reference repo.
- **MCP.so** — community registry, has search.
- **Glama MCP** — `https://glama.ai/mcp/servers` — modern registry with per-server metadata.

## GPU cloud / hardware
- **Lambda Labs** — `https://lambdalabs.com/service/gpu-cloud` — public pricing, no auth.
- **RunPod** — `https://www.runpod.io/gpu-instance/pricing`.
- **Vast.ai** — `https://vast.ai/pricing` — market-rate spot prices.
- **Modal** — `https://modal.com/pricing`.
- **Together.ai** — `https://www.together.ai/pricing` — also inference API.
- **Cloud GPU comparison** — `https://gpulist.com` (community).

## Vector databases
- **ANN-Benchmarks** — `https://ann-benchmarks.com` — recall vs QPS, the canonical comparison.
- **GitHub stars + downloads** — proxy for adoption.

## Coding CLIs / IDE plugins
- **GitHub topic pages** — `https://github.com/topics/cli-coding`, `https://github.com/topics/ai-coding`.
- **Aider polyglot** (already cited) — cross-model coding benchmark.
- **SWE-bench leaderboard** — `https://www.swebench.com` — PR-resolution accuracy, gold standard for coding agents.

## Embedding models
- **MTEB leaderboard** — `https://huggingface.co/spaces/mteb/leaderboard` — Massive Text Embedding Benchmark. 100+ models, 50+ tasks.
- **HF model cards** — same Shape 4 pattern.

## Speech-to-text / TTS
- **HF Open ASR Leaderboard** — `https://huggingface.co/spaces/open-asr-leaderboard/leaderboard`.
- **HF TTS Arena** — `https://huggingface.co/spaces/ArtificialAnalysis/text-to-speech-arena`.