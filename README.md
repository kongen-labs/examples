# Kongen Labs — Examples

Practical examples for the [Kongen Labs](https://kongenlabs.life) API. Score prompts, route to the cheapest capable LLM, and leverage cross-domain pattern transfer.

## Quick Start

```bash
# Python
pip install kongenlabs
export KONGEN_API_KEY="kl_live_..."
python quickstart.py

# Node.js
npm install @kongenlabs/sdk
export KONGEN_API_KEY="kl_live_..."
node quickstart.js
```

Get your API key at [garden.kongenlabs.life/keys](https://garden.kongenlabs.life/keys).

## Examples

| File | Description | Tokens |
|------|-------------|--------|
| `quickstart.py` | Score a prompt, transfer scoring, batch scoring (Python) | ~171 KT |
| `quickstart.js` | Score a prompt, transfer scoring (Node.js) | ~51 KT |
| `kongen_router.py` | Smart LLM router (Python) — routes to cheapest model per prompt | 1 KT/prompt |
| `kongen_router.js` | Smart LLM router (JavaScript) — same logic, Node.js | 1 KT/prompt |
| `organism_examples.py` | Organism creation at all 3 levels (L0 raw, L1 schema, L2 collective) | varies |
| `datacenter_ops.py` | Datacenter/SRE use cases — capacity planning, failure prediction, alert reduction | varies |

## Smart Router

The router scores each prompt with Kongen to determine its reasoning complexity (regime), then picks the cheapest LLM model that can handle it. Typical savings: **40–60%** on inference costs.

```
Prompt: "What is 2+2?"
  → Regime: trivial → Haiku ($1/M tokens) ✓

Prompt: "Prove √2 is irrational"
  → Regime: deep → Sonnet ($3/M tokens) ✓

Prompt: "Prove P ≠ NP"
  → Regime: exhaustive → Opus ($5/M tokens) ✓
```

### Python

```bash
pip install kongenlabs anthropic  # or openai
export KONGEN_API_KEY="kl_live_..."
export ANTHROPIC_API_KEY="sk-ant-..."
python kongen_router.py
```

### JavaScript

```bash
npm install @anthropic-ai/sdk  # or openai
export KONGEN_API_KEY="kl_live_..."
export ANTHROPIC_API_KEY="sk-ant-..."
node kongen_router.js
```

## Datacenter / SRE

Use pattern intelligence to make smarter infrastructure decisions. Instead of N threshold alerts that fire independently, observe the structural relationship between all your metrics at once.

```bash
pip install kongenlabs
export KONGEN_API_KEY="kl_live_..."
python datacenter_ops.py
```

**5 use cases in `datacenter_ops.py`:**

| Use Case | What | Savings |
|----------|------|---------|
| Proactive Capacity | Distinguish healthy traffic spikes from pre-failure patterns | $2-15K/incident |
| Drive Failure | Detect degradation 2-14 days before SMART thresholds | $50K+ data risk |
| Scaling Confidence | Cross-domain evidence for scale-up/down decisions | $2-5K/day |
| Alert Reduction | 1 pattern check replaces 5+ threshold alerts | 80-90% fewer pages |
| Batch Fleet Scoring | Score entire fleet in 1 call at 20% discount | 20% API savings |

## Organisms

Create domain-specific pattern organisms at three levels of integration:

```bash
python organism_examples.py
```

- **Level 0 (Raw):** Push 7 floats, get classification — zero config
- **Level 1 (Schema):** Named fields with semantic roles — auto-normalization
- **Level 2 (Collective):** Outcomes + cross-domain analogy webhooks — full intelligence

## Token Costs

Pay-as-you-go at **$0.0007 per Kongen Token**. All accounts start with 5,000 free credits.

| Operation | Tokens | Cost |
|-----------|--------|------|
| Logic Score (prompt analysis) | 1 KT | $0.0007 |
| Transfer Score (cross-domain) | 50 KT | $0.035 |
| Transfer Batch (per item) | 40 KT | $0.028 |
| MCP Tool Call | Same as REST | Same as REST |

## Links

- [Documentation](https://garden.kongenlabs.life/docs)
- [API Reference](https://api.kongenlabs.life/docs)
- [Get API Key](https://garden.kongenlabs.life/keys)
- [Pricing](https://kongenlabs.life/#pricing)
