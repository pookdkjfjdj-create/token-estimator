<p align="center">

# Token Estimator

</p>

<p align="center">
  <em>Stop burning money on LLM prompts — estimate before you send.</em>
</p>

<p align="center">
  <a href="https://github.com/pookdkjfjdj-create/token-estimator/stargazers">
    <img src="https://img.shields.io/github/stars/pookdkjfjdj-create/token-estimator?color=yellow&logo=github&style=for-the-badge" alt="Stars">
  </a>
  <img src="https://img.shields.io/badge/Python_3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-2ea44f?style=for-the-badge&logo=opensourceinitiative" alt="License">
  </a>
  <img src="https://img.shields.io/badge/Dependencies-None-ff69b4?style=for-the-badge" alt="Zero deps">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/GPT--4.1-4.1-blue?style=flat" alt="GPT-4.1">
  <img src="https://img.shields.io/badge/GPT--4o-4o-blue?style=flat" alt="GPT-4o">
  <img src="https://img.shields.io/badge/GPT--O3-O3-blue?style=flat" alt="GPT-o3">
  <img src="https://img.shields.io/badge/GPT--O4--Mini-O4_Mini-blue?style=flat" alt="GPT-o4-mini">
  <img src="https://img.shields.io/badge/Claude_Sonnet-Sonnet_4.6-orange?style=flat" alt="Claude">
  <img src="https://img.shields.io/badge/Claude_Opus-Opus_4.6-purple?style=flat" alt="Claude Opus">
  <img src="https://img.shields.io/badge/Gemini_2.5-Pro-red?style=flat" alt="Gemini">
  <img src="https://img.shields.io/badge/Llama_4-Maverick-22c55e?style=flat" alt="Llama">
</p>

<br>

---

## The Problem

LLM APIs charge **per token**. A vague task description can cost **50x more** than a tight one.

> **You have no idea how much a prompt will consume until *after* the API call.**

Token Estimator changes that. Analyze any task description → get token and cost estimates across **10+ models** — *before* you run the actual prompt.

## Quick Start

### One command

```bash
python -m token_estimator "Build a FastAPI endpoint with JWT auth and rate limiting"
```

**You'll see:**

```
Estimate for: "Build a FastAPI endpoint with JWT auth and rate limiting"
  Model:       claude-sonnet-4-6
  Complexity:  code_generation
  Input tokens:        154
  Output tokens:       827
  Total tokens:        981
  Input cost:    $0.000462
  Output cost:   $0.012398
  Total cost:    $0.012860
```

### Compare all models at once

```bash
python -m token_estimator "Debug production 500 on login" --all-models
```

```json
[
  {
    "model": "gpt-4.1",
    "complexity": "debugging",
    "total_cost_usd": 0.001865
  },
  {
    "model": "llama-4-maverick",
    "complexity": "debugging",
    "total_cost_usd": 0.000333
  },
  {
    "model": "claude-opus-4-6",
    "complexity": "debugging",
    "total_cost_usd": 0.080730
  }
]
```

---

## Commands

| Flag | Use |
|:---|:---|
| <code>python -m token_estimator "task"</code> | Quick estimate (default model) |
| <code>--model gpt-4o</code> | Specific model |
| <code>--all-models</code> | All 10 models side by side |
| <code>--json</code> | JSON output (pipe-friendly) |
| <code>--list-models</code> | Supported models & prices |
| <code>--help</code> | Full usage guide |

---

## Python API

```python
from token_estimator import estimate, format_report

# Single task, single model
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

# With image attachments
est = estimate(
    "Describe this screenshot",
    model="gpt-4o",
    include_attachments=True,
)
```

---

## Supported Models

| Model | Input (per 1M) | Output (per 1M) | Est. 1K tok cost |
|:---|:---:|:---:|:---:|
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

> Prices updated April 2026. Want to adjust? Edit [line 15 in `token_estimator.py`](token_estimator.py#L15).

---

## Complexity Detection

Your task description is classified into **8 tiers**:

| Tier | Cost | Example |
|:---|:---:|:---|
| simple_qa | **0.6x** | "What is a closure in Python?" |
| writing | **1.0x** | "Draft an article on async" |
| code_review | **1.2x** | "Review this endpoint" |
| planning | **1.3x** | "Design the database schema" |
| research | **1.4x** | "Compare Redis vs Memcached" |
| debugging | **1.5x** | "Fix the connection leak" |
| refactoring | **1.6x** | "Extract this into separate services" |
| code_generation | **1.8x** | "Build a REST API from scratch" |

---

## How It Works

```
TASK DESCRIPTION
"Build a FastAPI endpoint with JWT auth"
    │
    ├── Token Counting        words × 1.33 → ~20 tok
    │
    ├── Complexity Detection  keywords → code_generation (1.8x)
    │
    ├── Output Scaling        base = max(200, input × 3) × multiplier
    │
    ├── Cost Calculation      tokens / 1M × model price → total USD
    │
    └── Report                tokens + cost → you decide
```

### Accuracy

This is an **order-of-magnitude** estimate. Actual usage varies by:

- Tokenization differences between models
- Temperature and response randomness
- Prompt structure and few-shot examples
- Whether the model rambles or stays concise

> Use it to **compare** tasks and models — not to bill invoices.

---

## Contributing

PRs are welcome! Ideas for future improvements:

- [ ] Add more models and update pricing
- [ ] Real `tiktoken`-based counting instead of word approximation
- [ ] Image/file attachment cost estimation
- [ ] Simple web UI
- [ ] Historical cost tracking per session
- [ ] Prompt optimization suggestions

---

## License

MIT — use it however you want.

<p align="center">
  Made with care by
  <a href="https://github.com/pookdkjfjdj-create">@pookdkjfjdj-create</a>
</p>
