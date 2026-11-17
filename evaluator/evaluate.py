import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from agents.blue.analyze import analyze

def evaluate(path):
    events = [json.loads(x) for x in Path(path).read_text().splitlines() if x.strip()]
    results = [analyze(e) for e in events]
    return {"event_count": len(events), "detected_count": sum(r["detected"] for r in results), "results": results, "is_demo": True}

if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("--input", required=True); p.add_argument("--output", required=True); a = p.parse_args()
    Path(a.output).write_text(json.dumps(evaluate(a.input), ensure_ascii=False, indent=2)); print(f"wrote {a.output}")
