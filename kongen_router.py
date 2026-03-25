"""
Kongen Smart Router — Route LLM calls through Kongen for 60% cost savings.

Scores each prompt with Kongen's morphogenetic analysis to determine complexity,
then routes to the cheapest model that can handle it. Works with both Anthropic
(Claude) and OpenAI APIs.

Usage:
    pip install kongenlabs anthropic openai

    export KONGEN_API_KEY="kl_live_..."
    export ANTHROPIC_API_KEY="sk-ant-..."   # for Claude
    export OPENAI_API_KEY="sk-..."          # for OpenAI

    python kongen_router.py
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from kongen import KongenClient


# --- Model routing configuration ---

@dataclass
class ModelTier:
    """LLM model tier with cost info."""
    name: str
    input_cost_per_m: float   # $ per 1M input tokens
    output_cost_per_m: float  # $ per 1M output tokens
    max_regime: str           # highest regime this model handles well


# Claude model tiers (cheapest → most capable)
CLAUDE_TIERS = [
    ModelTier("claude-haiku-4-5-20251001", 1.0, 5.0, "fast"),
    ModelTier("claude-sonnet-4-6", 3.0, 15.0, "deep"),
    ModelTier("claude-opus-4-6", 5.0, 25.0, "exhaustive"),
]

# OpenAI model tiers
OPENAI_TIERS = [
    ModelTier("gpt-4o-mini", 0.15, 0.60, "fast"),
    ModelTier("gpt-4o", 2.50, 10.0, "deep"),
    ModelTier("o3", 10.0, 40.0, "exhaustive"),
]

# Regime ordering (simplest → most complex)
REGIME_ORDER = ["trivial", "fast", "moderate", "deep", "exhaustive"]


def pick_model(regime: str, tiers: list[ModelTier]) -> ModelTier:
    """Pick the cheapest model that can handle the given regime."""
    regime_idx = REGIME_ORDER.index(regime) if regime in REGIME_ORDER else 2
    for tier in tiers:
        tier_idx = REGIME_ORDER.index(tier.max_regime)
        if tier_idx >= regime_idx:
            return tier
    return tiers[-1]  # fallback to most capable


def estimate_cost(model: ModelTier, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost in dollars."""
    return (
        input_tokens * model.input_cost_per_m / 1_000_000
        + output_tokens * model.output_cost_per_m / 1_000_000
    )


# --- Smart Router ---

class KongenRouter:
    """
    Routes prompts to the optimal LLM model using Kongen's pattern analysis.

    Kongen scores each prompt to determine its reasoning complexity (regime),
    then the router picks the cheapest model that handles that regime.

    Example:
        router = KongenRouter(provider="claude")
        response = router.complete("What is 2+2?")
        # → Routes to Haiku (cheapest), saves ~80% vs always using Opus

        response = router.complete("Prove that P != NP")
        # → Routes to Opus (most capable), no savings but correct model
    """

    def __init__(
        self,
        provider: str = "claude",
        kongen_api_key: str | None = None,
        llm_api_key: str | None = None,
    ):
        self.provider = provider
        self.kongen = KongenClient(api_key=kongen_api_key)

        if provider == "claude":
            import anthropic
            self.llm = anthropic.Anthropic(api_key=llm_api_key)
            self.tiers = CLAUDE_TIERS
        elif provider == "openai":
            import openai
            self.llm = openai.OpenAI(api_key=llm_api_key)
            self.tiers = OPENAI_TIERS
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'claude' or 'openai'.")

        self.total_saved = 0.0
        self.total_spent = 0.0
        self.calls = 0

    def complete(
        self,
        prompt: str,
        system: str = "You are a helpful assistant.",
        max_tokens: int | None = None,
    ) -> dict:
        """
        Score prompt with Kongen, route to optimal model, return response.

        Returns dict with: text, model, regime, cost, would_cost, saved
        """
        # 1. Score with Kongen (1 KT)
        score = self.kongen.chiryu.score(prompt)
        regime = score.regime
        recommended = score.recommended_tokens

        # 2. Pick cheapest capable model
        model = pick_model(regime, self.tiers)
        expensive = self.tiers[-1]  # what you'd use without routing

        # 3. Use recommended tokens if no override
        if max_tokens is None:
            max_tokens = min(recommended, 4096)

        # 4. Call the LLM
        if self.provider == "claude":
            response = self.llm.messages.create(
                model=model.name,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
        else:
            response = self.llm.chat.completions.create(
                model=model.name,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            )
            text = response.choices[0].message.content
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens

        # 5. Calculate savings
        actual_cost = estimate_cost(model, input_tokens, output_tokens)
        would_cost = estimate_cost(expensive, input_tokens, output_tokens)
        saved = would_cost - actual_cost

        self.total_spent += actual_cost
        self.total_saved += saved
        self.calls += 1

        return {
            "text": text,
            "model": model.name,
            "regime": regime,
            "boost_factor": score.boost_factor,
            "a_i_ratio": score.a_i_ratio,
            "cost": actual_cost,
            "would_cost": would_cost,
            "saved": saved,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }

    def stats(self) -> dict:
        """Return cumulative routing statistics."""
        return {
            "calls": self.calls,
            "total_spent": round(self.total_spent, 4),
            "total_saved": round(self.total_saved, 4),
            "savings_pct": round(
                self.total_saved / (self.total_spent + self.total_saved) * 100, 1
            ) if (self.total_spent + self.total_saved) > 0 else 0,
        }


# --- Demo ---

if __name__ == "__main__":
    # Pick provider based on which API key is available
    if os.environ.get("ANTHROPIC_API_KEY"):
        provider = "claude"
    elif os.environ.get("OPENAI_API_KEY"):
        provider = "openai"
    else:
        print("Set ANTHROPIC_API_KEY or OPENAI_API_KEY to run the demo.")
        print("Also set KONGEN_API_KEY (get one at https://garden.kongenlabs.life/keys)")
        raise SystemExit(1)

    router = KongenRouter(provider=provider)
    print(f"Kongen Smart Router ({provider})\n{'=' * 50}\n")

    # Mix of simple and complex prompts
    prompts = [
        "What is 2 + 2?",
        "Summarize the key differences between TCP and UDP.",
        "Write a Python function to check if a number is prime.",
        "Explain the implications of Godel's incompleteness theorems on AI.",
        "Prove that the sum of the first n odd numbers equals n squared.",
    ]

    for prompt in prompts:
        result = router.complete(prompt)
        print(f"Prompt: {prompt[:60]}...")
        print(f"  Regime: {result['regime']} -> Model: {result['model']}")
        print(f"  Cost: ${result['cost']:.4f} (would be ${result['would_cost']:.4f}, saved ${result['saved']:.4f})")
        print(f"  Tokens: {result['input_tokens']}in/{result['output_tokens']}out")
        print()

    s = router.stats()
    print(f"{'=' * 50}")
    print(f"Total: {s['calls']} calls, ${s['total_spent']:.4f} spent, ${s['total_saved']:.4f} saved ({s['savings_pct']}%)")
