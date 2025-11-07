import dask
from dask.base import tokenize
import dask.config as dc


def test_config_context_manager_sets_and_restores():
    before = dc.get("optimization.fuse.active", default=None)
    with dc.set({"optimization.fuse.active": False}):
        assert dc.get("optimization.fuse.active") is False
    after = dc.get("optimization.fuse.active", default=None)
    assert after == before


def test_tokenize_is_deterministic_for_same_input():
    data = {"x": [1, 2, 3], "y": ("abc", 123), "z": {"a": 1, "b": 2}}
    t1 = tokenize(data)
    t2 = tokenize(data)
    assert t1 == t2
