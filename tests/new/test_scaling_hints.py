import logging
import pytest


def _import_compute():
    try:
        from distributed.scaling_hints import compute_scaling_hint  # type: ignore
    except Exception as e:  # pragma: no cover - fail clearly before feature exists
        pytest.fail(
            "Missing 'distributed.scaling_hints.compute_scaling_hint'. "
            "Implement a pure function compute_scaling_hint(metrics, config) -> dict as specified."
        )
    return compute_scaling_hint


def test_api_client_method_presence():
    try:
        from distributed import Client  # type: ignore
    except Exception:
        pytest.fail(
            "Missing public API: distributed.Client is unavailable; "
            "expected Client.get_scaling_hint() method per problem spec."
        )
    assert hasattr(Client, "get_scaling_hint"), (
        "Client.get_scaling_hint() must be implemented as a public API."
    )


def test_hint_add_workers_on_backlog_and_memory():
    compute_scaling_hint = _import_compute()
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
    compute_scaling_hint = _import_compute()
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
    compute_scaling_hint = _import_compute()
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


def test_hint_none_when_all_within_thresholds():
    compute_scaling_hint = _import_compute()
    metrics = {
        "task_backlog": 0,
        "memory": {"avg_used_pct": 0.10, "per_worker_used_pct": {"w-1": 0.10, "w-2": 0.12}},
        "idle": {"idle_workers": 0, "total_workers": 2, "idle_pct": 0.0},
        "skew": {"max_to_median_ratio": 1.1},
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
    assert out["action"] == "none"


def test_determinism_same_inputs_same_output():
    compute_scaling_hint = _import_compute()
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
    out1 = compute_scaling_hint(metrics, cfg)
    out2 = compute_scaling_hint(metrics, cfg)
    assert out1 == out2


def test_config_namespace_and_logging(caplog):
    compute_scaling_hint = _import_compute()
    caplog.set_level(logging.INFO)
    # Simulate config under the 'distributed' namespace
    cfg = {
        "autoscaler_hint": True,
        "hint_frequency": 60,
        "thresholds": {
            "memory_pct_high": 0.80,
            "idle_pct_low": 0.10,
            "task_backlog_high": 100,
            "skew_ratio_high": 2.0,
        },
    }
    metrics = {
        "task_backlog": 0,
        "memory": {"avg_used_pct": 0.10, "per_worker_used_pct": {"w-1": 0.10, "w-2": 0.12}},
        "idle": {"idle_workers": 0, "total_workers": 2, "idle_pct": 0.0},
        "skew": {"max_to_median_ratio": 1.1},
    }
    out = compute_scaling_hint(metrics, cfg)
    assert out["action"] in {"none", "add", "remove", "repartition"}
    # Expect some hint-related log emission when autoscaler_hint is True
    assert any("Scaling hint" in (rec.getMessage() or "") for rec in caplog.records), (
        "Expected a 'Scaling hint' log/dashboard emission when autoscaler_hint is enabled."
    )


def test_no_autoscaling_side_effects(monkeypatch):
    compute_scaling_hint = _import_compute()
    # Guard against accidental scaling side-effects by raising if scale is called
    try:
        from distributed import Client  # type: ignore
    except Exception:
        pytest.fail("distributed.Client must be importable for side-effect protection test.")

    called = {"scale": False}

    def fake_scale(*a, **k):
        called["scale"] = True
        raise AssertionError("Scaling must not be triggered by hint generation")

    monkeypatch.setattr(Client, "scale", fake_scale, raising=False)

    metrics = {
        "task_backlog": 10,
        "memory": {"avg_used_pct": 0.50, "per_worker_used_pct": {"w-1": 0.50, "w-2": 0.50}},
        "idle": {"idle_workers": 0, "total_workers": 2, "idle_pct": 0.0},
        "skew": {"max_to_median_ratio": 1.0},
    }
    cfg = {
        "autoscaler_hint": True,
        "hint_frequency": 60,
        "thresholds": {
            "memory_pct_high": 0.80,
            "idle_pct_low": 0.10,
            "task_backlog_high": 100,
            "skew_ratio_high": 2.0,
        },
    }
    _ = compute_scaling_hint(metrics, cfg)
    assert called["scale"] is False
