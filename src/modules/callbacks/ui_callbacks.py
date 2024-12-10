# modules/callbacks/ui_callbacks.py
from dash import Input, Output, State
import dash
from dash.exceptions import PreventUpdate

def register_ui_callbacks(app):
    @app.callback(
        [Output('garmin-login', 'style'),
         Output('file-upload', 'style'),
         Output('refresh-section', 'style')],
        [Input('data-source', 'value')]
    )
    def toggle_data_source(selected_source):
        if selected_source == 'garmin':
            return {'display': 'block'}, {'display': 'none'}, {'display': 'block', 'margin-bottom': '20px'}
        return {'display': 'none'}, {'display': 'block'}, {'display': 'none'}

    @app.callback(
        Output('fetch-button', 'n_clicks'),
        [Input('refresh-button', 'n_clicks')],
        [State('data-source', 'value')]
    )
    def refresh_data(n_clicks_refresh, data_source):
        if data_source != 'garmin' or not n_clicks_refresh:
            raise PreventUpdate
        return n_clicks_refresh + 1