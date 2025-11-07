# 1. Problem Brief

Provide deterministic, human-readable scaling hints for Dask Distributed clusters based on live runtime metrics. Operators should receive guidance (not automatic scaling) on when to add/remove workers or repartition to relieve hotspots, reduce cost, and improve time-to-result. Hints must be stable, explainable, and safe to act on.

# 2. Agent Instructions

- Implement a metrics-driven hint engine that evaluates these normalized keys: task_backlog (int), memory.avg_used_pct (0-1), memory.per_worker_used_pct (worker->0-1), idle.idle_pct (0-1) with idle/total counts, and skew.max_to_median_ratio (float). Ignore unknown keys deterministically.
- Produce a normalized hint dict: action in {add, remove, repartition, none}; reason: str; num_workers: int (only when action in {add, remove}, >=1).
- Configure under "distributed": autoscaler_hint (bool), hint_frequency (seconds), and hints.thresholds: memory_pct_high, idle_pct_low, task_backlog_high, skew_ratio_high.
- When autoscaler_hint is enabled, emit a concise log/dashboard message for every computed hint (including "none"), rate-limited by hint_frequency.
- No side effects: do not scale or mutate cluster state; outputs must be deterministic for identical inputs.
- Acceptance: backlog+memory -> add; sustained high idle -> remove; persistent skew -> repartition; otherwise none.

# 3. Test Assumptions (optional)

- Public API names/signatures:
  - distributed.Client.get_scaling_hint(self, metrics: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]
  - Module: distributed.scaling_hints provides:
    - compute_scaling_hint(metrics: Mapping[str, Any], config: Mapping[str, Any]) -> Dict[str, Any] (pure)
    - get_scaling_hint(metrics: Mapping[str, Any], config: Mapping[str, Any]) -> Dict[str, Any] (logging + frequency gating)
