# graders/pickup_graders.py

from typing import Dict, Any, List


def _clip_strict(score: float) -> float:
    """
    Ensure score is strictly between (0,1)
    """
    if score <= 0:
        return 0.01
    if score >= 1:
        return 0.99
    return score


def _kpis(assignments: List[Dict[str, Any]], total_shipments: int) -> Dict[str, float]:
    if not assignments:
        return {
            "on_time_rate": 0.0,
            "no_show_rate": 1.0,
            "avg_cost": 500.0,
            "coverage": 0.0
        }

    n = len(assignments)

    return {
        "on_time_rate": sum(a["on_time"] for a in assignments) / n,
        "no_show_rate": sum(not a["show"] for a in assignments) / n,
        "avg_cost": sum(a["cost"] for a in assignments) / n,
        "coverage": n / max(total_shipments, 1),
    }


def grade_easy(episode_info: Dict[str, Any]) -> float:
    k = _kpis(episode_info["assignments"], episode_info["total_shipments"])

    score = 0.8 * k["on_time_rate"] + 0.2 * (1 - k["no_show_rate"])

    return _clip_strict(score)


def grade_medium(episode_info: Dict[str, Any]) -> float:
    k = _kpis(episode_info["assignments"], episode_info["total_shipments"])

    cost_score = max(0.0, min(1.0, 1 - k["avg_cost"] / 600.0))

    score = (
        0.5 * k["on_time_rate"]
        + 0.2 * (1 - k["no_show_rate"])
        + 0.3 * cost_score
    )

    return _clip_strict(score)


def grade_hard(episode_info: Dict[str, Any]) -> float:
    k = _kpis(episode_info["assignments"], episode_info["total_shipments"])

    cost_score = max(0.0, min(1.0, 1 - k["avg_cost"] / 600.0))

    score = (
        0.35 * k["on_time_rate"]
        + 0.2 * (1 - k["no_show_rate"])
        + 0.25 * k["coverage"]
        + 0.2 * cost_score
    )

    return _clip_strict(score)