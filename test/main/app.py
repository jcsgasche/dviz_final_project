# app.py updates
from dash import Dash, html
from modules.charts.barchart import create_barchart_layout
from modules.charts.chart import create_chart_layout
from modules.utils import calculate_date_range
from modules.callbacks.data_callbacks import register_data_callbacks
from modules.callbacks.ui_callbacks import register_ui_callbacks
from modules.callbacks.chart_callbacks import register_barchart_callbacks

app = Dash(__name__)
first_day_last_month, last_day_last_month = calculate_date_range()

app.layout = html.Div([
    (create_barchart_layout(first_day_last_month, last_day_last_month)),
    (create_chart_layout(first_day_last_month, last_day_last_month)),
])

register_data_callbacks(app)
register_ui_callbacks(app)
register_barchart_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)