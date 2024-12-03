import pandas as pd
import plotly.graph_objects as go
from dash import dcc

def generate_barchart(data):
    """Create a bar chart from the data."""
    df = pd.DataFrame(data)

    # Default goal value
    goal_value = 500

    # Split data into "Goal Reached" and "Goal Not Reached"
    goal_reached = df[df['Calories'] >= goal_value]
    goal_not_reached = df[df['Calories'] < goal_value]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=goal_reached['Date'],
        y=goal_reached['Calories'],
        marker_color='green',
        name='Goal Reached'
    ))

    fig.add_trace(go.Bar(
        x=goal_not_reached['Date'],
        y=goal_not_reached['Calories'],
        marker_color='red',
        name='Goal Not Reached'
    ))

    # Add goal line
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=[goal_value] * len(df),
        mode='lines',
        name='Goal',
        line=dict(color='blue', dash='dash')
    ))

    fig.update_layout(
        title="Calories Over Time",
        xaxis_title="Date",
        yaxis_title="Calories",
        barmode='group'
    )

    return dcc.Graph(figure=fig)
