"""AI-usage detection vocabulary and commit-scanning helpers.

Two distinct phenomena are kept separate (see collectors/ai_usage.py):

* **dev** — an LLM coding tool helped *write/maintain* the code (Claude Code,
  GitHub Copilot, Cursor, Aider, Devin, Jules, …). Evidence: agent config
  files, commit co-author trailers, agent-bot commits/PRs, CI agents, review
  bots.
* **product** — the project *ships* LLM/GenAI functionality. Evidence: LLM SDK
  dependencies (openai, anthropic, langchain, …) and GenAI topics.

The DEFAULT_* dicts below are the authoritative vocabulary; config.yaml may
override them under ``detection.ai_dev_keywords`` / ``detection.product_llm_keywords``.
"""

from __future__ import annotations

# --- Group 3: LLM used in development (AI-assisted) -------------------------
DEFAULT_AI_DEV_KEYWORDS: dict = {
    # Exact root-file name -> tool label.
    "config_files": {
        "CLAUDE.md": "claude_code",
        "AGENTS.md": "agents_md",
        ".cursorrules": "cursor",
        ".windsurfrules": "windsurf",
        ".aider.conf.yml": "aider",
        "GEMINI.md": "gemini_cli",
        ".clinerules": "cline",
        ".roomodes": "roo",
        ".mcp.json": "mcp",
        "soul.md": "soul_md",
        "SOUL.md": "soul_md",
    },
    # Exact nested path -> tool label (checked via file_exists).
    "config_paths": {
        ".github/copilot-instructions.md": "github_copilot",
        ".cursor/mcp.json": "cursor",
    },
    # Directory path -> tool label (checked via directory listing).
    "config_dirs": {
        ".claude": "claude_code",
        ".cursor/rules": "cursor",
        ".github/prompts": "github_copilot",
        ".github/chatmodes": "github_copilot",
        ".continue": "continue",
        ".roo": "roo",
        ".junie": "junie",
    },
    # Substring found inside a commit co-author / "generated with" trailer line.
    # (Restricted to trailer-shaped lines, so generic words like "hermes" are
    # low-risk here — they only match inside Co-authored-by:/generated-with.)
    "trailer_tools": {
        "claude": "claude_code",
        "copilot": "github_copilot",
        "cursor": "cursor",
        "devin": "devin",
        "codex": "openai_codex",
        "aider": "aider",
        "jules": "jules",
        "clawcode": "clawcode",
        "openhuman": "openhuman",
        # "hermes agent" (not bare "hermes" — too generic; matched a human
        # co-author named Hermes and produced false positives).
        "hermes agent": "hermes_agent",
    },
    # Commit/PR author login -> tool label (matched case-insensitively).
    "agent_bot_logins": {
        "copilot-swe-agent[bot]": "github_copilot",
        "copilot[bot]": "github_copilot",
        "devin-ai-integration[bot]": "devin",
        "cursoragent": "cursor",
        "cursor[bot]": "cursor",
        "google-labs-jules[bot]": "jules",
        "jules[bot]": "jules",
        "sweep-ai[bot]": "sweep",
        "claude[bot]": "claude_code",
        "claude-bot": "claude_code",
    },
    # Commit author email substring -> tool label.
    "agent_bot_emails": {
        "noreply@anthropic.com": "claude_code",
    },
    # PR review/comment bot login -> tool label.
    "review_bot_logins": {
        "coderabbitai[bot]": "coderabbit",
        "sourcery-ai[bot]": "sourcery",
        "sweep-ai[bot]": "sweep",
        "github-advanced-security[bot]": "github_security",
        "copilot-pull-request-reviewer[bot]": "github_copilot",
    },
    # Substring inside a .github/workflows/* file -> tool label.
    "workflow_refs": {
        "anthropics/claude-code-action": "claude_code",
        "claude-code-action": "claude_code",
        "coderabbit": "coderabbit",
        "github/copilot": "github_copilot",
        "cursor": "cursor",
        "sweep": "sweep",
        "aider": "aider",
    },
    # Dependency name substring -> tool label (AI dev tools shipped as deps).
    "dependencies": {
        "aider-chat": "aider",
        "claude-code": "claude_code",
        "@anthropic-ai/claude-code": "claude_code",
        "@openai/codex": "openai_codex",
    },
}

# --- Group 2: LLM as a delivered product artifact --------------------------
DEFAULT_PRODUCT_LLM_KEYWORDS: dict = {
    # Dependency name substring -> provider label.
    "dependencies": {
        "openai": "openai",
        "anthropic": "anthropic",
        "@anthropic-ai/sdk": "anthropic",
        "google-generativeai": "google",
        "google-genai": "google",
        "@google/generative-ai": "google",
        "cohere": "cohere",
        "mistralai": "mistral",
        "litellm": "multi_provider",
        "langchain": "langchain",
        "langgraph": "langchain",
        "llama-index": "llamaindex",
        "llama_index": "llamaindex",
        "llamaindex": "llamaindex",
        "ollama": "ollama",
        "groq": "groq",
        "replicate": "replicate",
        "guidance": "guidance",
        "instructor": "instructor",
        "semantic-kernel": "semantic_kernel",
        "haystack-ai": "haystack",
        "vllm": "vllm",
        # Aggregators / alternative API providers
        "openrouter": "openrouter",
        # Chinese model providers (often via dedicated or OpenAI-compatible SDKs)
        "deepseek": "deepseek",
        "dashscope": "qwen",  # Alibaba Qwen
        "qwen": "qwen",
        "moonshot": "moonshot",  # Kimi
        "kimi": "moonshot",
        "zhipuai": "zhipu",  # GLM
        # Local inference runtimes / model servers
        "openllm": "openllm",
        "mlx-lm": "mlx",  # Apple MLX
        "mlx": "mlx",
        "llama-cpp-python": "llama_cpp",
        "ctransformers": "ctransformers",
        # "onnxruntime-genai" is the LLM-specific ONNX runtime. The bare "onnx"
        # package is deliberately NOT matched — it ships with many non-LLM
        # CV/ML projects and would produce false positives.
        "onnxruntime-genai": "onnx_genai",
    },
    # Repository topic -> kept as-is (lowercased) for the signal.
    "topics": [
        "llm",
        "gpt",
        "chatgpt",
        "rag",
        "chatbot",
        "generative-ai",
        "openai",
        "large-language-models",
        # Providers / models
        "openrouter",
        "deepseek",
        "qwen",
        "kimi",
        "moonshot",
        "llama",
        "mistral",
        "gemini",
        # Local inference runtimes
        "ollama",
        "mlx",
        "local-llm",
    ],
}


def match_agent_bot(
    login: str | None, email: str | None, dev_kw: dict
) -> str | None:
    """Return the AI tool label if a commit/PR author is a known AI agent bot."""
    lo = (login or "").lower()
    if lo:
        for needle, tool in dev_kw.get("agent_bot_logins", {}).items():
            n = needle.lower()
            if lo == n or lo == n.replace("[bot]", "") or n in lo:
                return tool
    em = (email or "").lower()
    if em:
        for needle, tool in dev_kw.get("agent_bot_emails", {}).items():
            if needle.lower() in em:
                return tool
    return None


def detect_ai_in_commit(
    message: str | None,
    author_login: str | None,
    author_email: str | None,
    dev_kw: dict,
) -> tuple[set[str], set[str]]:
    """Scan a single commit for AI-assisted-development signals.

    Returns ``(coauthor_tools, author_tools)``:

    * ``coauthor_tools`` — tools named in a co-author / "generated with" trailer
      line of the commit message (e.g. ``Co-authored-by: Claude``).
    * ``author_tools`` — tool whose AI agent bot authored the commit.

    Trailer matching is restricted to trailer-shaped lines to avoid false
    positives from projects that merely *mention* an AI tool in prose.
    """
    coauthor_tools: set[str] = set()
    author_tools: set[str] = set()

    trailer_tools = dev_kw.get("trailer_tools", {})
    for raw_line in (message or "").splitlines():
        line = raw_line.strip().lower()
        if not line:
            continue
        if line.startswith("co-authored-by:") or "generated with" in line or "🤖 generated" in line:
            for needle, tool in trailer_tools.items():
                if needle in line:
                    coauthor_tools.add(tool)

    tool = match_agent_bot(author_login, author_email, dev_kw)
    if tool:
        author_tools.add(tool)

    return coauthor_tools, author_tools
