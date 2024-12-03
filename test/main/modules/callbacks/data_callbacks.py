# modules/callbacks/data_callbacks.py
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
import dash
from modules.data_loader import fetch_garmin_data, process_uploaded_file

def register_data_callbacks(app):
    @app.callback(
        [Output('stored-data', 'data'),
         Output('garmin-status', 'children'),
         Output('upload-status', 'children')],
        [Input('fetch-button', 'n_clicks'),
         Input('upload-data', 'contents')],
        [State('garmin-email', 'value'),
         State('garmin-password', 'value'),
         State('data-source', 'value'),
         State('upload-data', 'filename')]
    )
    def handle_data_sources(fetch_clicks, upload_contents, email, password, data_source, upload_filename):
        ctx = dash.callback_context
        if not ctx.triggered:
            raise PreventUpdate

        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        stored_data = dash.no_update
        garmin_message = dash.no_update
        upload_message = dash.no_update

        if triggered_id == 'fetch-button' and data_source == 'garmin':
            if not email or not password:
                return stored_data, "Please provide both email and password.", dash.no_update

            df, message = fetch_garmin_data(email, password)
            return df.to_dict(orient='records') if not df.empty else stored_data, message, dash.no_update

        elif triggered_id == 'upload-data' and data_source == 'upload':
            if not upload_contents:
                return stored_data, dash.no_update, "No file uploaded."

            df, message = process_uploaded_file(upload_contents, upload_filename)
            return df.to_dict(orient='records') if df is not None else stored_data, dash.no_update, message

        raise PreventUpdate
