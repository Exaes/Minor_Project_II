"""
Rule-based fallback recommendation generator.

Generates structured, data-grounded recommendations without an LLM,
using templates that map specific metric deviations to actionable advice.

Always works — no API key needed.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
_processing_dir = os.path.join(os.path.dirname(__file__), "..", "..", "processing-layer")
sys.path.insert(0, _processing_dir)
import feature_engineer


# ── Recommendation Templates ──
# Maps metric names to template-based recommendations
# Each template includes category, and explanation template with placeholders

RECOMMENDATION_TEMPLATES = {
    "burn_rate": {
        "category": "Cost-cutting",
        "title_high": "Reduce Monthly Cash Burn",
        "title_low": "Healthy Cash Burn — Maintain Current Spending Discipline",
        "explanation_high": (
            "Your monthly burn rate of ${your_value:,.0f} is {z_score_abs:.1f} standard deviations "
            "above your peer group average of ${benchmark:,.0f}/month. This elevated burn threatens "
            "your runway. Consider: (1) auditing top 3 expense categories, (2) renegotiating vendor "
            "contracts, (3) pausing non-critical hiring. Reducing burn by {reduction_pct:.0f}% would "
            "align you with peer benchmarks and extend runway significantly."
        ),
    },
    "runway_months": {
        "category": "Cost-cutting",
        "title_high": "Extend Cash Runway",
        "title_low": "Strong Runway Position",
        "explanation_high": (
            "Your estimated runway of {your_value:.0f} months is {z_score_abs:.1f} standard "
            "deviations below the peer average of {benchmark:.0f} months. At current burn, you "
            "have limited time before needing additional capital. Prioritize reducing monthly "
            "expenses or accelerating revenue to extend runway to at least {target:.0f} months."
        ),
    },
    "gross_margin": {
        "category": "Margin improvement",
        "title_high": "Improve Gross Margin",
        "title_low": "Strong Gross Margin — Competitive Advantage",
        "explanation_high": (
            "Your gross margin of {your_value:.1%} is {z_score_abs:.1f} standard deviations below "
            "the peer average of {benchmark:.1%}. This {gap_pct:.1f} percentage point gap suggests "
            "higher-than-expected direct costs. Investigate: (1) COGS composition and supplier "
            "pricing, (2) pricing strategy — can unit prices increase without demand impact? "
            "(3) product mix optimization toward higher-margin offerings."
        ),
    },
    "cac": {
        "category": "Growth efficiency",
        "title_high": "Optimize Customer Acquisition Cost",
        "title_low": "Efficient Customer Acquisition",
        "explanation_high": (
            "Your CAC of ${your_value:,.0f} is {z_score_abs:.1f} standard deviations above the "
            "peer average of ${benchmark:,.0f}. You're spending {ratio:.1f}x more per customer "
            "than peers. Recommended actions: (1) analyze channel-level CAC to identify "
            "underperforming channels, (2) invest more in organic/referral growth, "
            "(3) improve conversion rates in your marketing funnel."
        ),
    },
    "ltv_cac_ratio": {
        "category": "Growth efficiency",
        "title_high": "Improve LTV:CAC Ratio",
        "title_low": "Healthy Unit Economics",
        "explanation_high": (
            "Your LTV:CAC ratio of {your_value:.2f} is {z_score_abs:.1f} standard deviations "
            "below the peer average of {benchmark:.2f}. A ratio below 3.0 indicates you may be "
            "spending too much to acquire customers relative to their lifetime value. "
            "Focus on: (1) reducing CAC through channel optimization, (2) increasing LTV through "
            "upselling/cross-selling, (3) improving retention to extend customer lifetime."
        ),
    },
    "opex_to_revenue": {
        "category": "Cost-cutting",
        "title_high": "Reduce Operating Expense Ratio",
        "title_low": "Lean Operating Structure",
        "explanation_high": (
            "Your OpEx-to-revenue ratio of {your_value:.2f} is {z_score_abs:.1f} standard "
            "deviations above the peer average of {benchmark:.2f}. Operating expenses consume "
            "{your_value_pct:.0f}% of revenue vs {benchmark_pct:.0f}% for peers. Target areas: "
            "(1) headcount efficiency — are you overstaffed relative to revenue? (2) SaaS tool "
            "consolidation, (3) office/infrastructure cost reduction."
        ),
    },
    "revenue_per_employee": {
        "category": "Hiring pace",
        "title_high": "Improve Revenue Per Employee",
        "title_low": "Strong Per-Employee Productivity",
        "explanation_high": (
            "Your revenue per employee of ${your_value:,.0f}/month is {z_score_abs:.1f} standard "
            "deviations below the peer average of ${benchmark:,.0f}/month. This suggests potential "
            "overstaffing or undermonetization. Consider: (1) pausing hiring until revenue catches "
            "up, (2) automating repetitive tasks, (3) reallocating headcount to revenue-generating "
            "roles."
        ),
    },
    "funding_efficiency": {
        "category": "Growth efficiency",
        "title_high": "Improve Capital Efficiency",
        "title_low": "Efficient Use of Capital",
        "explanation_high": (
            "Your funding efficiency ratio (annual revenue / total funding) is {your_value:.3f}, "
            "which is {z_score_abs:.1f} standard deviations below the peer average of "
            "{benchmark:.3f}. You're generating less revenue per dollar raised than peers. "
            "Focus on: (1) accelerating revenue growth, (2) reducing cash burn to make existing "
            "capital go further, (3) reaching revenue milestones before raising the next round."
        ),
    },
    "mom_revenue_growth": {
        "category": "Growth efficiency",
        "title_high": "Accelerate Revenue Growth",
        "title_low": "Strong Revenue Growth Trajectory",
        "explanation_high": (
            "Your month-over-month revenue growth of {your_value:.1%} is {z_score_abs:.1f} "
            "standard deviations below the peer average of {benchmark:.1%}. At the peer growth "
            "rate, you'd reach {projected_revenue:,.0f}/month in 12 months vs your current "
            "trajectory. Investigate: (1) sales pipeline health, (2) product-market fit signals, "
            "(3) pricing optimization."
        ),
    },
    "payback_period": {
        "category": "Growth efficiency",
        "title_high": "Shorten Customer Payback Period",
        "title_low": "Quick Customer Payback",
        "explanation_high": (
            "Your payback period of {your_value:.1f} months is {z_score_abs:.1f} standard "
            "deviations above the peer average of {benchmark:.1f} months. It takes you "
            "{extra_months:.0f} months longer to recover customer acquisition costs. Reduce by: "
            "(1) lowering CAC, (2) increasing first-month revenue per customer, "
            "(3) offering annual prepaid plans."
        ),
    },
    "capital_to_revenue": {
        "category": "Cost-cutting",
        "title_high": "Reduce Capital Dependency",
        "title_low": "Revenue-Funded Growth",
        "explanation_high": (
            "Your capital-to-revenue ratio of {your_value:.2f} means you've raised "
            "{your_value:.1f}x your annual revenue in funding — {z_score_abs:.1f} standard "
            "deviations above the peer average of {benchmark:.2f}x. Work toward: (1) reaching "
            "profitability sooner, (2) growing revenue to justify the capital raised, "
            "(3) demonstrating improving unit economics to investors."
        ),
    },
    "hc_vs_rev_growth": {
        "category": "Hiring pace",
        "title_high": "Align Hiring Pace with Revenue Growth",
        "title_low": "Revenue Outpacing Headcount Growth",
        "explanation_high": (
            "Your headcount-to-revenue growth ratio of {your_value:.2f} indicates headcount is "
            "growing {your_value:.1f}x faster than revenue — {z_score_abs:.1f} standard "
            "deviations from peers at {benchmark:.2f}. Consider: (1) implementing a hiring "
            "freeze until revenue catches up, (2) linking new hires to revenue milestones, "
            "(3) investing in productivity tools over headcount."
        ),
    },
}


def generate_fallback_recommendations(
    startup_data: dict,
    scoring_result: dict,
    num_recommendations: int = 5,
) -> list[dict]:
    """
    Generate recommendations using rule-based templates.

    Processes deviations in order of severity and generates
    templated recommendations grounded in actual computed numbers.

    Args:
        startup_data: Original startup data dict.
        scoring_result: Output from scorer.score_startup().
        num_recommendations: Max recommendations to generate.

    Returns:
        List of recommendation dicts.
    """
    deviations = scoring_result.get("deviations", [])

    # Filter to unfavorable deviations (things that need improvement)
    unfavorable = [d for d in deviations if not d.get("is_favorable", True)]

    # If few unfavorable, include all deviations
    if len(unfavorable) < 2:
        candidates = deviations
    else:
        candidates = unfavorable

    recommendations = []
    for i, dev in enumerate(candidates[:num_recommendations]):
        metric = dev["metric"]
        template = RECOMMENDATION_TEMPLATES.get(metric)

        if template is None:
            # Generic recommendation for metrics without specific templates
            rec = _generic_recommendation(dev, i + 1)
        else:
            rec = _apply_template(template, dev, startup_data, i + 1)

        recommendations.append(rec)

    # If we have fewer recommendations than requested, add positive observations
    if len(recommendations) < num_recommendations:
        favorable = [d for d in deviations if d.get("is_favorable", True)]
        for dev in favorable[:num_recommendations - len(recommendations)]:
            metric = dev["metric"]
            template = RECOMMENDATION_TEMPLATES.get(metric)
            if template:
                rec = {
                    "rank": len(recommendations) + 1,
                    "title": template.get("title_low", f"Strong {dev['label']}"),
                    "category": template["category"],
                    "impact_level": "Low",
                    "explanation": (
                        f"Your {dev['label'].lower()} of {dev['your_value']:.4g} is "
                        f"{'above' if dev['direction'] == 'above' else 'at or below'} "
                        f"the peer average of {dev['benchmark_mean']:.4g}. "
                        f"This is a strength — maintain this performance."
                    ),
                    "supporting_data": {
                        "metric": metric,
                        "your_value": dev["your_value"],
                        "benchmark": dev["benchmark_mean"],
                        "z_score": dev["z_score"],
                    },
                }
                recommendations.append(rec)

    return recommendations


def _apply_template(
    template: dict,
    deviation: dict,
    startup_data: dict,
    rank: int,
) -> dict:
    """Apply a recommendation template to a specific deviation."""
    z_abs = abs(deviation["z_score"])

    # Determine impact level from z-score
    if z_abs >= 2.0:
        impact = "High"
    elif z_abs >= 1.0:
        impact = "Medium"
    else:
        impact = "Low"

    # Build template variables
    template_vars = {
        "your_value": deviation["your_value"],
        "benchmark": deviation["benchmark_mean"],
        "z_score_abs": z_abs,
        "ratio": (deviation["your_value"] / max(0.01, deviation["benchmark_mean"])),
        "gap_pct": abs(deviation["your_value"] - deviation["benchmark_mean"]) * 100,
        "reduction_pct": min(50, z_abs * 15),
        "target": deviation["benchmark_mean"] * 1.1,
        "your_value_pct": deviation["your_value"] * 100,
        "benchmark_pct": deviation["benchmark_mean"] * 100,
        "extra_months": max(0, deviation["your_value"] - deviation["benchmark_mean"]),
        "projected_revenue": startup_data.get("monthly_revenue", 0) * (
            1 + deviation["benchmark_mean"]
        ) ** 12 if deviation["metric"] == "mom_revenue_growth" else 0,
    }

    # Select appropriate explanation
    explanation_key = "explanation_high"  # We already filtered to unfavorable
    explanation_template = template.get(explanation_key, "")

    try:
        explanation = explanation_template.format(**template_vars)
    except (KeyError, ValueError):
        explanation = (
            f"Your {deviation['label'].lower()} of {deviation['your_value']:.4g} "
            f"deviates {z_abs:.1f} standard deviations from the peer benchmark of "
            f"{deviation['benchmark_mean']:.4g}."
        )

    return {
        "rank": rank,
        "title": template.get("title_high", f"Improve {deviation['label']}"),
        "category": template["category"],
        "impact_level": impact,
        "explanation": explanation,
        "supporting_data": {
            "metric": deviation["metric"],
            "your_value": deviation["your_value"],
            "benchmark": deviation["benchmark_mean"],
            "z_score": deviation["z_score"],
        },
    }


def _generic_recommendation(deviation: dict, rank: int) -> dict:
    """Generate a generic recommendation for metrics without specific templates."""
    z_abs = abs(deviation["z_score"])
    higher_is_better = feature_engineer.METRIC_DIRECTION.get(deviation["metric"], True)

    if z_abs >= 2.0:
        impact = "High"
    elif z_abs >= 1.0:
        impact = "Medium"
    else:
        impact = "Low"

    direction_word = "increase" if higher_is_better else "decrease"

    return {
        "rank": rank,
        "title": f"{'Improve' if not deviation['is_favorable'] else 'Maintain'} {deviation['label']}",
        "category": "General",
        "impact_level": impact,
        "explanation": (
            f"Your {deviation['label'].lower()} of {deviation['your_value']:.4g} is "
            f"{z_abs:.1f} standard deviations "
            f"{'above' if deviation['direction'] == 'above' else 'below'} "
            f"the peer benchmark of {deviation['benchmark_mean']:.4g}. "
            f"To align with peers, aim to {direction_word} this metric toward "
            f"{deviation['benchmark_mean']:.4g}."
        ),
        "supporting_data": {
            "metric": deviation["metric"],
            "your_value": deviation["your_value"],
            "benchmark": deviation["benchmark_mean"],
            "z_score": deviation["z_score"],
        },
    }
