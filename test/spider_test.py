import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

# Initialisiere die Dash-App
app = dash.Dash(__name__)

# Beispiel-Daten für den Spider Chart
categories = ["Strength", "Cycling", "Trail Running"]
values = [80, 90, 70]  # Beispielwerte

# App-Layout
app.layout = html.Div([
    html.H1("Spider Chart Beispiel mit Dash und Plotly"),
    dcc.RadioItems(
        id='activity-type',
        options=[{'label': category, 'value': category} for category in categories],
        value='Strength',
        inline=True
    ),
    dcc.Graph(id='spider-chart')
])

# Callback zur Aktualisierung des Spider Charts basierend auf der Auswahl
@app.callback(
    Output('spider-chart', 'figure'),
    [Input('activity-type', 'value')]
)
def update_spider_chart(selected_activity):
    # Beispielwerte für die verschiedenen Aktivitäten
    data = {
        "Strength": [70, 85, 65],
        "Cycling": [90, 70, 80],
        "Trail Running": [60, 80, 95]
    }
    values = data[selected_activity]

    fig = go.Figure(
        data=go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself'
        )
    )
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False
    )

    return fig

# Starte die App
if __name__ == '__main__':
    app.run_server(debug=True)
