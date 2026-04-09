from typing import Any, Dict
import requests

class PickupEnvClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def reset(self, task_id="easy_day_single_plant"):
        return requests.post(f"{self.base_url}/reset/{task_id}").json()

    def step(self, task_id: str, action: Dict[str, Any]):
        return requests.post(f"{self.base_url}/step/{task_id}", json=action).json()