/**
 * Kongen Smart Router — Route LLM calls through Kongen for 60% cost savings.
 *
 * Scores each prompt with Kongen's morphogenetic analysis to determine complexity,
 * then routes to the cheapest model that can handle it.
 *
 * Usage:
 *   npm install @anthropic-ai/sdk openai
 *
 *   export KONGEN_API_KEY="kl_live_..."
 *   export ANTHROPIC_API_KEY="sk-ant-..."   # for Claude
 *   export OPENAI_API_KEY="sk-..."          # for OpenAI
 *
 *   node kongen_router.js
 */

const KONGEN_BASE =
  process.env.KONGEN_API_BASE_URL || "https://api.kongenlabs.life";
const KONGEN_KEY = process.env.KONGEN_API_KEY;

// --- Model tiers (cheapest → most capable) ---

const CLAUDE_TIERS = [
  { name: "claude-haiku-4-5-20251001", inputCost: 1.0, outputCost: 5.0, maxRegime: "fast" },
  { name: "claude-sonnet-4-6", inputCost: 3.0, outputCost: 15.0, maxRegime: "deep" },
  { name: "claude-opus-4-6", inputCost: 5.0, outputCost: 25.0, maxRegime: "exhaustive" },
];

const OPENAI_TIERS = [
  { name: "gpt-4o-mini", inputCost: 0.15, outputCost: 0.60, maxRegime: "fast" },
  { name: "gpt-4o", inputCost: 2.50, outputCost: 10.0, maxRegime: "deep" },
  { name: "o3", inputCost: 10.0, outputCost: 40.0, maxRegime: "exhaustive" },
];

const REGIME_ORDER = ["trivial", "fast", "moderate", "deep", "exhaustive"];

function pickModel(regime, tiers) {
  const idx = REGIME_ORDER.indexOf(regime);
  const regimeIdx = idx >= 0 ? idx : 2;
  for (const tier of tiers) {
    if (REGIME_ORDER.indexOf(tier.maxRegime) >= regimeIdx) return tier;
  }
  return tiers[tiers.length - 1];
}

function estimateCost(model, inputTokens, outputTokens) {
  return (
    (inputTokens * model.inputCost) / 1_000_000 +
    (outputTokens * model.outputCost) / 1_000_000
  );
}

// --- Kongen API call ---

async function scorePrompt(text) {
  const res = await fetch(`${KONGEN_BASE}/v1/logic/score`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": KONGEN_KEY,
    },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(`Kongen API error ${res.status}: ${err.detail || res.statusText}`);
  }
  return res.json();
}

// --- Smart Router ---

class KongenRouter {
  constructor(provider = "claude") {
    this.provider = provider;
    this.tiers = provider === "claude" ? CLAUDE_TIERS : OPENAI_TIERS;
    this.totalSpent = 0;
    this.totalSaved = 0;
    this.calls = 0;
  }

  async complete(prompt, { system = "You are a helpful assistant.", maxTokens } = {}) {
    // 1. Score with Kongen (1 KT)
    const score = await scorePrompt(prompt);
    const regime = score.regime;
    const recommended = score.recommended_tokens;

    // 2. Pick cheapest capable model
    const model = pickModel(regime, this.tiers);
    const expensive = this.tiers[this.tiers.length - 1];

    // 3. Use recommended tokens if no override
    const tokens = maxTokens || Math.min(recommended, 4096);

    // 4. Call the LLM
    let text, inputTokens, outputTokens;

    if (this.provider === "claude") {
      const Anthropic = (await import("@anthropic-ai/sdk")).default;
      const client = new Anthropic();
      const response = await client.messages.create({
        model: model.name,
        max_tokens: tokens,
        system,
        messages: [{ role: "user", content: prompt }],
      });
      text = response.content[0].text;
      inputTokens = response.usage.input_tokens;
      outputTokens = response.usage.output_tokens;
    } else {
      const OpenAI = (await import("openai")).default;
      const client = new OpenAI();
      const response = await client.chat.completions.create({
        model: model.name,
        max_tokens: tokens,
        messages: [
          { role: "system", content: system },
          { role: "user", content: prompt },
        ],
      });
      text = response.choices[0].message.content;
      inputTokens = response.usage.prompt_tokens;
      outputTokens = response.usage.completion_tokens;
    }

    // 5. Calculate savings
    const cost = estimateCost(model, inputTokens, outputTokens);
    const wouldCost = estimateCost(expensive, inputTokens, outputTokens);
    const saved = wouldCost - cost;

    this.totalSpent += cost;
    this.totalSaved += saved;
    this.calls++;

    return {
      text,
      model: model.name,
      regime,
      boostFactor: score.boost_factor,
      cost,
      wouldCost,
      saved,
      inputTokens,
      outputTokens,
    };
  }

  stats() {
    const total = this.totalSpent + this.totalSaved;
    return {
      calls: this.calls,
      totalSpent: +this.totalSpent.toFixed(4),
      totalSaved: +this.totalSaved.toFixed(4),
      savingsPct: total > 0 ? +((this.totalSaved / total) * 100).toFixed(1) : 0,
    };
  }
}

// --- Demo ---

async function main() {
  if (!KONGEN_KEY) {
    console.log("Set KONGEN_API_KEY (get one at https://garden.kongenlabs.life/keys)");
    console.log("Also set ANTHROPIC_API_KEY or OPENAI_API_KEY");
    process.exit(1);
  }

  const provider = process.env.ANTHROPIC_API_KEY ? "claude" : "openai";
  const router = new KongenRouter(provider);
  console.log(`Kongen Smart Router (${provider})\n${"=".repeat(50)}\n`);

  const prompts = [
    "What is 2 + 2?",
    "Summarize the key differences between TCP and UDP.",
    "Write a Python function to check if a number is prime.",
    "Explain the implications of Godel's incompleteness theorems on AI.",
    "Prove that the sum of the first n odd numbers equals n squared.",
  ];

  for (const prompt of prompts) {
    const r = await router.complete(prompt);
    console.log(`Prompt: ${prompt.slice(0, 60)}...`);
    console.log(`  Regime: ${r.regime} -> Model: ${r.model}`);
    console.log(`  Cost: $${r.cost.toFixed(4)} (would be $${r.wouldCost.toFixed(4)}, saved $${r.saved.toFixed(4)})`);
    console.log(`  Tokens: ${r.inputTokens}in/${r.outputTokens}out\n`);
  }

  const s = router.stats();
  console.log("=".repeat(50));
  console.log(
    `Total: ${s.calls} calls, $${s.totalSpent} spent, $${s.totalSaved} saved (${s.savingsPct}%)`
  );
}

main().catch(console.error);
