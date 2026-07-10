User prefers Twitter/X post review, approval, and automation status messages to go to Discord #tweets-automation rather than unrelated Discord threads.
§
Shivang prefers X/Twitter automation drafts to be more technical: concrete engineering details, backend/infra/reliability mechanisms, and implementation lessons over broad automation-UX, generic founder/productivity, or high-level human-in-the-loop takes.
§
User expects Hermes to avoid bot-to-bot acknowledgement loops in Discord; when another bot says to stop/no further acknowledgements/silence, Hermes should stop replying rather than acknowledge the stop request.
§
Shivang wants X/Twitter automation optimized toward AI-related technical posts: concrete AI agents, LLM infrastructure, evals/observability/reliability, backend mechanisms, and lessons from building AI-enabled products rather than generic productivity content.
§
Shivang wants X/Twitter drafts to emphasize how he uses AI as engineering leverage to build/work dramatically faster and become a dramatically better engineer, with mechanisms like agent workflows, debugging, evals, code review, testing, refactors, observability, and production reliability.
§
Shivang wants the Discord #tech-news channel/thread used for high-signal tech/AI news, YC/Hacker News items, notable new repositories, relevant YouTube tech/AI videos, and important industry/strike updates, with emphasis on EU/US-active hours and concrete AI/infra/startup developments.
§
Shivang approved making the X/Twitter strategy center on AI engineering lessons from his real building work, combined with current tech/AI news and proof-of-work posts aimed at recruiters/founders.
§
Shivang wants the AI/tech X/Twitter automation to auto-post strong approved-by-strategy posts instead of requiring a manual approval queue, while keeping the content aligned to AI engineering lessons, real building work, and recruiter/founder proof-of-work.
§
Shivang dislikes X/Twitter draft angles based on tiny UI/form bugs, redaction placeholders/sentinels, generic data-cleanliness issues, or narrow one-off frontend edge cases unless they reveal a broadly useful technical mechanism.
§
Shivang wants his AI/tech X/Twitter automation to run in fully auto-post mode, without asking for manual approval, and to apply the humanizer skill/checklist before every tweet or reply is posted.
§
Shivang wants future X/Twitter automation optimized toward source-backed technical takeaways that attach to active AI/agent/LLM infra conversations, include concrete mechanisms/tradeoffs, and use his learning-in-public builder voice rather than generic AI commentary.
§
Shivang wants X/Twitter automation posts to use 1-2 highly relevant hashtags for discoverability when they match the topic/search intent (e.g. #AIAgents, #LLM, #AIInfra, #DevTools, #OpenSource, #SoftwareEngineering), while avoiding generic tag-stuffing; source-backed @mentions are also okay when genuinely useful.
§
User prefers direct technical answers with architecture diagrams and config examples over high-level explanations. When asking "is X possible", they want the actual config/commands, not just "yes".
§
For AI/LLM recommendations and Hermes routing, Shivang prefers a three-tier stack: (1) lightweight/high-volume work on MiniMax M3 via pooled Ollama Cloud API keys; (2) intensive multi-step work on GLM 5.2; (3) extreme/high-stakes work escalated to Claude and Codex. Preserve cost-aware routing rather than using one model for everything.
§
When a job portal or web target is blocked by bot-mitigation (DataDome, Cloudflare, etc.) and the default browser tool fails, Shivang wants the agent to escalate to Playwright (real Chrome, persistent context, ideally CDP-attached to his running Chrome for Testing) before declaring the target unreachable. He will explicitly say "use playwright to do it" — that means "try harder, don't give up at the first wall." The escalation ladder, ethical lines, and "log blocked, never fabricate" pattern live in the `bot-blocked-web-fetch` Hermes skill.
§
Shivang prefers using the Pandoc CLI to generate PDFs from Markdown when available.
§
Shivang prefers browser tasks requiring authentication to use a hybrid logged-in session strategy: real Chrome/Arc via background computer-use first, with safe CDP-attached Playwright fallback.