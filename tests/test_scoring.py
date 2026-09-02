import pytest
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from modeling_layer.scorer import _compute_efficiency_score, _compute_deviations

def test_compute_deviations():
    metrics = {"gross_margin": 0.8}
    benchmarks = {
        "gross_margin": {"mean": 0.6, "median": 0.6, "std": 0.1, "count": 10}
    }
    
    devs = _compute_deviations(metrics, benchmarks)
    assert len(devs) == 1
    assert devs[0]["metric"] == "gross_margin"
    assert devs[0]["z_score"] == pytest.approx(2.0)
    assert devs[0]["direction"] == "above"
    assert devs[0]["is_favorable"] == True
    
def test_compute_efficiency_score():
    metrics = {"gross_margin": 0.8}
    benchmarks = {
        "gross_margin": {"mean": 0.6, "std": 0.1}
    }
    prob = 0.9
    
    score = _compute_efficiency_score(metrics, benchmarks, prob)
    assert 0 <= score <= 100
    # Prob contributes 36 (0.4 * 90)
    # Margin z=2 -> percentile ~97.7 -> contributes ~58.6
    # Expected ~ 94.6
    assert score > 90
