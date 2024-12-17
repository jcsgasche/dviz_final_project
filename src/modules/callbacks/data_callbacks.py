# modules/callbacks/data_callbacks.py
import dash
from dash import Input, Output, State, html
import pandas as pd
import json
import base64
import io
from datetime import datetime
from garminconnect import Garmin

def register_data_callbacks(app):
    # Combined UI elements callback
    @app.callback(
        [Output('download-section', 'style', allow_duplicate=True),
         Output('clear-data-section', 'style', allow_duplicate=True),
         Output('last-update-display', 'children', allow_duplicate=True),
         Output('data-status-container', 'children', allow_duplicate=True),
         Output('garmin-login', 'style', allow_duplicate=True),
         Output('file-upload', 'style', allow_duplicate=True)],
        [Input('stored-data', 'modified_timestamp'),
         Input('last-update-time', 'data'),
         Input('data-source', 'value')],
        [State('stored-data', 'data')],
        prevent_initial_call=True
    )
    def update_all_ui_elements(ts, last_update, data_source, stored_data):
        # Base styles for sections that depend on stored data
        display_style = {'marginTop': '20px', 'display': 'block'} if stored_data else {'display': 'none'}

        # Data source specific styles
        garmin_style = {'display': 'block'} if data_source == 'garmin' else {'display': 'none'}
        file_style = {'display': 'block'} if data_source != 'garmin' else {'display': 'none'}

        # Common message style
        message_style = {
            'fontWeight': '500',
            'padding': '10px',
            'borderRadius': '4px',
            'textAlign': 'center',
            'width': '100%'
        }

        # Status messages with consistent styling
        last_update_text = f"Last updated: {last_update}" if last_update else ""

        if stored_data:
            status_message = html.Div("Data loaded successfully.",
                                      style={
                                          **message_style,
                                          'color': '#28a745',  # Bootstrap success green
                                          'backgroundColor': '#f8f9f8'
                                      })
        else:
            status_message = html.Div("Ready to fetch data",
                                      style={
                                          **message_style,
                                          'color': '#6c757d',  # Bootstrap secondary gray
                                          'backgroundColor': '#f8f9fa'
                                      })

        return (
            display_style,           # download section style
            display_style,           # clear data section style
            last_update_text,        # last update display
            status_message,          # data status container
            garmin_style,           # garmin login style
            file_style              # file upload style
        )

    @app.callback(
        [Output('stored-data', 'data'),
         Output('strength-data-store', 'data'),
         Output('last-update-time', 'data'),
         Output('upload-data', 'contents')],
        [Input('fetch-button', 'n_clicks'),
         Input('upload-data', 'contents'),
         Input('clear-data-button', 'n_clicks')],
        [State('garmin-email', 'value'),
         State('garmin-password', 'value'),
         State('data-source', 'value'),
         State('upload-data', 'filename')]
    )
    def update_data(n_clicks, upload_contents, clear_clicks,
                    username, password, data_source, filename):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        # Handle clear data button
        if trigger_id == 'clear-data-button' and clear_clicks:
            return None, None, None, None

        # Handle file upload
        if trigger_id == 'upload-data' and upload_contents:
            try:
                content_type, content_string = upload_contents.split(',')
                decoded = base64.b64decode(content_string)

                if 'json' in filename.lower():
                    data = json.loads(decoded)
                    all_activities = []
                    strength_activities = []

                    activities_list = data if isinstance(data, list) else [data]

                    for activity in activities_list:
                        if 'summarizedExerciseSets' in activity:
                            strength_activities.append(activity)
                        all_activities.append(activity)

                    activities_df = pd.DataFrame(all_activities)
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    return (
                        activities_df.to_dict('records'),
                        json.dumps(strength_activities),
                        current_time,
                        None  # Reset upload contents
                    )
                else:
                    return None, None, None, None

            except Exception as e:
                print(f"Error processing file: {str(e)}")
                return None, None, None, None

        # Handle Garmin fetch
        if trigger_id == 'fetch-button' and n_clicks:
            if not username or not password:
                return None, None, None, dash.no_update

            try:
                api = Garmin(username, password)
                api.login()

                start = 0
                limit = 100
                all_activities = []
                strength_activities = []
                more_activities = True

                while more_activities:
                    batch = api.get_activities(start, limit)
                    if not batch:
                        break

                    for activity in batch:
                        if activity.get('activityType', {}).get('typeKey') == 'strength_training':
                            strength_activities.append(activity)
                        all_activities.append(activity)

                    if len(batch) < limit:
                        break
                    start += limit

                activities_df = pd.DataFrame(all_activities)
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                return (
                    activities_df.to_dict('records'),
                    json.dumps(strength_activities),
                    current_time,
                    dash.no_update
                )

            except Exception as e:
                return None, None, None, dash.no_update

        raise dash.exceptions.PreventUpdate

    @app.callback(
        Output("download-data", "data"),
        Input("btn-download", "n_clicks"),
        [State("download-type", "value"),
         State("stored-data", "data"),
         State("strength-data-store", "data")],
        prevent_initial_call=True
    )
    def download_data(n_clicks, download_type, all_data, strength_data):
        if not n_clicks:
            raise dash.exceptions.PreventUpdate

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if download_type == 'all' and all_data:
            return dict(
                content=json.dumps(all_data, indent=2),
                filename=f"garmin_activities_{timestamp}.json"
            )
        elif download_type == 'strength' and strength_data:
            return dict(
                content=strength_data,
                filename=f"garmin_strength_activities_{timestamp}.json"
            )

        return None

    @app.callback(
        [Output('garmin-login', 'style'),
         Output('file-upload', 'style')],
        [Input('data-source', 'value')]
    )
    def toggle_input_visibility(data_source):
        if data_source == 'garmin':
            return {'display': 'block'}, {'display': 'none'}
        return {'display': 'none'}, {'display': 'block'}

    @app.callback(
        [Output('download-section', 'style'),
         Output('clear-data-section', 'style'),
         Output('last-update-display', 'children')],
        [Input('stored-data', 'data'),
         Input('last-update-time', 'data')]
    )
    def update_ui_elements(data, last_update):
        if data:
            display_style = {'marginTop': '20px', 'display': 'block'}
            last_update_text = f"Last updated: {last_update}" if last_update else ""
            return display_style, display_style, last_update_text
        return {'display': 'none'}, {'display': 'none'}, ""