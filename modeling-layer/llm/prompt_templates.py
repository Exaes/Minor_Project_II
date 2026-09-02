"""
Structured prompt templates for LLM-based recommendation generation.

Designed to constrain the LLM to explain computed deviations rather than
invent new numbers. Every recommendation must cite the actual metrics.
"""

SYSTEM_PROMPT = """You are an expert startup strategy advisor. Your role is to analyze a startup's financial and operational metrics compared to its peer group benchmarks and provide actionable, data-grounded business recommendations.

CRITICAL RULES:
1. ONLY reference the specific numbers provided in the input data. Never invent statistics.
2. Every recommendation MUST cite the actual metric values and benchmarks.
3. Be specific and actionable — no generic advice like "improve your margins".
4. Focus on the HIGHEST IMPACT deviations first.
5. Output MUST be valid JSON matching the required schema.

You will receive:
- The startup's profile (industry, stage, size)
- Their computed metrics vs peer benchmarks
- The top deviations (biggest gaps from benchmarks)

For each deviation, produce a recommendation with:
- A clear, actionable title
- A detailed explanation grounded in the numbers
- A category tag
- An impact level estimate"""


RECOMMENDATION_PROMPT_TEMPLATE = """## Startup Profile
- **Company**: {company_name}
- **Industry**: {industry}
- **Stage**: {funding_stage}
- **Headcount**: {headcount}
- **Monthly Revenue**: ${monthly_revenue:,.0f}
- **Monthly Expenses**: ${monthly_expenses:,.0f}
- **Total Funding**: ${total_funding_usd:,.0f}

## Peer Group: {peer_group_label}

## Top Metric Deviations (from peer benchmark)
{deviations_text}

## Task
Generate exactly {num_recommendations} prioritized recommendations based on the deviations above.

Output valid JSON — an array of objects with these fields:
```json
[
  {{
    "rank": 1,
    "title": "Short actionable title",
    "category": "Cost-cutting | Margin improvement | Growth efficiency | Hiring pace",
    "impact_level": "High | Medium | Low",
    "explanation": "Detailed explanation citing the EXACT numbers from the deviations above. Example: Your burn rate of $X/month is Y standard deviations above your peer average of $Z/month...",
    "supporting_data": {{
      "metric": "metric_name",
      "your_value": 123.45,
      "benchmark": 67.89,
      "z_score": 2.1
    }}
  }}
]
```

IMPORTANT: Return ONLY the JSON array, no other text."""


def format_deviations_text(deviations: list[dict], max_items: int = 8) -> str:
    """
    Format deviation list into a human-readable text block for the LLM prompt.

    Only includes unfavorable deviations (the ones needing attention).
    """
    # Filter to unfavorable or all if few unfavorable
    unfavorable = [d for d in deviations if not d.get("is_favorable", True)]
    if len(unfavorable) < 3:
        items = deviations[:max_items]
    else:
        items = unfavorable[:max_items]

    lines = []
    for i, dev in enumerate(items, 1):
        status = "⚠️" if dev.get("severity") in ("critical", "warning") else "✅"
        direction = "above" if dev.get("direction") == "above" else "below"

        lines.append(
            f"{i}. {status} **{dev['label']}**: "
            f"Your value = {dev['your_value']:.4g}, "
            f"Peer average = {dev['benchmark_mean']:.4g}, "
            f"Z-score = {dev['z_score']:+.2f} ({direction} benchmark), "
            f"Severity = {dev.get('severity', 'unknown')}"
        )

    return "\n".join(lines)


def build_recommendation_prompt(
    startup_data: dict,
    scoring_result: dict,
    num_recommendations: int = 5,
) -> tuple[str, str]:
    """
    Build the full system + user prompt for recommendation generation.

    Args:
        startup_data: Original startup data dict.
        scoring_result: Output from scorer.score_startup().
        num_recommendations: Number of recommendations to generate.

    Returns:
        Tuple of (system_prompt, user_prompt).
    """
    deviations_text = format_deviations_text(
        scoring_result.get("deviations", [])
    )

    user_prompt = RECOMMENDATION_PROMPT_TEMPLATE.format(
        company_name=startup_data.get("company_name", "Target Startup"),
        industry=startup_data.get("industry", "Unknown"),
        funding_stage=startup_data.get("funding_stage", "Unknown"),
        headcount=startup_data.get("headcount", 0),
        monthly_revenue=startup_data.get("monthly_revenue", 0),
        monthly_expenses=startup_data.get("monthly_expenses", 0),
        total_funding_usd=startup_data.get("total_funding_usd", 0),
        peer_group_label=scoring_result.get("peer_group_label", "Unknown"),
        deviations_text=deviations_text,
        num_recommendations=num_recommendations,
    )

    return SYSTEM_PROMPT, user_prompt
