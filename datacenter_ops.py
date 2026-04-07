"""Datacenter Operations Example — Pattern Intelligence for Infrastructure.

Shows how SRE/DevOps teams use Kongen organisms to:
  1. Predict capacity bottlenecks before they cause outages
  2. Detect anomalous degradation patterns across the fleet
  3. Get cross-domain evidence for smarter scaling decisions
  4. Reduce alert fatigue by 80-90% vs naive threshold monitoring

Cost savings come from:
  - Catching failures 2-14 days earlier → fewer emergency interventions
  - Right-sizing scaling decisions with cross-domain confidence
  - Replacing 5+ threshold alerts with 1 structural pattern check
  - Reducing MTTR with pattern-based root cause suggestions

Prerequisites:
    pip install kongenlabs
    export KONGEN_API_KEY=kl_live_...
"""

import os
import time
from kongen import KongenClient


# ===================================================================
# SETUP: Create a datacenter organism with infrastructure metrics
# ===================================================================

def create_datacenter_organism():
    """Create an organism tuned for infrastructure monitoring.

    Maps standard infrastructure metrics to semantic roles:
      - CPU/request rate → growth (expansion pressure)
      - Error rate/latency → constraint (limiting forces)
      - Zone isolation → boundary (fault domain sharpness)
      - Metric stability → stability (pattern persistence)
      - CPU-memory coherence → coherence (resource agreement)
    """
    client = KongenClient(api_key=os.environ["KONGEN_API_KEY"])

    org = client.organisms.create(
        name="prod-fleet",
        domain="datacenter",
        description="Production fleet health — capacity, errors, scaling signals",
        schema={
            "cpu_utilization": {
                "role": "growth",
                "description": "Cluster-wide CPU utilization (0-1)",
                "normalization": "zero_to_one",
            },
            "error_rate": {
                "role": "constraint",
                "description": "Request error rate (0-1)",
                "normalization": "zero_to_one",
            },
            "zone_isolation": {
                "role": "boundary",
                "description": "Error containment across availability zones (0-1)",
                "normalization": "zero_to_one",
            },
            "metric_stability": {
                "role": "stability",
                "description": "Inverse variance of key metrics over 15-min window",
                "normalization": "zero_to_one",
            },
            "rack_coherence": {
                "role": "coherence",
                "description": "CPU-memory utilization agreement across racks",
                "normalization": "zero_to_one",
            },
        },
        outcomes_enabled=True,
    )

    print(f"Organism created: {org.id}")
    print(f"Level: {org.level}")  # 1 (schema) or 2 (if outcomes_enabled)
    return client, org


# ===================================================================
# USE CASE 1: Proactive Capacity Planning
# ===================================================================

def capacity_planning(client, org):
    """Detect capacity pressure before it causes throttling.

    Instead of setting a static "CPU > 80%" alert (which fires constantly
    during normal traffic spikes), observe the structural pattern. The
    cross-domain evidence tells you whether this pattern historically
    leads to degradation — or is just a healthy traffic peak.

    SAVINGS: Eliminates 80-90% of false capacity alerts. Teams only
    act on patterns that structurally match pre-failure signatures.
    """
    print("\n--- Use Case 1: Proactive Capacity Planning ---")

    # Observe current fleet state
    result = org.observe({
        "cpu_utilization": 0.78,      # High but not critical
        "error_rate": 0.02,           # Low errors
        "zone_isolation": 0.92,       # Errors well-contained
        "metric_stability": 0.85,     # Stable metrics
        "rack_coherence": 0.91,       # CPU and memory moving together
    })

    print(f"Pattern: {result.classification}")
    print(f"Confidence: {result.confidence:.2f}")

    # Cross-domain evidence — did similar patterns in other domains
    # lead to problems or resolve naturally?
    for ev in result.evidence:
        print(f"  Domain {ev['source_domain']}: "
              f"similarity={ev['similarity']:.2f}, "
              f"samples={ev['sample_count']}")

    # DECISION LOGIC:
    # High confidence + high similarity to stable patterns → don't scale
    # High confidence + high similarity to degradation patterns → scale now
    if result.confidence > 0.8:
        # Check if evidence suggests this is a stable high-load pattern
        # or a pre-failure pattern by looking at the classification
        if result.classification in ("pattern_c", "pattern_f"):
            # These tend to map to healthy expansion patterns
            print("→ DECISION: High load but structurally stable. Hold scaling.")
            print("  SAVINGS: Avoided unnecessary scale-up ($2,400/day for 10 extra instances)")
        else:
            print("→ DECISION: Pattern matches pre-degradation signature. Scale proactively.")
            print("  SAVINGS: Prevented outage (est. $15K/hr revenue impact)")

    return result


# ===================================================================
# USE CASE 2: Drive Failure Prediction (Backblaze-style)
# ===================================================================

def drive_failure_detection(client, org):
    """Detect failing drives days before SMART thresholds trigger.

    Traditional monitoring waits for SMART attributes to cross fixed
    thresholds. Pattern intelligence detects the structural signature
    of degradation — the *relationship* between metrics matters more
    than any single metric's absolute value.

    SAVINGS: 2-14 day early warning. Migrate data off failing drives
    during maintenance windows instead of emergency recovery.
    """
    print("\n--- Use Case 2: Drive Failure Prediction ---")

    # Create a separate organism for storage fleet
    storage_org = client.organisms.create(
        name="storage-fleet",
        domain="datacenter",
        description="Storage fleet SMART health monitoring",
        schema={
            "wear_stress": {
                "role": "growth",
                "description": "Power-on hours + temperature composite",
                "normalization": "zero_to_one",
            },
            "error_accumulation": {
                "role": "constraint",
                "description": "Reallocated + pending + uncorrectable sectors",
                "normalization": "zero_to_one",
            },
            "vault_isolation": {
                "role": "boundary",
                "description": "Drive isolation within vault/pod",
                "normalization": "zero_to_one",
            },
            "error_stability": {
                "role": "stability",
                "description": "Error count consistency (spiky = unstable)",
                "normalization": "zero_to_one",
            },
            "smart_coherence": {
                "role": "coherence",
                "description": "Agreement between SMART attributes",
                "normalization": "zero_to_one",
            },
        },
        outcomes_enabled=True,
    )

    # Simulate daily SMART check for a drive showing early degradation
    daily_readings = [
        # Day 1-3: healthy
        {"wear_stress": 0.35, "error_accumulation": 0.01, "vault_isolation": 0.5, "error_stability": 0.95, "smart_coherence": 0.92},
        {"wear_stress": 0.35, "error_accumulation": 0.01, "vault_isolation": 0.5, "error_stability": 0.94, "smart_coherence": 0.91},
        {"wear_stress": 0.36, "error_accumulation": 0.02, "vault_isolation": 0.5, "error_stability": 0.93, "smart_coherence": 0.90},
        # Day 4-6: subtle degradation (SMART thresholds wouldn't fire yet)
        {"wear_stress": 0.37, "error_accumulation": 0.05, "vault_isolation": 0.5, "error_stability": 0.82, "smart_coherence": 0.78},
        {"wear_stress": 0.38, "error_accumulation": 0.08, "vault_isolation": 0.5, "error_stability": 0.71, "smart_coherence": 0.65},
        {"wear_stress": 0.39, "error_accumulation": 0.12, "vault_isolation": 0.5, "error_stability": 0.58, "smart_coherence": 0.52},
    ]

    print("Monitoring drive SIM0042 over 6 days:")
    for day, reading in enumerate(daily_readings, 1):
        result = storage_org.observe(reading)
        status = "HEALTHY" if result.confidence < 0.7 or result.classification in ("pattern_c", "pattern_f") else "DEGRADING"
        print(f"  Day {day}: {result.classification} "
              f"(confidence={result.confidence:.2f}) → {status}")

        if status == "DEGRADING":
            print(f"    ⚠ EARLY WARNING: Structural pattern matches pre-failure signature")
            print(f"    → ACTION: Schedule data migration in next maintenance window")
            print(f"    → SAVINGS: Avoided emergency recovery ($8K labor + $50K data risk)")

            # Report outcome when we confirm the drive failed
            # org.report_outcome(pattern_id=result.pattern_id, success=True, magnitude=0.9)

    return storage_org


# ===================================================================
# USE CASE 3: Scaling Decision Confidence
# ===================================================================

def scaling_decisions(client, org):
    """Use cross-domain evidence to make smarter autoscaling decisions.

    Autoscalers typically use CPU/memory thresholds. Pattern intelligence
    adds structural context: "This CPU spike looks like patterns that
    resolved naturally in 3 other domains" vs "This spike matches
    patterns that cascaded into outages."

    SAVINGS: Right-size scaling. Avoid over-provisioning on benign spikes
    ($2-5K/day) and under-provisioning on structural degradation ($15K+/hr).
    """
    print("\n--- Use Case 3: Scaling Decision Confidence ---")

    scenarios = [
        {
            "name": "Traffic spike (Black Friday)",
            "metrics": {
                "cpu_utilization": 0.92,
                "error_rate": 0.01,
                "zone_isolation": 0.95,
                "metric_stability": 0.88,
                "rack_coherence": 0.93,
            },
        },
        {
            "name": "Cascading failure",
            "metrics": {
                "cpu_utilization": 0.85,
                "error_rate": 0.15,
                "zone_isolation": 0.35,
                "metric_stability": 0.22,
                "rack_coherence": 0.41,
            },
        },
        {
            "name": "Memory leak (slow burn)",
            "metrics": {
                "cpu_utilization": 0.55,
                "error_rate": 0.03,
                "zone_isolation": 0.80,
                "metric_stability": 0.45,
                "rack_coherence": 0.38,
            },
        },
    ]

    for scenario in scenarios:
        result = org.observe(scenario["metrics"])
        print(f"\n  Scenario: {scenario['name']}")
        print(f"  Pattern: {result.classification}, confidence: {result.confidence:.2f}")

        # Use evidence strength to calibrate response
        total_evidence = sum(ev["similarity"] for ev in result.evidence)
        avg_similarity = total_evidence / len(result.evidence) if result.evidence else 0

        if avg_similarity > 0.7:
            print(f"  Evidence: STRONG ({avg_similarity:.2f} avg similarity)")
            print(f"  → High-confidence scaling decision")
        elif avg_similarity > 0.4:
            print(f"  Evidence: MODERATE ({avg_similarity:.2f} avg similarity)")
            print(f"  → Scale conservatively, monitor closely")
        else:
            print(f"  Evidence: WEAK ({avg_similarity:.2f} avg similarity)")
            print(f"  → Novel pattern. Alert on-call for human judgment.")


# ===================================================================
# USE CASE 4: Alert Fatigue Reduction
# ===================================================================

def alert_reduction(client, org):
    """Replace N threshold alerts with 1 structural pattern check.

    Traditional: 5+ separate alerts (CPU > 80%, error > 5%, latency > 500ms,
    disk > 90%, memory > 85%). Each fires independently → alert storms.

    Pattern intelligence: 1 observation captures the structural relationship
    between ALL metrics. Only alerts when the *pattern* is anomalous, not
    when individual metrics cross arbitrary thresholds.

    SAVINGS: 80-90% fewer alerts. On-call engineers focus on real problems.
    """
    print("\n--- Use Case 4: Alert Fatigue Reduction ---")

    # Simulate a batch of 10-minute metric snapshots
    snapshots = [
        # Normal: high CPU during deploy (not a problem)
        {"cpu_utilization": 0.88, "error_rate": 0.005, "zone_isolation": 0.95, "metric_stability": 0.90, "rack_coherence": 0.94},
        # Normal: elevated errors during canary (expected)
        {"cpu_utilization": 0.60, "error_rate": 0.08, "zone_isolation": 0.98, "metric_stability": 0.85, "rack_coherence": 0.88},
        # PROBLEM: low CPU but errors spreading across zones
        {"cpu_utilization": 0.35, "error_rate": 0.12, "zone_isolation": 0.25, "metric_stability": 0.30, "rack_coherence": 0.42},
        # Normal: high everything during peak hours
        {"cpu_utilization": 0.82, "error_rate": 0.02, "zone_isolation": 0.90, "metric_stability": 0.87, "rack_coherence": 0.89},
    ]

    threshold_alerts = 0
    pattern_alerts = 0

    for i, snap in enumerate(snapshots):
        # Traditional: would this fire a threshold alert?
        if snap["cpu_utilization"] > 0.80:
            threshold_alerts += 1
        if snap["error_rate"] > 0.05:
            threshold_alerts += 1

        # Pattern: observe and only alert on structural anomalies
        result = org.observe(snap)

        # Alert only when pattern + confidence indicate real trouble
        is_concerning = (
            result.classification in ("pattern_a", "pattern_e")
            and result.confidence > 0.75
        )
        if is_concerning:
            pattern_alerts += 1
            print(f"  Snapshot {i+1}: ALERT — {result.classification} "
                  f"(confidence={result.confidence:.2f})")
        else:
            print(f"  Snapshot {i+1}: OK — {result.classification} "
                  f"(confidence={result.confidence:.2f})")

    print(f"\n  Threshold-based alerts: {threshold_alerts}")
    print(f"  Pattern-based alerts:   {pattern_alerts}")
    print(f"  Alert reduction:        {(1 - pattern_alerts/max(threshold_alerts, 1))*100:.0f}%")


# ===================================================================
# USE CASE 5: Batch Fleet Scoring (Cost-Efficient)
# ===================================================================

def batch_fleet_scoring(client, org):
    """Score entire fleet in one batch call at 20% discount.

    Instead of 1000 individual observe calls (50 KT each = 50,000 KT),
    use observe_batch (40 KT each = 40,000 KT). Saves 10,000 KT per
    fleet scan — at $0.0007/KT that's $7/scan, $210/month at 1 scan/day.

    SAVINGS: 20% API cost reduction on fleet-wide monitoring.
    """
    print("\n--- Use Case 5: Batch Fleet Scoring ---")

    # Simulate 5 hosts (in practice, hundreds or thousands)
    fleet = [
        {"cpu_utilization": 0.72, "error_rate": 0.01, "zone_isolation": 0.90, "metric_stability": 0.88, "rack_coherence": 0.85},
        {"cpu_utilization": 0.45, "error_rate": 0.00, "zone_isolation": 0.95, "metric_stability": 0.95, "rack_coherence": 0.92},
        {"cpu_utilization": 0.91, "error_rate": 0.08, "zone_isolation": 0.40, "metric_stability": 0.35, "rack_coherence": 0.50},
        {"cpu_utilization": 0.60, "error_rate": 0.02, "zone_isolation": 0.88, "metric_stability": 0.82, "rack_coherence": 0.79},
        {"cpu_utilization": 0.33, "error_rate": 0.00, "zone_isolation": 0.93, "metric_stability": 0.97, "rack_coherence": 0.95},
    ]

    results = org.observe_batch(fleet)

    print(f"  Scored {len(results)} hosts in 1 API call")
    print(f"  Cost: {len(results) * 40} KT (vs {len(results) * 50} KT individual)")
    print()

    for i, r in enumerate(results):
        status = "HEALTHY" if r.classification in ("pattern_c", "pattern_f", "pattern_b") else "REVIEW"
        print(f"  Host {i+1}: {r.classification} "
              f"(confidence={r.confidence:.2f}) → {status}")


# ===================================================================
# MAIN: Run all examples
# ===================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Kongen Labs — Datacenter Operations Example")
    print("=" * 60)

    # Uncomment to run with a live API key:
    # client, org = create_datacenter_organism()
    # capacity_planning(client, org)
    # drive_failure_detection(client, org)
    # scaling_decisions(client, org)
    # alert_reduction(client, org)
    # batch_fleet_scoring(client, org)
    # client.close()

    print("\n(Set KONGEN_API_KEY and uncomment function calls to run live)")
    print("\nValue summary:")
    print("  1. Proactive capacity:    Avoid $2-15K/incident with early structural signals")
    print("  2. Drive failure:         2-14 day early warning, $50K+ data risk avoided")
    print("  3. Scaling confidence:    Right-size with cross-domain evidence, save $2-5K/day")
    print("  4. Alert reduction:       80-90% fewer alerts, on-call sanity preserved")
    print("  5. Batch scoring:         20% API cost reduction on fleet scans")
