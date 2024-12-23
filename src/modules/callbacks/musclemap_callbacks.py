# modules/callbacks/musclemap_callbacks.py
from dash import Input, Output, State
import json
import datetime
import os
from modules.charts.musclemap import musclemap_load, musclemap_plot
from modules.charts.musclemap.musclemap import create_spider_chart, create_empty_spider_chart

def register_musclemap_callbacks(app):
    @app.callback(
        [Output('processed-strength-data-store', 'data'),
         Output('muscle-map-image', 'src')],
        [Input('strength-data-store', 'data'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('stored-data', 'modified_timestamp'),
         Input('global-colorblind-toggle', 'value')],  # Changed to correct ID
        [State('stored-data', 'data')]
    )
    def update_muscle_visualizations(raw_data, start_date, end_date, ts, colorblind_mode, stored_data):
        # Convert colorblind_mode from list to boolean
        colorblind_enabled = bool(colorblind_mode and True in colorblind_mode)

        if not raw_data:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            coordinates_path = os.path.join(script_dir, '..', 'charts', 'musclemap', 'data', 'muscle_coordinates.json')
            muscle_coordinates = musclemap_plot.load_and_parse_muscle_coordinates(coordinates_path)
            empty_img = musclemap_plot.create_empty_muscle_map(
                muscle_coordinates,
                zoom_out_factor=1.5,
                message="Waiting for you to add your personal fitness data",
                colorblind_mode=colorblind_enabled
            )
            empty_src = f"data:image/png;base64,{empty_img}"
            return None, empty_src

        try:
            strength_activities = json.loads(raw_data)
        except (json.JSONDecodeError, TypeError):
            return None, None

        filtered_activities = []
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        for activity in strength_activities:
            activity_date_str = activity.get('startTimeLocal', activity.get('startTimeGMT'))
            if not activity_date_str:
                continue

            try:
                activity_date = datetime.datetime.strptime(
                    activity_date_str.split('.')[0], '%Y-%m-%d %H:%M:%S'
                ).date()

                if start <= activity_date <= end:
                    filtered_activities.append(activity)
            except ValueError:
                continue

        if not filtered_activities:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            coordinates_path = os.path.join(script_dir, '..', 'charts', 'musclemap', 'data', 'muscle_coordinates.json')
            muscle_coordinates = musclemap_plot.load_and_parse_muscle_coordinates(coordinates_path)
            empty_img = musclemap_plot.create_empty_muscle_map(
                muscle_coordinates,
                zoom_out_factor=1.5,
                message="No data available in this period of time",
                colorblind_mode=colorblind_enabled
            )
            empty_src = f"data:image/png;base64,{empty_img}"
            return None, empty_src

        processed_data = musclemap_load.process_strength_activities(filtered_activities)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        coordinates_path = os.path.join(script_dir, '..', 'charts', 'musclemap', 'data', 'muscle_coordinates.json')
        muscle_coordinates = musclemap_plot.load_and_parse_muscle_coordinates(coordinates_path)

        img_data = musclemap_plot.plot_muscle_map(
            processed_data,
            muscle_coordinates,
            zoom_out_factor=1.5,
            colorblind_mode=colorblind_enabled
        )

        img_src = f"data:image/png;base64,{img_data}"

        return json.dumps(processed_data), img_src

    @app.callback(
        [Output('muscle-map-container', 'style'),
         Output('spider-chart-container', 'style'),
         Output('muscle-view-type', 'data')],
        [Input('toggle-muscle-view', 'n_clicks')],
        [State('muscle-view-type', 'data')]
    )
    def toggle_muscle_view(n_clicks, current_view):
        if n_clicks is None:
            return {'display': 'block'}, {'display': 'none'}, 'map'

        if current_view == 'map':
            return {'display': 'none'}, {'display': 'block'}, 'spider'
        else:
            return {'display': 'block'}, {'display': 'none'}, 'map'