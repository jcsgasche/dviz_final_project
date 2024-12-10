from dash import Input, Output
import pandas as pd

def register_activity_breakdown_callbacks(app):
    @app.callback(
        Output('activity-breakdown-chart', 'figure'),
        [Input('breakdown-metric-selector', 'value'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('stored-data', 'data')]
    )
    def update_activity_breakdown(selected_metric, start_date, end_date, stored_data):
        if not stored_data:
            return {}

        df = pd.DataFrame(stored_data)
        df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])

        # Filter data for selected date range
        mask = (df['startTimeLocal'] >= start_date) & (df['startTimeLocal'] <= end_date)
        filtered_df = df.loc[mask]

        from modules.charts.activity_breakdown import create_activity_breakdown_chart
        return create_activity_breakdown_chart(filtered_df, selected_metric)