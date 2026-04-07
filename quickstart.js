/**
 * Kongen Labs — Quickstart (Node.js)
 *
 * Score a prompt, check routing, and see transfer scoring.
 *
 *   npm install @kongenlabs/sdk
 *   export KONGEN_API_KEY="kl_live_..."
 *   node quickstart.js
 */

const { KongenClient } = require("@kongenlabs/sdk");

async function main() {
  const client = new KongenClient(); // reads KONGEN_API_KEY from env

  // --- 1. Score a prompt (1 KT) ---
  const result = await client.logic.score(
    "Explain quantum entanglement in simple terms"
  );
  console.log(`Regime:     ${result.regime}`);
  console.log(`Boost:      ${result.boost_factor}`);
  console.log(`Tokens:     ${result.recommended_tokens}`);
  console.log();

  // --- 2. Route based on regime ---
  const MODEL_MAP = {
    trivial: "haiku",
    fast: "haiku",
    moderate: "sonnet",
    deep: "sonnet",
    exhaustive: "opus",
  };
  console.log(`Recommended model: ${MODEL_MAP[result.regime] || "sonnet"}`);
  console.log(`Max tokens to use: ${result.recommended_tokens}`);
  console.log();

  // --- 3. Transfer scoring (50 KT) ---
  const transfer = await client.transfer.scoreSignal({
    complexity: 0.72,
    constraint: 0.65,
    boundary: 0.81,
    coherence: 0.44,
    magnitude: 1.56,
    balance: 1.11,
    gradient: 0.39,
  });
  console.log(`Pattern:    ${transfer.classification}`);
  console.log(`Confidence: ${transfer.confidence.toFixed(3)}`);
  console.log(`Boost:      ${transfer.boost_factor > 0 ? "+" : ""}${transfer.boost_factor.toFixed(3)}`);
  for (const ev of transfer.evidence) {
    console.log(
      `  ${ev.source_domain}: sim=${ev.similarity.toFixed(3)}`
    );
  }
  console.log();

  // --- 4. Token usage ---
  console.log(`Tokens used: ${client.tokenUsage?.used ?? "N/A"}`);
  console.log(`Remaining:   ${client.tokenUsage?.remaining ?? "N/A"}`);
}

main().catch((e) => {
  console.error("Error:", e.message);
  process.exit(1);
});
