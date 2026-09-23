"""
Modern Plotly Chart Components for Startup Analyzer AI.
Includes dark glassmorphism styling, vibrant gradients, and clean data storytelling.
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
    """Create a sleek circular efficiency score gauge with dark theme aesthetics."""
    score = max(0, min(100, float(score)))

    # Determine status & dynamic accent color
    if score >= 75:
        tier_color = "#10B981"  # Emerald
        tier_text = "High Efficiency"
    elif score >= 50:
        tier_color = "#3B82F6"  # Blue
        tier_text = "Moderate Efficiency"
    elif score >= 30:
        tier_color = "#F59E0B"  # Amber
        tier_text = "Needs Optimization"
    else:
        tier_color = "#EF4444"  # Red
        tier_text = "Critical Risk"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={
            "suffix": "/100",
            "font": {"size": 42, "family": "Outfit, sans-serif", "color": "#FFFFFF", "weight": 700}
        },
        title={
            "text": f"<b>Overall Efficiency Score</b><br><span style='font-size:0.85em;color:{tier_color}'>{tier_text}</span>",
            "font": {"size": 17, "family": "Outfit, sans-serif", "color": "#CBD5E1"}
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#475569",
                "tickfont": {"size": 11, "color": "#94A3B8"}
            },
            "bar": {"color": tier_color, "thickness": 0.28},
            "bgcolor": "rgba(255, 255, 255, 0.04)",
            "borderwidth": 1,
            "bordercolor": "rgba(255, 255, 255, 0.1)",
            "steps": [
                {"range": [0, 30], "color": "rgba(239, 68, 68, 0.15)"},
                {"range": [30, 50], "color": "rgba(245, 158, 11, 0.15)"},
                {"range": [50, 75], "color": "rgba(59, 130, 246, 0.15)"},
                {"range": [75, 100], "color": "rgba(16, 185, 129, 0.18)"}
            ],
            "threshold": {
                "line": {"color": "#FFFFFF", "width": 3},
                "thickness": 0.8,
                "value": score
            }
        }
    ))

    fig.update_layout(
        height=330,
        margin=dict(t=65, b=20, l=30, r=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Plus Jakarta Sans, sans-serif", "color": "#FAFAFA"}
    )
    return fig


def create_radar_chart(target_metrics: dict, benchmark_metrics: dict, metrics_list: list) -> go.Figure:
    """Create a dual-polygon radar chart comparing the startup against peer medians."""
    categories = [METRIC_PRETTY_NAMES.get(m, m.replace("_", " ").title()) for m in metrics_list]

    target_values = []
    bench_values = []

    for m in metrics_list:
        t_val = float(target_metrics.get(m, 0) or 0)
        b_mean = float(benchmark_metrics.get(m, {}).get("mean", 1) or 1)
        if b_mean == 0:
            b_mean = 0.01

        # Normalized ratio (1.0 = matches benchmark, capped between 0 and 2.2 for visual clarity)
        ratio = min(2.2, max(0.0, t_val / b_mean))
        target_values.append(round(ratio, 2))
        bench_values.append(1.0)  # Peer baseline normalized to 1.0

    # Close polygons
    categories_closed = categories + [categories[0]]
    target_closed = target_values + [target_values[0]]
    bench_closed = bench_values + [bench_values[0]]

    fig = go.Figure()

    # Peer Baseline Area
    fig.add_trace(go.Scatterpolar(
        r=bench_closed,
        theta=categories_closed,
        fill="toself",
        name="Peer Average (Baseline)",
        line=dict(color="#64748B", width=1.8, dash="dot"),
        fillcolor="rgba(100, 116, 139, 0.18)",
        hoverinfo="theta+name"
    ))

    # Target Startup Area
    fig.add_trace(go.Scatterpolar(
        r=target_closed,
        theta=categories_closed,
        fill="toself",
        name="Your Startup",
        line=dict(color="#6366F1", width=2.6),
        fillcolor="rgba(99, 102, 241, 0.35)",
        hoverinfo="theta+r+name"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 2.2],
                tickvals=[0.5, 1.0, 1.5, 2.0],
                ticktext=["50%", "100% (Avg)", "150%", "200%"],
                tickfont=dict(size=10, color="#64748B"),
                gridcolor="rgba(255, 255, 255, 0.08)",
                linecolor="rgba(255, 255, 255, 0.1)"
            ),
            angularaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.08)",
                linecolor="rgba(255, 255, 255, 0.1)",
                tickfont=dict(size=11, color="#CBD5E1", family="Plus Jakarta Sans, sans-serif")
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(color="#CBD5E1", size=12)
        ),
        margin=dict(t=30, b=50, l=40, r=40),
        paper_bgcolor="rgba(0,0,0,0)",
        height=380,
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#FAFAFA")
    )
    return fig


def create_deviation_bar_chart(deviations: list) -> go.Figure:
    """Create a horizontal diverging bar chart showing metric Z-scores vs peer benchmarks."""
    if not deviations:
        return go.Figure()

    # Sort by absolute Z-score (most significant first, top 8)
    sorted_devs = sorted(deviations, key=lambda x: abs(x.get("z_score", 0)), reverse=True)[:8]

    labels = [d.get("label", d.get("metric", "")) for d in sorted_devs]
    z_scores = [round(d.get("z_score", 0), 2) for d in sorted_devs]

    colors = []
    for d in sorted_devs:
        if d.get("is_favorable", False):
            colors.append("#10B981")  # Emerald
        elif d.get("severity") == "critical":
            colors.append("#EF4444")  # Red
        else:
            colors.append("#F59E0B")  # Amber

    fig = go.Figure(go.Bar(
        x=z_scores,
        y=labels,
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(color="rgba(255, 255, 255, 0.2)", width=1)
        ),
        text=[f"{z:+.2f}σ" for z in z_scores],
        textposition="outside",
        textfont=dict(color="#CBD5E1", size=11)
    ))

    fig.update_layout(
        title=dict(
            text="<b>Key Metric Deviations (Z-Scores vs Peers)</b>",
            font=dict(size=15, family="Outfit, sans-serif", color="#CBD5E1")
        ),
        xaxis=dict(
            title=dict(text="Standard Deviations from Peer Mean (σ)", font=dict(size=11, color="#64748B")),
            gridcolor="rgba(255, 255, 255, 0.06)",
            zerolinecolor="rgba(255, 255, 255, 0.2)",
            tickfont=dict(color="#94A3B8")
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(color="#CBD5E1", size=11)
        ),
        height=320,
        margin=dict(t=50, b=40, l=120, r=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif")
    )
    return fig


def create_cost_breakdown_donut(cogs: float, opex: float, marketing: float) -> go.Figure:
    """Create a sleek donut chart visualizing operating expense distribution."""
    # Ensure opex covers overhead minus marketing if marketing is a subset
    other_opex = max(0, opex - marketing)

    labels = ["Cost of Goods (COGS)", "Sales & Marketing", "Other OpEx (Salaries/G&A)"]
    values = [max(0, cogs), max(0, marketing), max(0, other_opex)]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(
            colors=["#F43F5E", "#8B5CF6", "#06B6D4"],
            line=dict(color="#0B0F17", width=2)
        ),
        textinfo="percent+label",
        textfont=dict(size=11, color="#F8FAFC"),
        hoverinfo="label+value+percent"
    ))

    fig.update_layout(
        showlegend=False,
        height=260,
        margin=dict(t=20, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#CBD5E1")
    )
    return fig
