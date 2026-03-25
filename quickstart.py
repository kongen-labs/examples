"""
Kongen Labs — Quickstart (Python)

Score a prompt, check your usage, and see routing recommendations.

    pip install kongenlabs
    export KONGEN_API_KEY="kl_live_..."
    python quickstart.py
"""

from kongen import KongenClient

client = KongenClient()  # reads KONGEN_API_KEY from env

# --- 1. Score a prompt (1 KT) ---
result = client.chiryu.score("Explain quantum entanglement in simple terms")
print(f"Regime:     {result.regime}")
print(f"Boost:      {result.boost_factor}")
print(f"A/I ratio:  {result.a_i_ratio:.3f}")
print(f"Tokens:     {result.recommended_tokens}")
print()

# --- 2. Route based on regime ---
MODEL_MAP = {
    "trivial": "haiku",    # $1/$5 per 1M tokens
    "fast": "haiku",       # $1/$5
    "moderate": "sonnet",  # $3/$15
    "deep": "sonnet",      # $3/$15
    "exhaustive": "opus",  # $5/$25
}
recommended_model = MODEL_MAP.get(result.regime, "sonnet")
print(f"Recommended model: {recommended_model}")
print(f"Max tokens to use: {result.recommended_tokens}")
print()

# --- 3. Transfer scoring (50 KT) ---
from kongen.types import StructuralSignature

sig = StructuralSignature(
    activator_strength=0.72,
    inhibitor_strength=0.65,
    boundary_strength=0.81,
    scale_coherence=0.44,
    field_magnitude=1.56,
    a_i_ratio=1.11,
    gradient_strength=0.39,
)
transfer = client.transfer.score_signal(sig)
print(f"Pattern:    {transfer.classification}")
print(f"Confidence: {transfer.confidence:.3f}")
print(f"Boost:      {transfer.boost_factor:+.3f}")
for ev in transfer.evidence:
    print(f"  {ev['source_domain']}: {ev['pattern_type']} (sim={ev['similarity']:.3f})")
print()

# --- 4. Batch scoring (40 KT per item) ---
signals = [
    StructuralSignature(
        activator_strength=0.3, inhibitor_strength=0.8, boundary_strength=0.6,
        scale_coherence=0.5, field_magnitude=1.1, a_i_ratio=0.38, gradient_strength=0.4,
    ),
    StructuralSignature(
        activator_strength=0.9, inhibitor_strength=0.4, boundary_strength=0.3,
        scale_coherence=0.7, field_magnitude=2.1, a_i_ratio=2.25, gradient_strength=0.6,
    ),
    StructuralSignature(
        activator_strength=0.6, inhibitor_strength=0.6, boundary_strength=0.9,
        scale_coherence=0.5, field_magnitude=1.5, a_i_ratio=1.0, gradient_strength=0.8,
    ),
]
batch = client.transfer.score_batch(signals, source_domain="capital")
for i, r in enumerate(batch.results):
    print(f"Signal {i+1}: {r.classification} (boost={r.boost_factor:+.3f})")
print()

# --- 5. Check token usage ---
print(f"Tokens used this session: {1 + 50 + 40*3} KT")
print("  1 Logic Score + 1 Transfer + 3 Batch items")
