from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from env.pickup_env import PickupEnv

app = FastAPI(title="Pickup OpenEnv API")

envs: Dict[str, PickupEnv] = {}

class ActionModel(BaseModel):
    shipment_id: Optional[int] = None
    carrier_id: Optional[int] = None

def difficulty_from_task(task_id: str) -> int:
    if "hard" in task_id:
        return 2
    if "medium" in task_id:
        return 1
    return 0

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/reset/{task_id}")
def reset(task_id: str):
    env = PickupEnv(difficulty=difficulty_from_task(task_id), seed=42)
    envs[task_id] = env
    return {"observation": env.reset()}

@app.post("/step/{task_id}")
def step(task_id: str, action: ActionModel):
    if task_id not in envs:
        raise HTTPException(status_code=404, detail="Task not initialized")

    obs, reward, done, info = envs[task_id].step(action.model_dump())

    return {
        "observation": obs,
        "reward": reward,
        "done": done,
        "info": info
    }

@app.get("/state/{task_id}")
def state(task_id: str):
    if task_id not in envs:
        raise HTTPException(status_code=404, detail="Task not initialized")

    env = envs[task_id]

    return {
        "time": env.current_time,
        "remaining_shipments": len(env.shipments)
    }