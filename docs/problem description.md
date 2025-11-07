# Problem Title

Feature request: Automatic worker resource-elasticity hints from runtime metrics

## Problem Brief

Enable Dask users running on clusters/cloud to receive deterministic, human-readable scaling hints derived from live runtime metrics. The system should analyze task backlog, worker memory utilization, idle time, and data skew to suggest actions such as adding/removing workers or repartitioning to reduce hotspots. This does not auto-scale; it provides clear guidance so operators can act confidently. The outcome is improved cluster efficiency and faster time-to-result through proactive, explainable recommendations.

## Agent Instructions

- Implement a metrics-driven hint engine that periodically inspects scheduler/client runtime metrics.
- Produce a single normalized hint dict: {action: "add"|"remove"|"repartition"|"none", num_workers: int when relevant, reason: str}.
- Ensure deterministic outputs for identical inputs (no hidden state or randomness).
- Add config flags: autoscaler_hint (bool), hint_frequency (seconds), thresholds: memory_pct_high, idle_pct_low, task_backlog_high, skew_ratio_high.
- Expose a public API: Client.get_scaling_hint() -> Dict[str, Any].
- When autoscaler_hint is enabled, emit a log/dashboard message whenever a new hint is computed.
- Do not change scheduling behavior or scale resources automatically; provide guidance only.
- Acceptance criteria:
  - High backlog AND memory pressure -> action "add" with a suggested worker count.
  - Sustained high idle fraction -> action "remove" with a suggested worker count.
  - Persistent skew (one/few workers repeatedly overloaded) -> action "repartition".
  - Outputs are stable and fully deterministic.
- Provide concise docs describing configuration keys and behavior.

## Test Assumptions (optional)

- New public API: distributed.Client.get_scaling_hint(self, metrics: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]. This method delegates to the module-level function; logging and debouncing are handled in the module, not the Client method.
- Config keys are namespaced under "distributed":
  - distributed.autoscaler_hint (bool)
  - distributed.hint_frequency (int seconds)
  - distributed.hints.thresholds: memory_pct_high, idle_pct_low, task_backlog_high, skew_ratio_high
- Module: distributed/scaling_hints.py provides:
  - compute_scaling_hint(metrics: Mapping[str, Any], config: Mapping[str, Any]) -> Dict[str, Any] (pure, no logging/side effects)
  - get_scaling_hint(metrics: Mapping[str, Any], config: Mapping[str, Any]) -> Dict[str, Any] (single source for logging/dashboard emission and hint_frequency gating)
