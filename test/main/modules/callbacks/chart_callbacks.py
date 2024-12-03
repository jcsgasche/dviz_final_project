# modules/callbacks/chart_callbacks.py
from dash import Input, Output, State
import pandas as pd
from modules.charts.barchart import create_activity_chart

def register_barchart_callbacks(app):
    @app.callback(
        Output('activity-graph', 'figure'),
        [Input('metric-selector', 'value'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('set-goal-button', 'n_clicks'),
         Input('activity-graph', 'relayoutData'),
         Input('stored-data', 'data')],
        [State('goal-input', 'value')]
    )
    def update_chart(selected_metric, start_date, end_date, n_clicks, relayout_data, stored_data, goal_value):
        if not stored_data:
            return {}

        df = pd.DataFrame(stored_data)
        df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])
        goal_value = goal_value if goal_value and n_clicks else 500

        if relayout_data and 'xaxis.range[0]' in relayout_data:
            start_date = relayout_data['xaxis.range[0]'][:10]
            end_date = relayout_data['xaxis.range[1]'][:10]

        return create_activity_chart(df, selected_metric, start_date, end_date, goal_value)