"""
charts.py - Executive Monochromatic Plotly Charts for maxanalysis platform.
High-contrast black, charcoal and grey palette tailored for the light editorial canvas.
Series distinguished by line styles (solid vs dashed), fill patterns, and explicit high-contrast text labels.
No emojis anywhere.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


METRIC_PRETTY_NAMES = {
    "gross_margin": "Gross Margin",
    "opex_to_revenue": "OpEx / Revenue",
    "runway_months": "Runway (Months)",
    "ltv_cac_ratio": "LTV / CAC",
    "mom_revenue_growth": "MoM Growth",
    "funding_efficiency": "Capital Efficiency",
    "revenue_per_employee": "Rev / Employee",
    "burn_rate": "Burn Rate",
}


def create_efficiency_gauge(score: float) -> go.Figure:
    """Create a high-contrast monochromatic circular efficiency gauge on light background."""
    score = max(0, min(100, float(score)))

    if score >= 75:
        tier_text = "OPTIMAL EFFICIENCY"
    elif score >= 50:
        tier_text = "MODERATE EFFICIENCY"
    elif score >= 30:
        tier_text = "CAPITAL DEFICIT"
    else:
        tier_text = "CRITICAL RUNWAY DEFICIT"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={
            "suffix": " / 100",
            "font": {"size": 42, "family": "Obelisk, Remixa, sans-serif", "color": "#0B0B0B"}
        },
        title={
            "text": f"<b>OVERALL EFFICIENCY SCORE</b><br><span style='font-size:0.8em;color:#555555;letter-spacing:0.08em;'>{tier_text}</span>",
            "font": {"size": 15, "family": "Obelisk, Remixa, sans-serif", "color": "#0B0B0B"}
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1.5,
                "tickcolor": "#0B0B0B",
                "tickfont": {"size": 11, "color": "#333333", "family": "Goga, sans-serif"}
            },
            "bar": {"color": "#0B0B0B", "thickness": 0.28},
            "bgcolor": "#DDD9D0",
            "borderwidth": 1.5,
            "bordercolor": "#0B0B0B",
            "steps": [
                {"range": [0, 30], "color": "rgba(0, 0, 0, 0.05)"},
                {"range": [30, 50], "color": "rgba(0, 0, 0, 0.12)"},
                {"range": [50, 75], "color": "rgba(0, 0, 0, 0.22)"},
                {"range": [75, 100], "color": "rgba(0, 0, 0, 0.35)"}
            ],
            "threshold": {
                "line": {"color": "#0B0B0B", "width": 3},
                "thickness": 0.8,
                "value": score
            }
        }
    ))

    fig.update_layout(
        height=320,
        margin=dict(t=65, b=20, l=30, r=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Goga, sans-serif", "color": "#0B0B0B"}
    )
    return fig


def create_radar_chart(target_metrics: dict, benchmark_metrics: dict, metrics_list: list) -> go.Figure:
    """Create a high-contrast monochromatic radar chart distinguishing target vs peers."""
    categories = [METRIC_PRETTY_NAMES.get(m, m.replace("_", " ").title()) for m in metrics_list]

    target_values = []
    bench_values = []

    for m in metrics_list:
        t_val = float(target_metrics.get(m, 0) or 0)
        b_mean = float(benchmark_metrics.get(m, {}).get("mean", 1) or 1)
        if b_mean == 0:
            b_mean = 0.01

        ratio = min(2.2, max(0.0, t_val / b_mean))
        target_values.append(round(ratio, 2))
        bench_values.append(1.0)

    categories_closed = categories + [categories[0]]
    target_closed = target_values + [target_values[0]]
    bench_closed = bench_values + [bench_values[0]]

    fig = go.Figure()

    # Peer Baseline Area - Dashed Mid-Grey line
    fig.add_trace(go.Scatterpolar(
        r=bench_closed,
        theta=categories_closed,
        fill="toself",
        name="Peer Average Baseline (1.0x)",
        line=dict(color="#666666", width=2.0, dash="dash"),
        fillcolor="rgba(100, 100, 100, 0.08)",
        hoverinfo="theta+name"
    ))

    # Target Startup Area - Solid Bold Black line with subtle fill
    fig.add_trace(go.Scatterpolar(
        r=target_closed,
        theta=categories_closed,
        fill="toself",
        name="Your Startup Metrics",
        line=dict(color="#0B0B0B", width=3.0),
        fillcolor="rgba(11, 11, 11, 0.15)",
        hoverinfo="theta+r+name"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 2.2],
                tickvals=[0.5, 1.0, 1.5, 2.0],
                ticktext=["50%", "100% (Baseline)", "150%", "200%"],
                tickfont=dict(size=10, color="#444444"),
                gridcolor="#C8C5BD",
                linecolor="#888888"
            ),
            angularaxis=dict(
                gridcolor="#C8C5BD",
                linecolor="#0B0B0B",
                tickfont=dict(size=11, color="#0B0B0B", family="Obelisk, Remixa, sans-serif")
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(color="#0B0B0B", size=12, family="Goga, sans-serif")
        ),
        margin=dict(t=30, b=55, l=40, r=40),
        paper_bgcolor="rgba(0,0,0,0)",
        height=380,
        font=dict(family="Goga, sans-serif", color="#0B0B0B")
    )
    return fig


def create_deviation_bar_chart(deviations: list) -> go.Figure:
    """Create a high-contrast monochromatic horizontal diverging bar chart."""
    if not deviations:
        return go.Figure()

    sorted_devs = sorted(deviations, key=lambda x: abs(x.get("z_score", 0)), reverse=True)[:8]

    labels = [d.get("label", d.get("metric", "")).upper() for d in sorted_devs]
    z_scores = [round(d.get("z_score", 0), 2) for d in sorted_devs]

    colors = []
    text_labels = []
    border_colors = []

    for d in sorted_devs:
        z = round(d.get("z_score", 0), 2)
        if d.get("is_favorable", False):
            colors.append("#0B0B0B")
            border_colors.append("#0B0B0B")
            text_labels.append(f"{z:+.2f}σ [FAVORABLE]")
        elif d.get("severity") == "critical":
            colors.append("#3A3A3A")
            border_colors.append("#0B0B0B")
            text_labels.append(f"{z:+.2f}σ [CRITICAL]")
        else:
            colors.append("#7A7A7A")
            border_colors.append("#0B0B0B")
            text_labels.append(f"{z:+.2f}σ [WARNING]")

    fig = go.Figure(go.Bar(
        x=z_scores,
        y=labels,
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(color=border_colors, width=1.5)
        ),
        text=text_labels,
        textposition="outside",
        textfont=dict(color="#0B0B0B", size=11, family="Goga, sans-serif")
    ))

    fig.update_layout(
        title=dict(
            text="<b>KEY METRIC DEVIATIONS (Z-SCORES VS PEERS)</b>",
            font=dict(size=14, family="Obelisk, Remixa, sans-serif", color="#0B0B0B")
        ),
        xaxis=dict(
            title=dict(text="Standard Deviations from Peer Mean (σ)", font=dict(size=11, color="#444444")),
            gridcolor="#C8C5BD",
            zerolinecolor="#0B0B0B",
            zerolinewidth=2,
            tickfont=dict(color="#333333")
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(color="#0B0B0B", size=11, family="Obelisk, sans-serif")
        ),
        height=320,
        margin=dict(t=50, b=40, l=130, r=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Goga, sans-serif", color="#0B0B0B")
    )
    return fig


def create_cost_breakdown_donut(cogs: float, opex: float, marketing: float) -> go.Figure:
    """Create a high-contrast monochromatic donut chart with fallback if raw metrics are 0."""
    cogs = max(0.0, float(cogs or 0))
    marketing = max(0.0, float(marketing or 0))
    other_opex = max(0.0, float(opex or 0) - marketing)

    total = cogs + marketing + other_opex
    if total == 0:
        cogs = 25.0
        marketing = 35.0
        other_opex = 40.0
        labels = ["Cost of Goods (COGS - Est.)", "Sales & Marketing (Est.)", "Other OpEx (Salaries / G&A - Est.)"]
    else:
        labels = ["Cost of Goods (COGS)", "Sales & Marketing", "Other OpEx (Salaries / G&A)"]

    values = [cogs, marketing, other_opex]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.60,
        marker=dict(
            colors=["#0B0B0B", "#555555", "#9E9E9E"],
            line=dict(color="#EDEBE6", width=2.5)
        ),
        textinfo="percent",
        textfont=dict(size=12, color="#FFFFFF", family="Obelisk, sans-serif"),
        hoverinfo="label+value+percent"
    ))

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.35,
            xanchor="center",
            x=0.5,
            font=dict(color="#0B0B0B", size=11, family="Goga, sans-serif")
        ),
        height=300,
        margin=dict(t=20, b=50, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text="<b>COSTS</b>",
            x=0.5, y=0.5,
            font=dict(size=14, color="#0B0B0B", family="Obelisk, sans-serif"),
            showarrow=False
        )]
    )
    return fig
