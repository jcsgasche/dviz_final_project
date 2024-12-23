from dash import Input, Output
import pandas as pd

def register_activity_breakdown_callbacks(app):
    @app.callback(
        Output('activity-breakdown-chart', 'figure'),
        [Input('breakdown-metric-selector', 'value'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('stored-data', 'data'),
         Input('global-colorblind-toggle', 'value')]  # Add colorblind toggle input
    )
    def update_activity_breakdown(selected_metric, start_date, end_date, stored_data, colorblind_mode):
        # Convert colorblind_mode from list to boolean
        colorblind_enabled = bool(colorblind_mode and True in colorblind_mode)

        if not stored_data:
            from modules.charts.activity_breakdown import create_activity_breakdown_chart
            return create_activity_breakdown_chart(None, selected_metric, colorblind_enabled)

        try:
            # Handle data whether it's a string or already a list
            if isinstance(stored_data, str):
                df = pd.DataFrame(json.loads(stored_data))
            else:
                df = pd.DataFrame(stored_data)

            df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])

            # Filter data for selected date range
            mask = (df['startTimeLocal'] >= start_date) & (df['startTimeLocal'] <= end_date)
            filtered_df = df.loc[mask]

            from modules.charts.activity_breakdown import create_activity_breakdown_chart
            return create_activity_breakdown_chart(filtered_df, selected_metric, colorblind_enabled)

        except Exception as e:
            print(f"Error updating activity breakdown: {e}")
            from modules.charts.activity_breakdown import create_activity_breakdown_chart
            return create_activity_breakdown_chart(None, selected_metric, colorblind_enabled)

    @app.callback(
        Output('breakdown-metric-container', 'style'),
        [Input('stored-data', 'data')]
    )
    def toggle_breakdown_metric_selector(stored_data):
        if stored_data:
            return {'marginBottom': '20px', 'marginTop': '10px', 'display': 'block'}
        else:
            return {'display': 'none'}