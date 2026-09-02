import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_efficiency_gauge(score: float):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Overall Efficiency Score"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#10B981" if score > 70 else "#F59E0B" if score > 40 else "#EF4444"},
            'steps': [
                {'range': [0, 40], 'color': "rgba(239, 68, 68, 0.2)"},
                {'range': [40, 70], 'color': "rgba(245, 158, 11, 0.2)"},
                {'range': [70, 100], 'color': "rgba(16, 185, 129, 0.2)"}
            ]
        }
    ))
    fig.update_layout(height=350, margin=dict(t=50, b=10, l=10, r=10), paper_bgcolor="rgba(0,0,0,0)", font={'color': "#FAFAFA"})
    return fig

def create_radar_chart(target_metrics: dict, benchmark_metrics: dict, metrics_list: list):
    categories = metrics_list
    
    target_values = []
    bench_values = []
    
    for m in categories:
        # We need to scale these to a relative percentage (target / benchmark) or Z-score for plotting
        t_val = target_metrics.get(m, 0)
        b_mean = benchmark_metrics.get(m, {}).get("mean", 1)
        if b_mean == 0: b_mean = 0.01
        
        # Simple ratio capped at 2.0 (200%) for radar visibility
        ratio = min(2.0, max(0.0, t_val / b_mean))
        target_values.append(ratio)
        bench_values.append(1.0) # Benchmark is always 1.0 (100%)

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=target_values,
        theta=categories,
        fill='toself',
        name='Your Startup',
        line_color='#3B82F6'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=bench_values,
        theta=categories,
        fill='toself',
        name='Peer Average',
        line_color='#9CA3AF'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 2]),
            bgcolor="rgba(0,0,0,0)"
        ),
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#FAFAFA"},
        height=500
    )
    return fig
