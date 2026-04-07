"""Organism creation examples -- all three levels.

These examples demonstrate how to use the SDK to build
domain-specific organisms at all three levels of integration.
"""

from kongen import KongenClient


# ===================================================================
# LEVEL 0: Minimal -- raw float arrays
# ===================================================================
# The creator has already computed their own 7 feature values.
# They don't need to understand what each position means beyond
# the generic docs: "slot 0 = primary growth signal", etc.

def level_0_raw():
    """Minimal organism: push 7 floats, get pattern classification."""

    client = KongenClient(api_key="kl_live_...")

    # Register -- just a name and domain
    org = client.organisms.create(
        name="seismic-ryu",
        domain="seismology",
    )
    print(f"Created: {org}")
    # -> Organism(name='seismic-ryu', domain='seismology', level=0, id='org_a1b2c3d4e5f6')

    # Observe with a 7-element float array
    result = org.observe([0.82, 0.15, 0.91, 0.7, 1.8, 5.47, 0.45])

    print(f"Pattern: {result.classification}")    # "pattern_c"
    print(f"Confidence: {result.confidence}")      # 0.89
    print(f"Cross-domain adj: {result.confidence_adj}")  # +0.15
    print(f"Evidence: {len(result.evidence)} domains")    # 3

    # Batch scoring at discount
    readings = [
        [0.82, 0.15, 0.91, 0.7, 1.8, 5.47, 0.45],
        [0.3, 0.6, 0.2, 0.4, 0.67, 0.5, 0.3],
        [0.5, 0.5, 0.75, 0.8, 1.0, 1.0, 0.6],
    ]
    results = org.observe_batch(readings)
    for r in results:
        print(f"  {r.pattern_id}: {r.classification} ({r.confidence:.2f})")

    client.close()


# ===================================================================
# LEVEL 1: Guided -- named fields with semantic roles
# ===================================================================
# The creator describes their domain fields and assigns semantic
# roles. The API handles normalization and mapping automatically.

def level_1_schema():
    """Schema organism: named fields auto-mapped to pattern space."""

    client = KongenClient(api_key="kl_live_...")

    org = client.organisms.create(
        name="weather-ryu",
        domain="meteorology",
        description="Weather pattern intelligence for forecasting",
        schema={
            # Each field gets a semantic role + optional normalization hint
            "temperature": {
                "role": "growth",
                "description": "Surface temperature in Celsius",
                "normalization": "symmetric",     # Can be negative
            },
            "pressure": {
                "role": "constraint",
                "description": "Atmospheric pressure in hPa",
                "normalization": "positive_unbounded",
            },
            "humidity": {
                "role": "boundary",
                "description": "Relative humidity (0-1)",
                "normalization": "zero_to_one",
            },
            "wind_stability": {
                "role": "stability",
                "description": "Wind direction consistency over 6h",
                "normalization": "zero_to_one",
            },
            "pressure_coherence": {
                "role": "coherence",
                "description": "Pressure pattern similarity across altitudes",
                "normalization": "zero_to_one",
            },
        },
    )

    print(f"Created: {org}")
    print(f"Level: {org.level}")           # 1
    print(f"Vector size: {org.vector_size}")  # 5 (number of schema fields)

    # Observe with a dict -- field names match the schema
    result = org.observe({
        "temperature": 28.5,
        "pressure": 1013.25,
        "humidity": 0.65,
        "wind_stability": 0.8,
        "pressure_coherence": 0.72,
    })

    print(f"Pattern: {result.classification}")
    print(f"Confidence: {result.confidence}")

    # The API handles all normalization and mapping internally.
    # You just get pattern classifications and cross-domain evidence.

    # Check health
    health = org.health()
    print(f"Status: {health.status}")
    print(f"Observations: {health.total_observations}")
    print(f"Distribution: {health.classification_distribution}")

    client.close()


# ===================================================================
# LEVEL 2: Full collective -- outcomes + cross-domain feedback
# ===================================================================
# The organism reports outcomes and receives cross-domain analogies.
# This is maximum integration with the pattern collective.

def level_2_full():
    """Full organism: schema + outcomes + analogy feedback."""

    client = KongenClient(api_key="kl_live_...")

    org = client.organisms.create(
        name="supply-ryu",
        domain="logistics",
        description="Supply chain disruption pattern detection",
        schema={
            "demand_growth": {
                "role": "growth",
                "normalization": "positive_unbounded",
                "weight": 1.5,  # Demand is more important
            },
            "supply_constraint": {
                "role": "constraint",
                "normalization": "positive_unbounded",
            },
            "region_boundary": {
                "role": "boundary",
                "description": "How distinct this region is from neighbors",
                "normalization": "zero_to_one",
            },
            "lead_time_stability": {
                "role": "stability",
                "normalization": "ratio",
            },
            "multi_tier_coherence": {
                "role": "coherence",
                "description": "Pattern consistency across supply tiers",
                "normalization": "zero_to_one",
            },
            "disruption_propagation": {
                "role": "diffusion",
                "description": "How fast disruptions spread through network",
                "normalization": "zero_to_one",
            },
        },
        outcomes_enabled=True,
        analogies_webhook="https://my-logistics-api.com/kongen-callback",
    )

    print(f"Level: {org.level}")  # 2

    # Observe
    result = org.observe({
        "demand_growth": 1500,
        "supply_constraint": 800,
        "region_boundary": 0.85,
        "lead_time_stability": 0.3,
        "multi_tier_coherence": 0.6,
        "disruption_propagation": 0.9,
    })

    print(f"Pattern: {result.classification}")
    print(f"Evidence from {len(result.evidence)} domains")

    # Later: report outcome (the disruption prediction was correct)
    outcome = org.report_outcome(
        pattern_id=result.pattern_id,
        success=True,
        magnitude=0.85,
        exit_reason="disruption_confirmed",
    )
    print(f"Outcome accepted: {outcome.accepted}")
    print(f"Transfer impact: {outcome.transfer_impact}")

    # Poll for cross-domain analogies (alternative to webhook)
    analogies = org.get_analogies(limit=10)
    for a in analogies:
        print(
            f"  Analogy: your pattern {a.your_pattern_id} "
            f"matched domain {a.source_domain_id} "
            f"(similarity={a.similarity:.2f}, "
            f"outcome={a.source_outcome}, "
            f"suggested_adj={a.suggested_adj:+.3f})"
        )
        # You see: "domain d3 had a similar pattern that succeeded"
        # Domains are opaque identifiers — you get similarity, not internals

    client.close()


# ===================================================================
# MULTI-FIELD ROLES: multiple fields sharing one semantic role
# ===================================================================

def multi_field_example():
    """When multiple domain features map to the same semantic role."""

    client = KongenClient(api_key="kl_live_...")

    org = client.organisms.create(
        name="biotech-ryu",
        domain="bioprocess",
        schema={
            # Two growth fields: their weighted average becomes the growth signal
            "cell_density": {
                "role": "growth",
                "weight": 2.0,              # More important
                "normalization": "positive_unbounded",
            },
            "nutrient_uptake": {
                "role": "growth",
                "weight": 1.0,
                "normalization": "positive_unbounded",
            },
            # Two constraint fields
            "ph_deviation": {
                "role": "constraint",
                "weight": 1.5,
                "normalization": "symmetric",
            },
            "temperature_deviation": {
                "role": "constraint",
                "weight": 1.0,
                "normalization": "symmetric",
            },
            # Single fields for other roles
            "batch_phase_sharpness": {
                "role": "boundary",
                "normalization": "zero_to_one",
            },
            "yield_consistency": {
                "role": "stability",
                "normalization": "ratio",
            },
        },
    )

    result = org.observe({
        "cell_density": 2.5e6,
        "nutrient_uptake": 340.0,
        "ph_deviation": -0.3,
        "temperature_deviation": 1.2,
        "batch_phase_sharpness": 0.88,
        "yield_consistency": 0.76,
    })

    # cell_density (w=2.0) and nutrient_uptake (w=1.0) are averaged
    # into a single "growth" signal with 2:1 weighting.

    print(f"Pattern: {result.classification}")
    print(f"Confidence: {result.confidence}")

    client.close()


if __name__ == "__main__":
    print("=== Level 0: Raw ===")
    # level_0_raw()

    print("\n=== Level 1: Schema ===")
    # level_1_schema()

    print("\n=== Level 2: Full ===")
    # level_2_full()

    print("\n=== Multi-field ===")
    # multi_field_example()

    print("\n(Uncomment function calls to run with a live API key)")
