import streamlit as st
import pandas as pd
import time
from typing import Dict, Any
from env.pickup_env import PickupEnv


st.set_page_config(page_title="Pickup Logistics Decision System", layout="wide")

st.title("Pickup Logistics Decision System")
st.markdown("Factory pickup scheduling under uncertainty using intelligent decision support.")

# ================= SIDEBAR =================
st.sidebar.header("Control Panel")

task_id = st.sidebar.selectbox(
    "Task Difficulty",
    ["easy_day_single_plant", "medium_multi_plant", "hard_dynamic_orders"]
)

difficulty_map = {
    "easy_day_single_plant": 0,
    "medium_multi_plant": 1,
    "hard_dynamic_orders": 2
}

if st.sidebar.button("Reset Environment"):
    st.session_state.reset_clicked = True

col1, col2 = st.sidebar.columns(2)
shipment_id = col1.number_input("Shipment ID", min_value=-1, value=-1)
carrier_id = col2.number_input("Carrier ID", min_value=-1, value=-1)

if st.sidebar.button("Execute Decision"):
    st.session_state.step_clicked = True

auto_play = st.sidebar.checkbox("Automated Mode")
step_delay = st.sidebar.slider("Step delay", 0.5, 3.0, 1.0)

# ================= SESSION STATE =================
if "env" not in st.session_state:
    st.session_state.env = None
if "env_state" not in st.session_state:
    st.session_state.env_state = None
if "history" not in st.session_state:
    st.session_state.history = []
if "total_reward" not in st.session_state:
    st.session_state.total_reward = 0.0
if "done" not in st.session_state:
    st.session_state.done = False
if "reset_clicked" not in st.session_state:
    st.session_state.reset_clicked = False
if "step_clicked" not in st.session_state:
    st.session_state.step_clicked = False

# ================= RESET =================
if st.session_state.reset_clicked:
    env = PickupEnv(difficulty=difficulty_map[task_id], seed=42)
    obs = env.reset()

    st.session_state.env = env
    st.session_state.env_state = obs
    st.session_state.history = []
    st.session_state.total_reward = 0.0
    st.session_state.done = False
    st.session_state.reset_clicked = False

# ================= SMART RECOMMENDATION =================
def smart_recommendation(obs):
    t = obs["time"]
    best = None
    best_score = -1e9

    for s in obs["shipments"]:
        if not (s["ready_time"] <= t <= s["due_time"]):
            continue
        for c in obs["carriers"]:
            score = c["reliability"] * 100 - c["cost_per_km"] * 50
            if score > best_score:
                best_score = score
                best = (s, c)
    return best

# ================= AUTO MODE =================
if auto_play and st.session_state.env_state and not st.session_state.done:

    def baseline_agent(obs):
        t = obs["time"]
        ready = [s for s in obs["shipments"] if s["ready_time"] <= t <= s["due_time"]]
        if not ready:
            return {"shipment_id": None, "carrier_id": None}

        shipment = min(ready, key=lambda s: s["due_time"])
        carrier = max(obs["carriers"], key=lambda c: c["reliability"])

        return {"shipment_id": shipment["id"], "carrier_id": carrier["id"]}

    action = baseline_agent(st.session_state.env_state)

    obs, reward, done, _ = st.session_state.env.step(action)

    st.session_state.env_state = obs
    st.session_state.total_reward += reward

    st.session_state.history.append({
        "time": obs["time"],
        "shipment_id": action["shipment_id"],
        "carrier_id": action["carrier_id"],
        "reward": reward,
        "success": 1 if reward > 0 else 0
    })

    st.session_state.done = done

    time.sleep(step_delay)
    st.rerun()

# ================= MANUAL STEP =================
if st.session_state.step_clicked and st.session_state.env_state and not st.session_state.done:

    action = {"shipment_id": shipment_id, "carrier_id": carrier_id}

    obs, reward, done, _ = st.session_state.env.step(action)

    st.session_state.env_state = obs
    st.session_state.total_reward += reward

    st.session_state.history.append({
        "time": obs["time"],
        "shipment_id": action["shipment_id"],
        "carrier_id": action["carrier_id"],
        "reward": reward,
        "success": 1 if reward > 0 else 0
    })

    st.session_state.done = done
    st.session_state.step_clicked = False

# ================= MAIN =================
if st.session_state.env_state:
    obs = st.session_state.env_state

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Time", obs["time"])
    col2.metric("Pending Shipments", len(obs["shipments"]))
    col3.metric("Total Reward", f"{st.session_state.total_reward:.1f}")
    col4.metric("Status", "Complete" if st.session_state.done else "In Progress")

    if st.session_state.history:
        last_reward = st.session_state.history[-1]["reward"]
        success_rate = sum(r["success"] for r in st.session_state.history) / len(st.session_state.history) * 100

        c1, c2, _, _ = st.columns(4)
        c1.metric("Last Decision Reward", f"{last_reward:.1f}")
        c2.metric("Success Rate", f"{success_rate:.1f}%")

    rec = smart_recommendation(obs)
    if rec:
        s, c = rec
        st.info(f"Recommended Action: Carrier {c['id']} → Shipment {s['id']}")

    st.subheader("Shipments")
    df_s = pd.DataFrame(obs["shipments"])
    st.dataframe(df_s, use_container_width=True)

    st.subheader("Carriers")
    df_c = pd.DataFrame(obs["carriers"])
    st.dataframe(df_c, use_container_width=True)

    if st.session_state.history:
        st.subheader("Decision Log")
        st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)

else:
    st.info("Click 'Reset Environment' to start")

st.markdown("---")
st.markdown("Outbound Pickup Reliability Benchmark | Decision Intelligence System")