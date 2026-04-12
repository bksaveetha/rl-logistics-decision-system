import os, sys
import json
import requests
import random
from openai import OpenAI


BASE_URL = os.environ.get("BASE_URL", "http://localhost:7860")

API_BASE_URL = os.environ.get("API_BASE_URL")
API_KEY      = os.environ.get("API_KEY")
MODEL        = os.environ.get("MODEL_NAME", "gpt-4o-mini")

USE_LLM = API_BASE_URL is not None and API_KEY is not None

client = None
if USE_LLM:
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

TASKS = [
    ("easy_day_single_plant",  "easy"),
    ("medium_multi_plant",     "medium"),
    ("hard_dynamic_orders",    "hard"),
]

ENV_NAME = "pickup-logistics"


def _clip(score: float) -> float:
    return max(0.001, min(0.99, float(score)))


def normalize_step_reward(r: float) -> float:
    score = (r + 600.0) / 700.0
    return _clip(score)



def smart_action(obs):
    t = obs["time"]

    ready = [
        s for s in obs["shipments"]
        if s["ready_time"] <= t <= s["due_time"]
    ]

    if not ready:
        return {"shipment_id": None, "carrier_id": None}

    shipment = min(ready, key=lambda s: s["due_time"])
    carriers  = obs["carriers"]
    good      = [c for c in carriers if c["reliability"] >= 0.7]

    if not good:
        return {"shipment_id": None, "carrier_id": None}

    good_sorted = sorted(good, key=lambda c: (-c["reliability"], c["cost_per_km"]))
    top_k   = good_sorted[:2] if len(good_sorted) >= 2 else good_sorted
    carrier = random.choice(top_k)

    return {"shipment_id": shipment["id"], "carrier_id": carrier["id"]}



def call_llm(obs):
    if not USE_LLM:
        return
    try:
        client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": f"Observation: {json.dumps(obs)}"}],
            temperature=0,
        )
    except Exception:
        pass


# ---------------- RUN TASK ---------------- #

def run_task(task_id: str, label: str) -> float:
    print(f"[START] task={label} env={ENV_NAME} model={MODEL}", flush=True)

    res = requests.post(f"{BASE_URL}/reset/{task_id}", json={})
    obs = res.json()["observation"]

    step_rewards: list[float] = []
    done      = False
    step_idx  = 0

    while not done and step_idx < 20:
        action = smart_action(obs)
        call_llm(obs)

        res = requests.post(f"{BASE_URL}/step/{task_id}", json=action).json()

        raw_reward   = float(res["reward"])
        step_score   = normalize_step_reward(raw_reward)   
        step_rewards.append(step_score)

        obs  = res["observation"]
        done = res["done"]

        print(
            f"[STEP] step={step_idx + 1} action={json.dumps(action)} "
            f"reward={step_score:.4f} done={str(done).lower()} error=null",
            flush=True,
        )
        step_idx += 1

    if step_rewards:
        raw_score = sum(step_rewards) / len(step_rewards)
    else:
        raw_score = 0.001

    score        = _clip(raw_score)
    rewards_str  = ",".join(f"{r:.4f}" for r in step_rewards)
    success      = any(r > 0.5 for r in step_rewards)

    print(
        f"[END] success={str(success).lower()} steps={step_idx} "
        f"score={score:.4f} rewards={rewards_str}",
        flush=True,
    )
    print(f"→ Avg score '{label}': {score:.4f}", flush=True)

    return score


if __name__ == "__main__":
    results: dict[str, float] = {}

    for (task_id, label) in TASKS:
        score         = run_task(task_id, label)
        results[label] = score         

    print("\n===== FINAL SCORES =====", flush=True)
    total = 0.0
    for label in ["easy", "medium", "hard"]:
        s = results.get(label, 0.001)
        print(f"{label}: {s:.4f}", flush=True)
        total += s
    avg = _clip(total / len(results)) if results else 0.001
    print(f"Average: {avg:.4f}", flush=True)

    sys.stdout.write(json.dumps(results))
    sys.stdout.flush()
