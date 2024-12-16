from dash import Input, Output

def register_ui_callbacks(app):
    @app.callback(
        [Output('garmin-login', 'style'),
         Output('file-upload', 'style')],
        [Input('data-source', 'value')]
    )
    def toggle_data_source(selected_source):
        if selected_source == 'garmin':
            return {'display': 'block'}, {'display': 'none'}
        return {'display': 'none'}, {'display': 'block'}