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

import re

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
    # Tool name that must open the name in a Co-authored-by: line, or directly
    # follow a "Generated with/by/using" marker. A name match on a co-author
    # line only counts for automated identities (see coauthor_emails below).
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
    # Co-authored-by: e-mail substring -> tool label. A co-author line credits a
    # tool if its e-mail matches one of these, or if the identity is automated
    # (a [bot] address, or no e-mail at all) and its name starts with a
    # trailer_tools name. People who happen to be called Claude, Devin, or
    # Jules have ordinary addresses and are therefore not counted.
    "coauthor_emails": {
        "noreply@anthropic.com": "claude_code",
        "+copilot@users.noreply.github.com": "github_copilot",
        "copilot@github.com": "github_copilot",
        "devin-ai-integration[bot]": "devin",
        "google-labs-jules[bot]": "jules",
        "cursoragent@cursor.com": "cursor",
        "noreply@aider.chat": "aider",
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


def keep_earliest(first_dates: dict, key: str, when) -> None:
    """Store *when* for *key* unless an earlier date is already stored.

    ``None`` means "date unknown": it is stored only for a new key and is
    replaced by the first known date.
    """
    if key not in first_dates:
        first_dates[key] = when
    elif when is not None and (first_dates[key] is None or when < first_dates[key]):
        first_dates[key] = when


# Bullets, quote marks, emoji, and zero-width characters before a marker.
_LEADING_NOISE = re.compile(r"^[^a-z0-9]+")
_COAUTHOR_LINE = re.compile(
    r"^co-authored-by\s*:?\s*(?P<name>[^<]*?)\s*(?:<(?P<email>[^>]*)>?)?\s*$"
)
_GENERATED_MARKER = re.compile(r"\bgenerated (?:with|by|using)\b(?P<rest>.*)")
# Words allowed between the marker and the tool ("Generated by GitHub Copilot").
_VENDOR_WORDS = ("github", "openai", "anthropic", "google", "the")

# dev_kw dict -> (dev_kw, needles, emails); keeps the dict alive so its id
# cannot be reused by another dict while cached.
_VOCAB_CACHE: dict[int, tuple[dict, list[tuple[str, str]], list[tuple[str, str]]]] = {}


def _trailer_vocab(dev_kw: dict) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    cached = _VOCAB_CACHE.get(id(dev_kw))
    if cached is not None and cached[0] is dev_kw:
        return cached[1], cached[2]
    # Longest first, so "hermes agent" is tried before shorter names.
    needles = sorted(
        ((n.lower(), t) for n, t in dev_kw.get("trailer_tools", {}).items()),
        key=lambda nt: -len(nt[0]),
    )
    # A config that predates coauthor_emails still gets the defaults.
    email_src = dev_kw.get("coauthor_emails", DEFAULT_AI_DEV_KEYWORDS["coauthor_emails"])
    emails = [(e.lower(), t) for e, t in email_src.items()]
    _VOCAB_CACHE[id(dev_kw)] = (dev_kw, needles, emails)
    return needles, emails


def _starts_with_word(text: str, word: str) -> bool:
    return text.startswith(word) and not text[len(word):len(word) + 1].isalnum()


def _leading_tool(text: str, needles: list[tuple[str, str]]) -> str | None:
    text = _LEADING_NOISE.sub("", text)
    stripped = True
    while stripped:
        stripped = False
        for word in _VENDOR_WORDS:
            if _starts_with_word(text, word):
                text = _LEADING_NOISE.sub("", text[len(word):])
                stripped = True
    for needle, tool in needles:
        if _starts_with_word(text, needle):
            return tool
    return None


def _coauthor_tool(
    name: str, email: str, needles: list[tuple[str, str]], emails: list[tuple[str, str]]
) -> str | None:
    for marker, tool in emails:
        if marker in email:
            return tool
    if not email or "[bot]" in email:
        return _leading_tool(name, needles)
    return None


def match_trailer_tools(text: str | None, dev_kw: dict) -> set[str]:
    """Return the AI tools credited by co-author / "generated with" lines of *text*.

    A ``Co-authored-by:`` line credits a tool when its e-mail is a known AI
    address, or when the identity is automated and the name starts with the
    tool's name. A "Generated with/by/using" line credits only the tool named
    directly after the phrase. Prose and template lines that merely list tools
    credit nothing. Shared by the commit message scan and the PR body scan.
    """
    needles, emails = _trailer_vocab(dev_kw)
    tools: set[str] = set()
    lines = (text or "").splitlines()
    for i, raw_line in enumerate(lines):
        line = _LEADING_NOISE.sub("", raw_line.strip().lower())
        if not line:
            continue
        coauthor = _COAUTHOR_LINE.match(line)
        if coauthor:
            tool = _coauthor_tool(
                coauthor["name"], coauthor["email"] or "", needles, emails
            )
        else:
            generated = _GENERATED_MARKER.search(line)
            if not generated:
                continue
            rest = generated["rest"]
            # "Generated with:" on one line and the tool on the next.
            if not _LEADING_NOISE.sub("", rest) and i + 1 < len(lines):
                rest = lines[i + 1].strip().lower()
            tool = _leading_tool(rest, needles)
        if tool:
            tools.add(tool)
    return tools


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
    coauthor_tools = match_trailer_tools(message, dev_kw)
    author_tools: set[str] = set()

    tool = match_agent_bot(author_login, author_email, dev_kw)
    if tool:
        author_tools.add(tool)

    return coauthor_tools, author_tools
