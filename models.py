from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Action(BaseModel):
    shipment_id: Optional[int] = None
    carrier_id: Optional[int] = None

class Observation(BaseModel):
    time: int
    shipments: List[Dict[str, Any]]
    carriers: List[Dict[str, Any]]