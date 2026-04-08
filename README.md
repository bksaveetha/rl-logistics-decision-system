---
title: RL Logistics Decision System
emoji: 🚚
colorFrom: blue
colorTo: indigo
sdk: docker
app_file: streamlit_app.py
pinned: false
---

# Outbound Pickup Reliability - OpenEnv Project

## Problem
Simulate real-world logistics where manufacturers assign carriers to shipments under uncertainty (delays, no-shows, cost trade-offs).

---

## Environment

### Observation Space
- time: current simulation time
- shipments: list of pending shipments
- carriers: available transport providers

### Action Space
- shipment_id: ID of shipment to assign
- carrier_id: ID of carrier

---

## Objective
Maximize:
- on-time delivery
- reliability
- cost efficiency

---

## Reward Function
- +100 → On-time delivery
- -200 → Late delivery
- -500 → Carrier no-show
- -0.1 × cost penalty

---

## Tasks

| Task | Description |
|-----|------------|
| Easy | Single plant, few shipments |
| Medium | Multi-plant |
| Hard | Dynamic arrivals |

---

## Evaluation
Graded using:
- on-time rate
- cost efficiency
- coverage

Score range: 0.0 → 1.0

---

## Baseline Agent
Rule-based:
- selects urgent shipments
- picks most reliable carrier

---

## Automated Mode
Automated Mode = system plays the simulation using a built-in decision logic (baseline agent).  
It simulates dispatcher behavior step-by-step for shipment assignment.

---

## Control Panel
Includes:
- Task Difficulty
- Reset Environment
- Shipment ID
- Carrier ID  

Used to manually test decisions and observe rewards.

---

## Reward System
- Positive reward → successful on-time assignment  
- Negative reward → delay or carrier no-show  

---

## Decision Log
Tracks:
- time
- shipment_id
- carrier_id
- reward
- success (1 = success, 0 = failure)

---

## Run Locally

```bash
pip install -r requirements.txt
uvicorn app:app --port 7860
streamlit run streamlit_app.py