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
         Output('muscle-map-image', 'src'),
         Output('muscle-spider-chart', 'figure')],
        [Input('strength-data-store', 'data'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('stored-data', 'modified_timestamp')],  # Add this to trigger on data load
        [State('stored-data', 'data')]  # Add this to access persisted data
    )
    def update_muscle_visualizations(raw_data, start_date, end_date, ts, stored_data):
        if not raw_data:
            # Create empty muscle map image
            script_dir = os.path.dirname(os.path.abspath(__file__))
            coordinates_path = os.path.join(script_dir, '..', 'charts', 'musclemap', 'data', 'muscle_coordinates.json')
            muscle_coordinates = musclemap_plot.load_and_parse_muscle_coordinates(coordinates_path)
            empty_img = musclemap_plot.create_empty_muscle_map(
                muscle_coordinates,
                zoom_out_factor=1.5,
                message="Waiting for you to add your personal fitness data"
            )
            empty_src = f"data:image/png;base64,{empty_img}"
            return None, empty_src, create_empty_spider_chart()

        try:
            strength_activities = json.loads(raw_data)
        except (json.JSONDecodeError, TypeError):
            return None, None, create_empty_spider_chart("Error processing data")

        # Filter activities by date range
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
            # Create empty muscle map with no data message
            script_dir = os.path.dirname(os.path.abspath(__file__))
            coordinates_path = os.path.join(script_dir, '..', 'charts', 'musclemap', 'data', 'muscle_coordinates.json')
            muscle_coordinates = musclemap_plot.load_and_parse_muscle_coordinates(coordinates_path)
            empty_img = musclemap_plot.create_empty_muscle_map(
                muscle_coordinates,
                zoom_out_factor=1.5,
                message="No data available in this period of time"
            )
            empty_src = f"data:image/png;base64,{empty_img}"
            return None, empty_src, create_empty_spider_chart("No data available in this period of time")

        # Process the filtered activities
        processed_data = musclemap_load.process_strength_activities(filtered_activities)

        # Generate muscle map image
        script_dir = os.path.dirname(os.path.abspath(__file__))
        coordinates_path = os.path.join(script_dir, '..', 'charts', 'musclemap', 'data', 'muscle_coordinates.json')
        muscle_coordinates = musclemap_plot.load_and_parse_muscle_coordinates(coordinates_path)

        img_data = musclemap_plot.plot_muscle_map(
            processed_data,
            muscle_coordinates,
            zoom_out_factor=1.5
        )

        img_src = f"data:image/png;base64,{img_data}"

        # Generate spider chart
        spider_fig = create_spider_chart(processed_data, start_date, end_date)

        return json.dumps(processed_data), img_src, spider_fig

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