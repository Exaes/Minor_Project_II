"""
Orchestrates the full analysis pipeline:
1. Load startup from DB
2. Run scorer (feature engineering -> benchmarking)
3. Generate recommendations (LLM or fallback)
4. Save results to DB
"""

import os
import sys
import json
from sqlalchemy.orm import Session

# Direct imports using sys.path manipulation for modeling and data layers
_data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data-layer")
sys.path.insert(0, _data_dir)
from storage import models as db_models

_modeling_dir = os.path.join(os.path.dirname(__file__), "..", "..", "modeling-layer")
sys.path.insert(0, _modeling_dir)
import scorer
from llm import recommendation_generator


def run_analysis_pipeline(db: Session, startup_id: int, use_llm: bool = True) -> int:
    """
    Run the full pipeline for a target startup and store the result.

    Args:
        db: SQLAlchemy session
        startup_id: ID of the startup in the database
        use_llm: Whether to use LLM for recommendations

    Returns:
        analysis_id: ID of the stored AnalysisResult
    """
    # 1. Fetch startup
    startup = db.query(db_models.Startup).filter(db_models.Startup.id == startup_id).first()
    if not startup:
        raise ValueError(f"Startup with ID {startup_id} not found.")

    # Convert to dict for pipeline
    startup_data = {
        col.name: getattr(startup, col.name)
        for col in startup.__table__.columns
    }

    # 2. Score startup
    scoring_result = scorer.score_startup(startup_data)

    # 3. Generate recommendations
    recommendations = recommendation_generator.generate_recommendations(
        startup_data=startup_data,
        scoring_result=scoring_result,
        num_recommendations=5,
        use_llm=use_llm
    )

    # 4. Save to Database
    analysis = db_models.AnalysisResult(
        startup_id=startup_id,
        efficiency_score=scoring_result["efficiency_score"],
        peer_group_id=scoring_result["peer_group_id"],
        peer_group_label=scoring_result["peer_group_label"],
        computed_metrics_json=json.dumps(scoring_result["computed_metrics"]),
        peer_benchmarks_json=json.dumps(scoring_result["peer_benchmarks"]),
        deviations_json=json.dumps(scoring_result["deviations"])
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    for rec in recommendations:
        db_rec = db_models.Recommendation(
            analysis_id=analysis.id,
            rank=rec["rank"],
            category=rec["category"],
            impact_level=rec["impact_level"],
            title=rec["title"],
            explanation=rec["explanation"],
            supporting_data_json=json.dumps(rec["supporting_data"])
        )
        db.add(db_rec)
    
    db.commit()

    return analysis.id
