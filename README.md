# Token Estimator

> Estimate how many tokens your LLM task will consume — and how much it'll cost — before you run it.

A zero-dependency Python tool that analyzes a task description, detects complexity, and gives you a rough estimate of **input/output tokens** and **USD cost** across **10+ AI models**.

---

## Why?

LLM APIs charge per token. A vague task description can cost 50x more than a tight one. This tool helps you:

- **Predict costs** before sending a prompt
- **Compare models** — same task, different prices
- **Understand complexity** — code gen vs review vs debugging vs planning
- **Budget** recurring API tasks

## Installation

```bash
git clone https://github.com/pookdkjfjdj-create/token-estimator.git
cd token-estimator
```

**Zero dependencies. Python 3.10+.**

## Usage

### CLI

```bash
# Basic estimate
python -m token_estimator "Fix the login page. Users report 500 errors on form submit."

# Specific model
python -m token_estimator "Write a FastAPI endpoint with auth" --model gpt-4o

# Compare all models at once
python -m token_estimator "Refactor monolithic function into service layer" --all-models

# JSON output (for piping)
python -m token_estimator "Debug the database migration" --json

# List supported models and prices
python -m token_estimator --list-models
```

### Python API

```python
from token_estimator import estimate, format_report

est = estimate(
    "Build a REST API with Flask: users, posts, comments. "
    "Include SQLAlchemy models, Pydantic schemas, "
    "JWT auth, and rate limiting.",
    model="claude-sonnet-4-6",
)

print(format_report(est))
# Model:       claude-sonnet-4-6
# Complexity:  code_generation
# Input tokens:       132
# Output tokens:     1,108
# Total tokens:      1,240
# Total cost:    $0.006546
```

## Supported Models

| Model | Input (per 1M) | Output (per 1M) |
|---|---|---|
| gpt-4.1 | $2.00 | $8.00 |
| gpt-4o | $2.50 | $10.00 |
| gpt-o3 | $4.00 | $16.00 |
| gpt-o4-mini | $1.10 | $4.40 |
| claude-sonnet-4-6 | $3.00 | $15.00 |
| claude-opus-4-6 | $15.00 | $75.00 |
| gemini-2.5-pro | $1.25 | $10.00 |
| gemini-2.5-flash | $0.15 | $0.60 |
| llama-4-maverick | $0.15 | $0.60 |
| llama-4-scout | $0.25 | $1.00 |

## Complexity Detection

The tool classifies tasks into **8 complexity tiers**:

| Tier | Multiplier | Keywords |
|---|---|---|
| `simple_qa` | 0.6x | "what is", "explain", "define" |
| `writing` | 1.0x | "draft", "article", "blog" |
| `code_review` | 1.2x | "review", "analyze", "audit" |
| `planning` | 1.3x | "design", "architect", "roadmap" |
| `debugging` | 1.5x | "fix", "debug", "error" |
| `refactoring` | 1.6x | "refactor", "restructure", "optimize" |
| `research` | 1.4x | "research", "compare", "investigate" |
| `code_generation` | 1.8x | "create", "build", "implement" |

## How It Works

1. **Token counting** — Rough `words * 1.33` approximation (1 token ≈ 0.75 English words). Close enough for estimates.
2. **Complexity detection** — Keyword matching against 8 categories. The most-matched category wins.
3. **Output scaling** — Base output = max(200, input * 3), multiplied by complexity factor.
4. **Cost calculation** — Uses per-model pricing (per 1M tokens).

> This is an **order-of-magnitude** estimate. Actual usage varies by model, temperature, and prompt structure. Use it to compare, not to bill invoices.

## Contributing

PRs welcome! Some ideas:

- Add more models and update pricing
- Improve token counting accuracy
- Add support for image/file attachments estimation
- Build a simple web UI
- Add historical cost tracking

## License

MIT
