import json
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, Optional, Tuple

def parse_visualization_data(text: str) -> Tuple[Optional[Dict], str]:
    """
    Extract visualization JSON from LLM response.
    Format: [VISUALIZE: {...json data...}]
    Returns: (visualization_data, cleaned_text)
    """
    import re

    # Find the VISUALIZE tag
    start_pattern = r'\[VISUALIZE:\s*'
    match = re.search(start_pattern, text)

    if not match:
        return None, text

    # Find the matching closing bracket by counting braces
    start_pos = match.end()
    brace_count = 0
    in_string = False
    escape_next = False
    json_end = -1

    for i, char in enumerate(text[start_pos:], start=start_pos):
        if escape_next:
            escape_next = False
            continue

        if char == '\\':
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break
            elif char == ']' and brace_count == 0:
                json_end = i
                break

    if json_end == -1:
        return None, text

    json_str = text[start_pos:json_end]

    try:
        viz_data = json.loads(json_str)
        # Remove the entire [VISUALIZE: ...] tag from text
        full_tag = text[match.start():json_end + 1]
        cleaned_text = text.replace(full_tag, '', 1).strip()
        return viz_data, cleaned_text
    except json.JSONDecodeError as e:
        # If parsing fails, return original text
        return None, text


def create_ecoscore_breakdown_chart(data: Dict[str, Any]) -> go.Figure:
    """Create a radar chart showing EcoScore breakdown by category."""
    categories = data.get('categories', [])
    scores = data.get('scores', [])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        fillcolor='rgba(183, 210, 146, 0.4)',
        line=dict(color='#9cb87a', width=2),
        marker=dict(size=8, color='#B7D292'),
        name='Score'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10),
                gridcolor='#e8f1e1'
            ),
            angularaxis=dict(
                tickfont=dict(size=11, family='Inter')
            )
        ),
        showlegend=False,
        title=dict(
            text=data.get('title', 'EcoScore Breakdown'),
            font=dict(size=16, family='Poppins', color='#2d3436'),
            x=0.5,
            xanchor='center'
        ),
        height=400,
        margin=dict(l=80, r=80, t=80, b=40),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )

    return fig


def create_bar_chart(data: Dict[str, Any]) -> go.Figure:
    """Create a horizontal bar chart for comparisons."""
    labels = data.get('labels', [])
    values = data.get('values', [])
    colors = data.get('colors', ['#B7D292'] * len(values))

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=labels,
        x=values,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='#2d3436', width=0.5)
        ),
        text=values,
        textposition='auto',
        textfont=dict(size=11, color='#2d3436')
    ))

    fig.update_layout(
        title=dict(
            text=data.get('title', 'Comparison'),
            font=dict(size=16, family='Poppins', color='#2d3436'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(
                text=data.get('x_label', ''),
                font=dict(size=12, family='Inter')
            ),
            gridcolor='#e8f1e1'
        ),
        yaxis=dict(
            title='',
        ),
        height=400,
        margin=dict(l=150, r=40, t=80, b=60),
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=False
    )

    return fig


def create_gauge_chart(data: Dict[str, Any]) -> go.Figure:
    """Create a gauge chart for showing a single score."""
    score = data.get('score', 0)
    title = data.get('title', 'Score')

    # Determine color based on score
    if score >= 85:
        color = '#4CAF50'
    elif score >= 70:
        color = '#8BC34A'
    elif score >= 65:
        color = '#FFC107'
    elif score >= 30:
        color = '#FF9800'
    else:
        color = '#F44336'

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'family': 'Poppins', 'color': '#2d3436'}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#2d3436"},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': '#e8f1e1',
            'steps': [
                {'range': [0, 30], 'color': '#ffebee'},
                {'range': [30, 65], 'color': '#fff3e0'},
                {'range': [65, 70], 'color': '#fff9c4'},
                {'range': [70, 85], 'color': '#e8f5e9'},
                {'range': [85, 100], 'color': '#c8e6c9'}
            ],
            'threshold': {
                'line': {'color': "#2d3436", 'width': 3},
                'thickness': 0.75,
                'value': score
            }
        }
    ))

    fig.update_layout(
        height=350,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor='white',
        font={'family': 'Inter'}
    )

    return fig


def create_pie_chart(data: Dict[str, Any]) -> go.Figure:
    """Create a pie chart for distribution visualization."""
    labels = data.get('labels', [])
    values = data.get('values', [])

    colors = ['#B7D292', '#9cb87a', '#8aa66b', '#78925c', '#667d4d']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textfont=dict(size=12, family='Inter'),
        hole=0.3
    )])

    fig.update_layout(
        title=dict(
            text=data.get('title', 'Distribution'),
            font=dict(size=16, family='Poppins', color='#2d3436'),
            x=0.5,
            xanchor='center'
        ),
        height=400,
        margin=dict(l=40, r=40, t=80, b=40),
        paper_bgcolor='white',
        showlegend=True,
        legend=dict(
            font=dict(size=11, family='Inter')
        )
    )

    return fig


def create_line_chart(data: Dict[str, Any]) -> go.Figure:
    """Create a line chart for trends over time."""
    x_values = data.get('x', [])
    y_values = data.get('y', [])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_values,
        y=y_values,
        mode='lines+markers',
        line=dict(color='#9cb87a', width=3),
        marker=dict(size=8, color='#B7D292', line=dict(color='#2d3436', width=1)),
        fill='tozeroy',
        fillcolor='rgba(183, 210, 146, 0.2)'
    ))

    fig.update_layout(
        title=dict(
            text=data.get('title', 'Trend'),
            font=dict(size=16, family='Poppins', color='#2d3436'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(
                text=data.get('x_label', ''),
                font=dict(size=12, family='Inter')
            ),
            gridcolor='#e8f1e1'
        ),
        yaxis=dict(
            title=dict(
                text=data.get('y_label', ''),
                font=dict(size=12, family='Inter')
            ),
            gridcolor='#e8f1e1'
        ),
        height=400,
        margin=dict(l=60, r=40, t=80, b=60),
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=False
    )

    return fig


def render_visualization(viz_data: Dict[str, Any]) -> Optional[go.Figure]:
    """
    Route to appropriate chart renderer based on chart type.

    Expected format:
    {
        "type": "radar|bar|gauge|pie|line",
        "data": {...chart specific data...}
    }
    """
    chart_type = viz_data.get('type', '').lower()
    chart_data = viz_data.get('data', {})

    if chart_type == 'radar':
        return create_ecoscore_breakdown_chart(chart_data)
    elif chart_type == 'bar':
        return create_bar_chart(chart_data)
    elif chart_type == 'gauge':
        return create_gauge_chart(chart_data)
    elif chart_type == 'pie':
        return create_pie_chart(chart_data)
    elif chart_type == 'line':
        return create_line_chart(chart_data)
    else:
        return None
