import argparse, json, random
from datetime import datetime, timezone, timedelta
from pathlib import Path

CATALOG = json.loads((Path(__file__).with_name("scenarios.json")).read_text())

def generate(scenario, seed):
    if scenario not in CATALOG:
        raise ValueError(f"scenario not allowed: {scenario}")
    rng = random.Random(seed)
    spec = CATALOG[scenario]
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(spec["count"]):
        yield {
            "schema_version": "1.0", "event_id": f"demo-{seed}-{i:04d}",
            "timestamp_utc": (base + timedelta(seconds=i)).isoformat(),
            "tenant_id": "demo-tenant", "site_id": "demo-site", "device_id": spec["device_id"],
            "source": "synthetic-simulator", "is_demo": True, "src_ip": f"198.51.100.{rng.randint(1, 20)}",
            "src_port": 40000 + i, "dst_ip": "192.0.2.10", "dst_port": 443, "protocol": "TCP",
            "direction": "egress", "event_type": spec["event_type"],
            "evidence": [f"synthetic {scenario} event {i + 1}"], "severity": spec["severity"],
            "model_version": "none", "policy_version": "baseline"
        }

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--scenario", required=True); p.add_argument("--seed", type=int, required=True); p.add_argument("--output", required=True)
    a = p.parse_args(); out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in generate(a.scenario, a.seed)))
    print(f"generated {CATALOG[a.scenario]['count']} demo events: {out}")
