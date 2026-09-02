import pandas as pd
import pytest
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from processing_layer.peer_grouper import assign_peer_groups, find_peer_group

def test_rule_based_grouping():
    df = pd.DataFrame([
        {"industry": "SaaS", "funding_stage": "Series A", "headcount": 40},
        {"industry": "Fintech", "funding_stage": "Seed", "headcount": 10},
    ])
    
    res = assign_peer_groups(df, method="rule")
    
    assert res["size_bucket"].iloc[0] == "Medium"
    assert res["peer_group_id"].iloc[0] == "SaaS_SeriesA_Medium"
    
    assert res["size_bucket"].iloc[1] == "Small"
    assert res["peer_group_id"].iloc[1] == "Fintech_Seed_Small"

def test_find_peer_group_exact():
    groups = ["SaaS_SeriesA_Medium", "Fintech_Seed_Small"]
    match = find_peer_group("SaaS", "Series A", 50, groups)
    assert match == "SaaS_SeriesA_Medium"

def test_find_peer_group_fallback():
    groups = ["SaaS_SeriesA_Large", "SaaS_Seed_Small"]
    # Exact: SaaS_SeriesA_Medium -> miss
    # Partial: SaaS_SeriesA_ -> hits SaaS_SeriesA_Large
    match = find_peer_group("SaaS", "Series A", 50, groups)
    assert match == "SaaS_SeriesA_Large"
