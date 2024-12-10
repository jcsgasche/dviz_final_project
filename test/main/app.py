from dash import Dash, html
import json
from pathlib import Path
from modules.charts.barchart import create_barchart_layout
from modules.charts.activity_breakdown import create_activity_breakdown_layout
from modules.utils import calculate_date_range, create_general_layout
from modules.callbacks.data_callbacks import register_data_callbacks
from modules.callbacks.ui_callbacks import register_ui_callbacks
from modules.callbacks.barchart_callbacks import register_barchart_callbacks
from modules.callbacks.activity_breakdown_callbacks import register_activity_breakdown_callbacks

app = Dash(__name__)
first_day_last_month, last_day_last_month = calculate_date_range()

app.layout = html.Div([
    create_general_layout(),
    create_barchart_layout(first_day_last_month, last_day_last_month),
    create_activity_breakdown_layout()
])

register_data_callbacks(app)
register_ui_callbacks(app)
register_barchart_callbacks(app)
register_activity_breakdown_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)