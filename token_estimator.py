"""Token Estimator — estimate LLM token costs from task descriptions."""

from __future__ import annotations

import json
import math
import re
import sys
from dataclasses import dataclass
from typing import Sequence

# ============================================================
# Pricing (per 1M tokens, USD) — update as of 2026-04
# ============================================================
PRICING: dict[str, dict[str, float]] = {
    "gpt-4.1": {"input": 2.0, "output": 8.0},
    "gpt-4o": {"input": 2.5, "output": 10.0},
    "gpt-o3": {"input": 4.0, "output": 16.0},
    "gpt-o4-mini": {"input": 1.1, "output": 4.4},
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
    "claude-opus-4-6": {"input": 15.0, "output": 75.0},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.0},
    "gemini-2.5-flash": {"input": 0.15, "output": 0.6},
    "llama-4-maverick": {"input": 0.15, "output": 0.6},
    "llama-4-scout": {"input": 0.25, "output": 1.0},
}

DEFAULT_MODEL = "claude-sonnet-4-6"

# Multipliers for task complexity
COMPLEXITY_MULTIPLIERS = {
    "code_generation": 1.8,
    "code_review": 1.2,
    "debugging": 1.5,
    "writing": 1.0,
    "research": 1.4,
    "simple_qa": 0.6,
    "planning": 1.3,
    "refactoring": 1.6,
}

# Keywords to detect complexity class
KEYWORDS: dict[str, list[str]] = {
    "code_generation": ["create", "build", "implement", "write a function", "script", "endpoint", "api", "add"],
    "code_review": ["review", "check code", "analyze", "look at", "audit"],
    "debugging": ["fix", "debug", "error", "bug", "crash", "broken", "not working", "issue"],
    "writing": ["write", "draft", "article", "blog", "document", "readme", "compose"],
    "research": ["research", "compare", "find information", "search", "investigate", "analyze"],
    "simple_qa": ["what is", "explain", "define", "how does"],
    "planning": ["plan", "design", "architect", "proposal", "spec", "roadmap"],
    "refactoring": ["refactor", "restructure", "clean up", "optimize", "improve", "reorganize"],
}


@dataclass
class Estimate:
    """Token cost estimate."""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    complexity: str
    model: str

    def to_dict(self) -> dict:
        return {
            "model": self.model,
            "complexity": self.complexity,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "input_cost_usd": round(self.input_cost, 6),
            "output_cost_usd": round(self.output_cost, 6),
            "total_cost_usd": round(self.total_cost, 6),
        }


def _estimate_tokens(text: str) -> int:
    """Rough word-to-token estimate (1 token ~= 0.75 English words)."""
    # Split on whitespace/punctuation boundaries
    tokens = re.findall(r"\w+(?:[-']\w+)*|[^\w\s]", text)
    return max(1, math.ceil(len(tokens) * 1.33))  # char-level approximation


def _detect_complexity(text: str) -> tuple[str, float]:
    """Detect task complexity and return (category, multiplier)."""
    text_lower = text.lower()
    scores: dict[str, int] = {}

    for category, keywords_list in KEYWORDS.items():
        for kw in keywords_list:
            if kw in text_lower:
                scores[category] = scores.get(category, 0) + 1

    if not scores:
        return "simple_qa", COMPLEXITY_MULTIPLIERS["simple_qa"]

    best = max(scores, key=scores.get)  # type: ignore[arg-type]
    return best, COMPLEXITY_MULTIPLIERS[best]


def estimate(
    task: str,
    *,
    model: str = DEFAULT_MODEL,
    system_prompt_tokens: int = 0,
    few_shot_examples: Sequence[str] = (),
    include_attachments: bool = False,
) -> Estimate:
    """Estimate token usage and cost for a given task description."""

    model_lower = model.lower()
    if model_lower not in PRICING:
        known = ", ".join(sorted(PRICING))
        raise ValueError(f"Unknown model '{model}'. Known: {known}")

    price = PRICING[model_lower]
    complexity, multiplier = _detect_complexity(task)

    # Input tokens
    input_tokens = _estimate_tokens(task) + system_prompt_tokens
    for ex in few_shot_examples:
        input_tokens += _estimate_tokens(ex)

    # Attachment overhead (~1500 tokens per image if included)
    if include_attachments:
        input_tokens += 1500

    # Output tokens scale with input + complexity
    base_output = max(200, int(input_tokens * 3))  # outputs tend to be 2-5x inputs
    output_tokens = int(base_output * multiplier)

    # Costs (per 1M tokens)
    input_cost = (input_tokens / 1_000_000) * price["input"]
    output_cost = (output_tokens / 1_000_000) * price["output"]

    return Estimate(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        input_cost=input_cost,
        output_cost=output_cost,
        total_cost=input_cost + output_cost,
        complexity=complexity,
        model=model,
    )


def format_report(est: Estimate) -> str:
    """Pretty-print an estimate."""
    lines = [
        f"  Model:       {est.model}",
        f"  Complexity:  {est.complexity}",
        f"  Input tokens:  {est.input_tokens:>8,}",
        f"  Output tokens: {est.output_tokens:>8,}",
        f"  Total tokens:  {est.total_tokens:>8,}",
        f"  Input cost:    ${est.input_cost:.6f}",
        f"  Output cost:   ${est.output_cost:.6f}",
        f"  Total cost:    ${est.total_cost:.6f}",
    ]
    return "\n".join(lines)


def main() -> None:
    if "--list-models" in sys.argv:
        print("Supported models:")
        for name, pricing in sorted(PRICING.items()):
            print(f"  {name}:  in=${pricing['input']}/1M, out=${pricing['output']}/1M")
        return

    if len(sys.argv) < 2 or "--help" in sys.argv:
        print("Usage: python -m token_estimator \"Your task description\" [--model MODEL]")
        print()
        print("Options:")
        print("  --model MODEL    Model to estimate for (default: claude-sonnet-4-6)")
        print("  --list-models    List all supported models and pricing")
        print("  --json           Output as JSON")
        print("  --all-models     Estimate for all supported models")
        return

    task = sys.argv[1]
    model = DEFAULT_MODEL

    if "--model" in sys.argv:
        idx = sys.argv.index("--model")
        if idx + 1 < len(sys.argv):
            model = sys.argv[idx + 1]

    if "--all-models" in sys.argv:
        results = []
        for name in PRICING:
            est = estimate(task, model=name)
            results.append(est.to_dict())
        print(json.dumps(results, indent=2))
        return

    est = estimate(task, model=model)

    if "--json" in sys.argv:
        print(json.dumps(est.to_dict(), indent=2))
    else:
        print(f'Estimate for: "{task}"')
        print(format_report(est))


if __name__ == "__main__":
    main()
