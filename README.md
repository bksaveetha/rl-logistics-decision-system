#  Outbound Pickup Reliability - OpenEnv Project

## Problem
Simulate real-world logistics where manufacturers assign carriers to shipments under uncertainty (delays, no-shows, cost trade-offs).

---

##  Environment

### Observation Space
- time: current simulation time
- shipments: list of pending shipments
- carriers: available transport providers

### Action Space
- shipment_id: ID of shipment to assign
- carrier_id: ID of carrier

---

##  Objective
Maximize:
- on-time delivery
- reliability
- cost efficiency

---

##  Reward Function
- +100 → On-time delivery
- -200 → Late delivery
- -500 → Carrier no-show
- -0.1 × cost penalty

---

##  Tasks

| Task | Description |
|-----|------------|
| Easy | Single plant, few shipments |
| Medium | Multi-plant |
| Hard | Dynamic arrivals |

---

##  Evaluation
Graded using:
- on-time rate
- cost efficiency
- coverage

Score range: 0.0 → 1.0

---

##  Baseline Agent
Rule-based:
- selects urgent shipments
- picks most reliable carrier



## Automated mode
Automated Mode = system plays the simulation for you using a built-in decision logic (baseline agent)
Automated Mode = “Auto decision-making system that simulates a dispatcher choosing shipments and carriers step-by-step, It can show as end to end demo of Shipment allotment to the carrier assignment”

## Control Panel
In control panel we have "Task Difficulty", "Reset Environment", "Shipment-id", "Carrier-id" which is has unlimitet input which eventually decides the positive and negative reward according to the shipment and carrier status.

## Reward System
The action taken on the recommendation basis, So if sometime if priority shipment is alloted then in that case to it can show as the negative/positve reward basis on the carrier shows up or not, if they shows then it will be positve reward, if delayed/did not show up then it will be negative reward marking.

## Decision log
You can find the time, shipment id, carrier id, reward, success, The major clarity on the success column where you can see 1 signifies and 0 signifies as unsuccessful.
## ▶ Run Locally

```bash
pip install -r requirements.txt
uvicorn app:app --port 7860 or uvicorn app:app --reload --host 0.0.0.0 --port 7860
streamlit run streamlit_app.py