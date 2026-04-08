#env>pickup_env.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import numpy as np


@dataclass
class Shipment:
    id: int
    manufacturer_id: int
    location_id: int
    ready_time: int
    due_time: int
    volume: float
    priority: int = 1


@dataclass
class Carrier:
    id: int
    reliability: float
    capacity_per_slot: int
    cost_per_km: float
    base_fee: float
    max_daily_capacity: float


class PickupEnv:
    def __init__(self, difficulty: int = 0, seed: Optional[int] = None):
        self.difficulty = difficulty
        self.rng = np.random.RandomState(seed)
        self.time_horizon = 48
        self.current_time = 0

        self.shipments: List[Shipment] = []
        self.carriers: List[Carrier] = []
        self.dist_matrix: Optional[np.ndarray] = None
        self.assignments: List[Dict[str, Any]] = []
        self.total_shipments = 0

    def reset(self) -> Dict[str, Any]:
        self.current_time = 0
        self.shipments = self._generate_shipments()
        self.carriers = self._generate_carriers()
        self.dist_matrix = self._generate_distances()
        self.assignments = []
        self.total_shipments = len(self.shipments)
        return self._get_observation()

    def _generate_shipments(self) -> List[Shipment]:
        if self.difficulty == 0:
            num_manu, num_ship = 1, 8
        elif self.difficulty == 1:
            num_manu, num_ship = 3, 20
        else:
            num_manu, num_ship = 5, 40

        shipments: List[Shipment] = []
        for i in range(num_ship):
            manufacturer_id = int(self.rng.randint(0, num_manu))
            location_id = manufacturer_id
            ready = int(self.rng.randint(0, self.time_horizon // 2))
            due = int(self.rng.randint(ready + 1, min(self.time_horizon, ready + 10)))
            volume = float(self.rng.randint(1, 5))
            priority = int(self.rng.randint(1, 4))
            shipments.append(
                Shipment(
                    id=i,
                    manufacturer_id=manufacturer_id,
                    location_id=location_id,
                    ready_time=ready,
                    due_time=due,
                    volume=volume,
                    priority=priority,
                )
            )
        return shipments

    def _generate_carriers(self) -> List[Carrier]:
        if self.difficulty == 0:
            num_carriers = 2
        elif self.difficulty == 1:
            num_carriers = 3
        else:
            num_carriers = 4

        carriers: List[Carrier] = []
        for cid in range(num_carriers):
            if cid == 0:
                reliability = float(self.rng.uniform(0.90, 0.99))
                cost_per_km = float(self.rng.uniform(8.0, 12.0))
            else:
                reliability = float(self.rng.uniform(0.60, 0.90))
                cost_per_km = float(self.rng.uniform(4.0, 9.0))

            capacity_per_slot = int(self.rng.randint(2, 6))
            base_fee = float(self.rng.uniform(50.0, 150.0))
            max_daily_capacity = float(self.rng.uniform(20.0, 80.0))

            carriers.append(
                Carrier(
                    id=cid,
                    reliability=reliability,
                    capacity_per_slot=capacity_per_slot,
                    cost_per_km=cost_per_km,
                    base_fee=base_fee,
                    max_daily_capacity=max_daily_capacity,
                )
            )
        return carriers

    def _generate_distances(self) -> np.ndarray:
        num_locations = max((s.location_id for s in self.shipments), default=-1) + 1
        n = num_locations + 1  # depot + locations
        d = self.rng.uniform(5.0, 100.0, size=(n, n))
        d = (d + d.T) / 2.0
        np.fill_diagonal(d, 0.0)
        return d

    def _get_observation(self) -> Dict[str, Any]:
        return {
            "time": self.current_time,
            "time_horizon": self.time_horizon,
            "shipments": [
                {
                    "id": s.id,
                    "manufacturer_id": s.manufacturer_id,
                    "location_id": s.location_id,
                    "ready_time": s.ready_time,
                    "due_time": s.due_time,
                    "volume": s.volume,
                    "priority": s.priority,
                }
                for s in self.shipments
            ],
            "carriers": [
                {
                    "id": c.id,
                    "reliability": c.reliability,
                    "capacity_per_slot": c.capacity_per_slot,
                    "cost_per_km": c.cost_per_km,
                    "base_fee": c.base_fee,
                    "max_daily_capacity": c.max_daily_capacity,
                }
                for c in self.carriers
            ],
        }

    def step(self, action: Dict[str, Any]) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        reward = 0.0
        info: Dict[str, Any] = {"valid_action": False}
        done = False

        shipment_id = action.get("shipment_id")
        carrier_id = action.get("carrier_id")

        available_ids = {s.id for s in self.shipments}
        carrier_ids = {c.id for c in self.carriers}

        if shipment_id is None or carrier_id is None:
            ready_exists = any(s.ready_time <= self.current_time <= s.due_time for s in self.shipments)
            if ready_exists:
                reward -= 20.0
        elif shipment_id not in available_ids or carrier_id not in carrier_ids:
            reward -= 50.0
        else:
            shipment = next(s for s in self.shipments if s.id == shipment_id)
            carrier = next(c for c in self.carriers if c.id == carrier_id)
            info["valid_action"] = True

            loc_idx = shipment.location_id + 1
            dist = float(self.dist_matrix[0, loc_idx])

            base_travel_slots = max(1, int(round((dist / 35.0) * 2)))
            noise = float(self.rng.normal(1.0, 0.10 if self.difficulty == 0 else 0.25))
            travel_slots = max(1, int(round(base_travel_slots * noise)))
            arrival_time = self.current_time + travel_slots

            show = bool(self.rng.rand() < carrier.reliability)
            on_time = bool(show and shipment.ready_time <= arrival_time <= shipment.due_time)
            cost = float(carrier.base_fee + carrier.cost_per_km * dist)

            if on_time:
                reward += 100.0
            elif show:
                reward -= 200.0
            else:
                reward -= 500.0

            reward -= 0.1 * cost

            assignment = {
                "shipment_id": shipment.id,
                "carrier_id": carrier.id,
                "arrival_time": arrival_time,
                "show": show,
                "on_time": on_time,
                "cost": cost,
                "manufacturer_id": shipment.manufacturer_id,
            }
            self.assignments.append(assignment)
            self.shipments = [s for s in self.shipments if s.id != shipment.id]
            info["assignment"] = assignment

        self.current_time += 1

        if self.difficulty == 2 and self.rng.rand() < 0.05 and self.current_time < self.time_horizon - 4:
            nid = max([a["shipment_id"] for a in self.assignments] + [s.id for s in self.shipments] + [-1]) + 1
            self.shipments.append(
                Shipment(
                    id=nid,
                    manufacturer_id=int(self.rng.randint(0, 5)),
                    location_id=int(self.rng.randint(0, 5)),
                    ready_time=self.current_time,
                    due_time=min(self.time_horizon - 1, self.current_time + int(self.rng.randint(3, 8))),
                    volume=float(self.rng.randint(1, 5)),
                    priority=int(self.rng.randint(1, 4)),
                )
            )

        done = self.current_time >= self.time_horizon or len(self.shipments) == 0
        info["assignments"] = self.assignments
        info["remaining_shipments"] = len(self.shipments)
        info["total_shipments"] = self.total_shipments

        return self._get_observation(), reward, done, info