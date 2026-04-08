---
title: RL Logistics Decision System
colorFrom: blue
colorTo: indigo
sdk: docker
app_file: streamlit_app.py
pinned: false
tags:
  - openenv
  - reinforcement-learning
  - logistics
  - decision-intelligence
---

# Outbound Pickup Reliability Environment

This project implements a real-world logistics decision environment using the OpenEnv specification. It simulates outbound pickup scheduling under uncertainty, where an agent assigns carriers to shipments while optimizing reliability, timeliness, and cost.

The environment is designed for reinforcement learning and decision intelligence systems, exposing a Gym-style interface with `reset()`, `step()`, and `state()` APIs.

---

## Overview

In manufacturing logistics, assigning the right carrier to the right shipment is critical. Poor decisions lead to:

- delayed shipments
- carrier no-shows
- increased operational costs

This environment models these uncertainties and allows agents to learn optimal assignment strategies.

Key characteristics:

- stochastic carrier reliability
- time-window constrained shipments
- cost vs reliability trade-offs
- partial observability of outcomes

---

## Environment Design

The environment follows OpenEnv principles with structured state, action, and reward definitions.

### Observation

Each step returns:

- `time`: current simulation time
- `shipments`: list of pending shipments
  - id
  - ready_time
  - due_time
  - priority
- `carriers`: available carriers
  - id
  - reliability
  - cost_per_km
  - base_fee

---

### Action

The agent selects:

- `shipment_id`: shipment to assign
- `carrier_id`: carrier to assign

If no valid action exists:

- `shipment_id = None`
- `carrier_id = None`

---

### Reward Function Ranges(Approximation Values)

The reward is designed to reflect real-world logistics outcomes:

- +100 → successful on-time pickup
- -200 → delayed pickup
- -500 → carrier no-show
- cost penalty → proportional to transport cost

This creates a trade-off between:

- reliability (high success probability)
- cost efficiency (low-cost carriers)
- urgency (shipment deadlines)

---

## Tasks

The environment includes three difficulty levels:

### Easy: Single Plant

- limited shipments
- stable carrier pool
- predictable conditions

### Medium: Multi-Plant

- multiple shipment sources
- increased coordination complexity

### Hard: Dynamic Orders

- new shipments arrive over time
- higher uncertainty
- requires adaptive decision-making

---

## Evaluation

Performance is evaluated using graders:

- on-time delivery rate
- carrier reliability (no-show rate)
- cost efficiency
- shipment coverage

Scores are normalized between:


0.0 → poor performance
1.0 → optimal performance


---

## Baseline Agent

A rule-based baseline agent is provided.

Strategy:

- prioritize earliest due shipments
- select highest reliability carriers
- fallback when no valid assignments exist

The baseline ensures reproducible performance across tasks.

---

## API Specification

The environment implements standard OpenEnv APIs:

### Reset

reset() → observation



Initializes a new episode.

---

### Step

step(action) → observation, reward, done, info


Executes an action and advances simulation.

---

### State

state → internal environment state


Provides additional metadata such as:

- current time
- remaining shipments

---

## Inference Script

The `inference.py` script:

- runs all tasks (easy, medium, hard)
- executes the baseline policy
- logs structured outputs

Log format:

[START] task_id=...
[STEP] step=... action=...
[END] task_id=... score=...


This ensures compatibility with automated evaluation pipelines.

---

## Deployment

The environment is deployed using:

- Docker container
- HuggingFace Spaces

Key characteristics:

- reproducible execution
- isolated environment
- HTTP-compatible interface (optional)

---

## User Interface

A Streamlit-based interface provides:

- task selection (difficulty levels)
- manual decision input
- automated simulation mode
- KPI tracking:
  - total reward
  - success rate
  - decision history

The UI is designed for demonstration and evaluation purposes.

---

## File Structure

pickup_env/
├── env/
│ └── pickup_env.py
├── graders/
│ └── pickup_graders.py
├── streamlit_app.py
├── inference.py
├── app.py
├── openenv.yaml
├── requirements.txt
└── Dockerfile


---

## Running Locally

Install dependencies:

pip install -r requirements.txt


Run the UI:

streamlit run streamlit_app.py


Run inference:

python inference.py


---

## Key Highlights

- Real-world logistics simulation (non-toy problem)
- OpenEnv-compliant environment
- Multi-task evaluation framework
- Deterministic baseline agent
- Interactive decision dashboard
- Fully containerized deployment

---

## Conclusion

This environment provides a practical benchmark for evaluating decision-making agents in logistics systems. It bridges the gap between simulation environments and real-world operational challenges by incorporating uncertainty, constraints, and trade-offs.

It is suitable for:

- reinforcement learning research
- decision intelligence systems
- operations optimization
- benchmarking agent performance

