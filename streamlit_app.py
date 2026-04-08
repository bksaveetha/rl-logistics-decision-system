import streamlit as st
import requests
import pandas as pd
from typing import Dict, Any
import time

# ================= SMART RECOMMENDATION =================
def smart_recommendation(obs):
    t = obs["time"]
    best_option = None
    best_score = -float("inf")

    for s in obs["shipments"]:
        if not (s["ready_time"] <= t <= s["due_time"]):
            continue

        for c in obs["carriers"]:
            dist = 50
            travel_time = max(1, int((dist / 35.0) * 2))
            arrival = t + travel_time

            success_prob = c["reliability"] if arrival <= s["due_time"] else 0
            score = success_prob * 100 - c["cost_per_km"] * dist

            if score > best_score:
                best_score = score
                best_option = (s, c)

    return best_option


# ================= CONFIG =================
BASE_URL = "http://localhost:7860"

st.set_page_config(
    page_title="Pickup Logistics Decision System",
    layout="wide"
)

st.title("Pickup Logistics Decision System")
st.markdown("Factory pickup scheduling under uncertainty using intelligent decision support.")

# ================= SIDEBAR =================
st.sidebar.header("Control Panel")

task_id = st.sidebar.selectbox(
    "Task Difficulty",
    ["easy_day_single_plant", "medium_multi_plant", "hard_dynamic_orders"],
    index=0
)

if st.sidebar.button("Reset Environment"):
    st.session_state.reset_clicked = True
    st.rerun()

col1, col2 = st.sidebar.columns(2)
shipment_id = col1.number_input("Shipment ID", min_value=-1, value=-1, step=1)
carrier_id = col2.number_input("Carrier ID", min_value=-1, value=-1, step=1)

if st.sidebar.button("Execute Decision"):
    st.session_state.step_clicked = True
    st.rerun()

st.sidebar.markdown("---")

auto_play = st.sidebar.checkbox("Automated Mode")
if auto_play:
    step_delay = st.sidebar.slider("Step delay (s)", 0.5, 3.0, 1.0)

# ================= SESSION STATE =================
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

# ================= API =================
@st.cache_data(ttl=1)
def api_call(endpoint: str, method: str = "GET", json_data=None):
    try:
        url = f"{BASE_URL}/{endpoint}"
        if method == "POST":
            resp = requests.post(url, json=json_data, timeout=5)
        else:
            resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

# ================= RESET =================
if st.session_state.get("reset_clicked", False):
    reset_data = api_call(f"reset/{task_id}", "POST")
    if reset_data:
        st.session_state.env_state = reset_data["observation"]
        st.session_state.history = []
        st.session_state.total_reward = 0.0
        st.session_state.done = False
        st.session_state.reset_clicked = False

# ================= AUTO PLAY =================
if auto_play and st.session_state.env_state and not st.session_state.done:

    def baseline_agent(obs: Dict[str, Any]) -> Dict[str, Any]:
        t = obs["time"]
        ready_shipments = [s for s in obs["shipments"] if s["ready_time"] <= t <= s["due_time"]]
        if not ready_shipments:
            return {"shipment_id": None, "carrier_id": None}

        shipment = min(ready_shipments, key=lambda s: (s["due_time"] - t, -s["priority"]))
        carriers = sorted(obs["carriers"], key=lambda c: (-c["reliability"], c["cost_per_km"]))
        carrier = carriers[0]

        return {"shipment_id": shipment["id"], "carrier_id": carrier["id"]}

    action = baseline_agent(st.session_state.env_state)
    step_data = api_call(f"step/{task_id}", "POST", action)

    if step_data:
        st.session_state.env_state = step_data["observation"]
        st.session_state.total_reward += step_data["reward"]
        st.session_state.history.append({
        "time": step_data["observation"]["time"],
        "shipment_id": action.get("shipment_id"),
        "carrier_id": action.get("carrier_id"),
        "reward": step_data["reward"],
        "success": 1 if step_data["reward"] > 0 else 0
    })
        st.session_state.done = step_data["done"]

    time.sleep(step_delay)
    st.rerun()

# ================= MANUAL STEP =================
if st.session_state.step_clicked and st.session_state.env_state and not st.session_state.done:
    action = {"shipment_id": shipment_id, "carrier_id": carrier_id}
    step_data = api_call(f"step/{task_id}", "POST", action)

    if step_data:
        st.session_state.env_state = step_data["observation"]
        st.session_state.total_reward += step_data["reward"]
        st.session_state.history.append({
        "time": step_data["observation"]["time"],
        "shipment_id": action.get("shipment_id"),
        "carrier_id": action.get("carrier_id"),
        "reward": step_data["reward"],
        "success": 1 if step_data["reward"] > 0 else 0
    })
        st.session_state.done = step_data["done"]

    st.session_state.step_clicked = False

# ================= MAIN =================
if st.session_state.env_state:
    obs = st.session_state.env_state

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Time", f"{obs['time']}")
    col2.metric("Pending Shipments", len(obs["shipments"]))
    col3.metric("Total Reward", f"{st.session_state.total_reward:.1f}")
    col4.metric("Status", "Complete" if st.session_state.done else "In Progress")
    # ================= PERFORMANCE METRICS =================
    if st.session_state.history:
        last_reward = st.session_state.history[-1]["reward"]

        success_count = sum(1 for r in st.session_state.history if r["reward"] > 0)
        total_steps = len(st.session_state.history)

        success_rate = (success_count / total_steps) * 100 if total_steps > 0 else 0

        # 🔥 Align with top KPI row (4 columns)
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Last Decision Reward", f"{last_reward:.1f}")
        col2.metric("Success Rate", f"{success_rate:.1f}%")

    # Recommendation
    rec = smart_recommendation(obs)
    if rec:
        shipment, carrier = rec
        st.info(f"Recommended Action: Assign Carrier {carrier['id']} to Shipment {shipment['id']}")

    # Ready shipments
    current_time = obs["time"]
    ready_shipments = [s for s in obs["shipments"] if s["ready_time"] <= current_time <= s["due_time"]]

    if ready_shipments:
        st.warning(f"{len(ready_shipments)} shipments are ready for pickup within their time window.")

    # ================= SHIPMENTS TABLE =================
    st.subheader("Shipments")

    shipments_df = pd.DataFrame(obs["shipments"])

    if not shipments_df.empty and "ready_time" in shipments_df.columns and "due_time" in shipments_df.columns:
        shipments_df["window_left"] = shipments_df["due_time"] - current_time

        shipments_df["status"] = shipments_df.apply(
            lambda row: "READY" if row["ready_time"] <= current_time <= row["due_time"]
            else f"Pending ({row['ready_time'] - current_time}h)",
            axis=1
        )
    else:
        shipments_df["window_left"] = None
        shipments_df["status"] = "No Data"

    st.dataframe(
        shipments_df[["id", "volume", "priority", "status", "window_left"]],
        use_container_width=True
    )

    # ================= CARRIERS TABLE =================
    st.subheader("Carriers")

    carriers_df = pd.DataFrame(obs["carriers"])
    carriers_df["reliability_%"] = (carriers_df["reliability"] * 100).round(1)

    st.dataframe(
        carriers_df[["id", "reliability_%", "cost_per_km", "capacity_per_slot"]],
        use_container_width=True
    )

    # ================= HISTORY =================
    if st.session_state.history:
        st.subheader("Decision Log")

        history_df = pd.DataFrame(st.session_state.history)

        # Success rate calculation
        success_rate = history_df["success"].mean() * 100

        st.dataframe(
            history_df[["time", "shipment_id", "carrier_id", "reward", "success"]],
            use_container_width=True
        )

        st.metric("Overall Success Rate", f"{success_rate:.1f}%")

    # ================= COMPLETE =================
    if st.session_state.done:
        final_score = (
            st.session_state.total_reward / len(st.session_state.history)
            if st.session_state.history else 0
        )
        st.success(f"Execution Complete. Average reward: {final_score:.1f}")

else:
    st.info("Click 'Reset Environment' to start.")

# ================= FOOTER =================
st.markdown("---")
st.markdown("Outbound Pickup Reliability Benchmark | Decision Intelligence System")