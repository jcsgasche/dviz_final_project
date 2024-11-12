import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html

# Lade die CSV-Daten (ersetze den Dateipfad durch den tatsächlichen Pfad)
data = pd.read_csv('../data/JanickSteffen_2024-09.csv')

# Auswahl relevanter Spalten für die beiden Analysen
activity_stress_columns = [
    'activeKilocalories', 'activeSeconds', 'activityStressDuration',
    'activityStressPercentage', 'averageStressLevel', 'vigorousIntensityMinutes'
]
sleep_wellness_columns = [
    'averageMonitoringEnvironmentAltitude', 'averageSpo2', 'avgWakingRespirationValue',
    'wellnessActiveKilocalories', 'wellnessKilocalories'
]

# Daten für Korrelation bereinigen
activity_stress_data = data[activity_stress_columns].dropna()
sleep_wellness_data = data[sleep_wellness_columns].dropna()

# Korrelationsmatrix berechnen
activity_stress_corr = activity_stress_data.corr()
sleep_wellness_corr = sleep_wellness_data.corr()

# Dash App erstellen
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Interaktive Heatmaps der Gesundheits- und Aktivitätsdaten"),

    html.H2("Korrelationen zwischen Aktivitätsmetriken und Stress"),
    dcc.Graph(
        id='activity-stress-heatmap',
        figure=px.imshow(activity_stress_corr, text_auto=True,
                         title="Aktivitätsmetriken und Stress", color_continuous_scale="Viridis")
    ),

    html.H2("Zusammenhang von Schlafparametern und Wellnessmetriken"),
    dcc.Graph(
        id='sleep-wellness-heatmap',
        figure=px.imshow(sleep_wellness_corr, text_auto=True,
                         title="Schlafparameter und Wellnessmetriken", color_continuous_scale="Cividis")
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
