import pytest


try:
    # Expected new helper as per problem spec
    from distributed.scaling_hints import compute_scaling_hint  # type: ignore
except Exception as e:  # pragma: no cover - fail clearly before feature exists
    raise AssertionError(
        "Missing 'distributed.scaling_hints.compute_scaling_hint'.\n"
        "Implement a pure function compute_scaling_hint(metrics, config) -> dict as specified."
    ) from e


def test_hint_add_workers_on_backlog_and_memory():
    metrics = {
        "task_backlog": 200,
        "memory": {"avg_used_pct": 0.86, "per_worker_used_pct": {"w-1": 0.90, "w-2": 0.82}},
        "idle": {"idle_workers": 0, "total_workers": 2, "idle_pct": 0.0},
        "skew": {"max_to_median_ratio": 1.2},
    }
    cfg = {
        "hint_frequency": 60,
        "thresholds": {
            "memory_pct_high": 0.80,
            "idle_pct_low": 0.10,
            "task_backlog_high": 100,
            "skew_ratio_high": 2.0,
        },
    }
    out = compute_scaling_hint(metrics, cfg)
    assert out["action"] == "add"
    assert isinstance(out.get("num_workers", 1), int)
    assert out["num_workers"] >= 1
    assert "reason" in out and isinstance(out["reason"], str)


def test_hint_remove_workers_on_sustained_idle():
    metrics = {
        "task_backlog": 0,
        "memory": {"avg_used_pct": 0.20, "per_worker_used_pct": {"w-1": 0.2, "w-2": 0.2, "w-3": 0.2}},
        "idle": {"idle_workers": 3, "total_workers": 3, "idle_pct": 1.0},
        "skew": {"max_to_median_ratio": 1.0},
    }
    cfg = {
        "hint_frequency": 60,
        "thresholds": {
            "memory_pct_high": 0.80,
            "idle_pct_low": 0.10,
            "task_backlog_high": 100,
            "skew_ratio_high": 2.0,
        },
    }
    out = compute_scaling_hint(metrics, cfg)
    assert out["action"] == "remove"
    assert isinstance(out.get("num_workers", 1), int)
    assert out["num_workers"] >= 1
    assert "reason" in out and isinstance(out["reason"], str)


def test_hint_repartition_on_persistent_skew():
    metrics = {
        "task_backlog": 10,
        "memory": {"avg_used_pct": 0.50, "per_worker_used_pct": {"w-1": 0.90, "w-2": 0.10}},
        "idle": {"idle_workers": 0, "total_workers": 2, "idle_pct": 0.0},
        "skew": {"max_to_median_ratio": 5.0},
    }
    cfg = {
        "hint_frequency": 60,
        "thresholds": {
            "memory_pct_high": 0.80,
            "idle_pct_low": 0.10,
            "task_backlog_high": 100,
            "skew_ratio_high": 2.0,
        },
    }
    out = compute_scaling_hint(metrics, cfg)
    assert out["action"] == "repartition"
    assert "reason" in out and isinstance(out["reason"], str)
