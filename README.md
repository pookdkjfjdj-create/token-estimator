# Token Estimator

<p align="center">
  <em>Stop burning money on LLM prompts — estimate before you send.</em>
</p>

<p align="center">
  <strong>Zero dependencies</strong> &middot; Python 3.10+ &middot; 10+ models &middot; CLI + API
</p>

---

## The Problem

LLM APIs charge per token. A vague task description can cost **50x more** than a tight one. Developers and teams have no idea how much a prompt will actually consume until after the API call.

**Token Estimator** changes that — it analyzes your task description, detects complexity, and gives you a **rough estimate of tokens and cost** across 10+ models, all before you run the actual prompt.

## Quick Start

```bash
# Clone
git clone https://github.com/pookdkjfjdj-create/token-estimator.git
cd token-estimator

# Estimate a task
python -m token_estimator "Build a FastAPI endpoint with auth and rate limiting"
```

**Output:**
```
Estimate for: "Build a FastAPI endpoint with auth and rate limiting"
  Model:       claude-sonnet-4-6
  Complexity:  code_generation
  Input tokens:        154
  Output tokens:       827
  Total tokens:        981
  Input cost:    $0.000462
  Output cost:   $0.012398
  Total cost:    $0.012860
```

### Compare Models

```bash
python -m token_estimator "Debug production 500 error on login" --all-models
```

```json
[
  {
    "model": "gpt-4.1",
    "complexity": "debugging",
    "total_tokens": 741,
    "total_cost_usd": 0.001865
  },
  {
    "model": "claude-sonnet-4-6",
    "complexity": "debugging",
    "total_tokens": 741,
    "total_cost_usd": 0.008892
  }
]
```

## Usage

| Command | Description |
|---|---|
| `python -m token_estimator "task text"` | Quick estimate (default model) |
| `python -m token_estimator "task" --model gpt-4o` | Specific model |
| `python -m token_estimator "task" --all-models` | All 10 models at once |
| `python -m token_estimator "task" --json` | JSON output (pipe-friendly) |
| `python -m token_estimator --list-models` | See all supported models & prices |
| `python -m token_estimator --help` | Show usage |

### Python API

```python
from token_estimator import estimate, format_report

# Single model
est = estimate(
    "Write a Celery task that processes CSV uploads and stores results in Postgres",
    model="claude-sonnet-4-6",
)
print(format_report(est))

# With system prompt overhead
est = estimate(
    "Fix the race condition in the cache layer",
    model="gpt-4o",
    system_prompt_tokens=500,
)

# With few-shot examples
est = estimate(
    "Classify sentiment: positive, negative, neutral",
    model="gemini-2.5-flash",
    few_shot_examples=[
        "Great product! Five stars.",
        "Terrible, broke on day one.",
    ],
)
```

## Supported Models

| Model | Input (per 1M tok) | Output (per 1M tok) | Est. 1K token cost |
|---|---|---|---|
| llama-4-maverick | $0.15 | $0.60 | $0.00075 |
| gemini-2.5-flash | $0.15 | $0.60 | $0.00075 |
| llama-4-scout | $0.25 | $1.00 | $0.00125 |
| gpt-o4-mini | $1.10 | $4.40 | $0.00550 |
| gemini-2.5-pro | $1.25 | $10.00 | $0.01125 |
| **gpt-4.1** | $2.00 | $8.00 | $0.01000 |
| gpt-4o | $2.50 | $10.00 | $0.01250 |
| **claude-sonnet-4-6** | $3.00 | $15.00 | $0.01800 |
| gpt-o3 | $4.00 | $16.00 | $0.02000 |
| claude-opus-4-6 | $15.00 | $75.00 | $0.09000 |

> Prices updated April 2026. [Edit pricing in `token_estimator.py` line 15.](token_estimator.py#L15)

## Complexity Tiers

The tool classifies tasks into **8 complexity tiers** based on keyword matching:

| Tier | Multiplier | When |
|---|---|---|
| `simple_qa` | **0.6x** | "What is...", "explain...", "define..." |
| `writing` | **1.0x** | "Draft an article", "write documentation" |
| `code_review` | **1.2x** | "Review this code", "analyze..." |
| `planning` | **1.3x** | "Design architecture", "roadmap..." |
| `research` | **1.4x** | "Compare X vs Y", "investigate..." |
| `debugging` | **1.5x** | "Fix the error", "debug the crash" |
| `refactoring` | **1.6x** | "Refactor this function", "clean up" |
| `code_generation` | **1.8x** | "Build an API", "create a component" |

## How It Works

```
┌─────────────────────────────────────────────────┐
│              Task Description                    │
│  "Build a FastAPI endpoint with JWT auth"       │
└──────────────┬──────────────────────────────────┘
               │
    ┌──────────▼──────────┐
    │  Token Counting     │  words × 1.33
    │  ~15 words → ~20 tok│
    └──────────┬──────────┘
               │
    ┌──────────▼────────────────────┐
    │  Complexity Detection          │  keyword matching
    │  "Build", "endpoint"           │  → code_generation (1.8x)
    │  "API", "auth"                 │
    └──────────┬────────────────────┘
               │
    ┌──────────▼──────────────┐
    │  Output Scaling          │  base = max(200, input × 3)
    │  output = base × 1.8x    │  → complexity multiplier
    └──────────┬──────────────┘
               │
    ┌──────────▼──────────────┐
    │  Cost Calculation        │  tokens/1M × model price
    │  input + output cost     │  → total USD
    └──────────┬──────────────┘
               │
    ┌──────────▼──────────────┐
    │  📊 Estimate Report      │  tokens + cost
    └─────────────────────────┘
```

## Accuracy

This is an **order-of-magnitude** estimate. Actual usage varies by:

- Model-specific tokenization (GPT vs Claude differ)
- Temperature and randomness of responses
- Prompt structure and few-shot examples
- Whether the model rambles or stays concise

**Use it to compare tasks and models, not to bill invoices.**

## Contributing

PRs welcome! Ideas for improvements:

- [ ] Add more models and update pricing
- [ ] Real tiktoken-based counting instead of word approximation
- [ ] Image/file attachment cost estimation
- [ ] Simple web UI
- [ ] Historical cost tracking per session
- [ ] Prompt optimization suggestions

## License

MIT — use it however you want.
