# inference.py
import json, os
from env.pickup_env import PickupEnv
from graders.pickup_graders import grade_easy, grade_medium, grade_hard

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "baseline")
HF_TOKEN = os.getenv("HF_TOKEN", "dummy")

def choose_action(obs):
    t = obs["time"]
    ready = [s for s in obs["shipments"] if s["ready_time"] <= t <= s["due_time"]]
    if not ready:
        return {"shipment_id": None, "carrier_id": None}
    shipment = min(ready, key=lambda s: (s["due_time"], -s["priority"]))
    carriers = sorted(
        obs["carriers"],
        key=lambda c: (-c["reliability"], c["cost_per_km"], c["base_fee"])
    )
    carrier = carriers[0]
    return {"shipment_id": shipment["id"], "carrier_id": carrier["id"]}

def run(task_id, difficulty):
    env = PickupEnv(difficulty=difficulty, seed=42)
    obs = env.reset()
    print(f"[START] task_id={task_id}", flush=True)

    done = False
    step_idx = 0
    info = {}
    while not done:
        action = choose_action(obs)
        print(f"[STEP] step={step_idx} action={json.dumps(action)}", flush=True)
        obs, reward, done, info = env.step(action)
        step_idx += 1

    episode_info = {
        "assignments": info["assignments"],
        "total_shipments": info["total_shipments"],
    }
    score = {
        0: grade_easy,
        1: grade_medium,
        2: grade_hard,
    }[difficulty](episode_info)

    print(f"[END] task_id={task_id} score={score}", flush=True)
    return score

if __name__ == "__main__":
    results = {
        "easy_day_single_plant": run("easy_day_single_plant", 0),
        "medium_multi_plant": run("medium_multi_plant", 1),
        "hard_dynamic_orders": run("hard_dynamic_orders", 2),
    }
    print(json.dumps(results))