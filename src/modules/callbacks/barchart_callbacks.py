# modules/callbacks/barchart_callbacks.py
from dash import Input, Output, State, callback_context, html, dcc, ALL
import pandas as pd
from modules.charts.barchart import create_activity_chart, get_default_goals, get_metric_units, create_summary_chart, METRIC_LABEL_MAP, create_empty_chart
import json
import dash

def register_barchart_callbacks(app):
    # Add callback for colorblind mode toggle
    @app.callback(
        Output('colorblind-mode', 'data'),
        Input('colorblind-toggle', 'value')
    )
    def update_colorblind_mode(value):
        return True if value else False

    @app.callback(
        [Output('initial-loading-div', 'style'),
         Output('data-loaded-div', 'style')],
        [Input('stored-data', 'data')]
    )
    def switch_layout_visibility(stored_data):
        if not stored_data:
            return {'display': 'block'}, {'display': 'none'}
        return {'display': 'none'}, {'display': 'block'}

    @app.callback(
        Output('activity-graph', 'figure'),
        [Input('metric-selector', 'value'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('stored-data', 'data'),
         Input('stored-goals', 'data'),
         Input('activity-graph', 'relayoutData'),
         Input('colorblind-mode', 'data')],  # Add colorblind mode input
        prevent_initial_call=True
    )
    def update_chart(selected_metric, start_date, end_date, stored_data, stored_goals,
                     relayout_data, colorblind_mode):
        if not stored_data or not stored_goals:
            return {}

        df = pd.DataFrame(stored_data)
        df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])

        goal_value = stored_goals.get(selected_metric, get_default_goals()[selected_metric])

        if relayout_data and 'xaxis.range[0]' in relayout_data:
            start_date = relayout_data['xaxis.range[0]'][:10]
            end_date = relayout_data['xaxis.range[1]'][:10]

        mask = (df['startTimeLocal'] >= start_date) & (df['startTimeLocal'] <= end_date)
        filtered_df = df.loc[mask]

        if len(filtered_df) == 0:
            return create_empty_chart("No data available<br>in this period of time")

        return create_activity_chart(filtered_df, selected_metric, start_date, end_date,
                                     goal_value, colorblind_mode)

    @app.callback(
        Output('summary-graph', 'figure'),
        [Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('stored-data', 'data'),
         Input('stored-goals', 'data'),
         Input('view-type', 'data'),
         Input('summary-type', 'value'),
         Input('summary-metrics-selector', 'value'),
         Input('colorblind-mode', 'data')],  # Add colorblind mode input
        prevent_initial_call=True
    )
    def update_summary_chart(start_date, end_date, stored_data, stored_goals,
                             view_type, summary_type, selected_metrics, colorblind_mode):
        if not stored_data or not stored_goals or view_type == 'detail':
            return create_empty_chart("Waiting for you to add<br>your personal fitness data")

        df = pd.DataFrame(stored_data)
        df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])

        mask = (df['startTimeLocal'] >= start_date) & (df['startTimeLocal'] <= end_date)
        filtered_df = df.loc[mask]

        if len(filtered_df) == 0:
            return create_empty_chart("No data available<br>in this period of time")

        metrics_to_show = selected_metrics if summary_type == 'custom' else None
        return create_summary_chart(filtered_df, start_date, end_date,
                                    stored_goals, metrics_to_show, colorblind_mode)

    @app.callback(
        Output({'type': 'goal-input', 'metric': 'quick-set'}, 'value', allow_duplicate=True),
        [Input('metric-selector', 'value')],
        [State('stored-goals', 'data')],
        prevent_initial_call=True
    )
    def update_quick_set_display(selected_metric, stored_goals):
        if not stored_goals:
            return get_default_goals()[selected_metric]
        return stored_goals.get(selected_metric, get_default_goals()[selected_metric])

    @app.callback(
        [Output('activity-graph', 'style'),
         Output('summary-graph', 'style'),
         Output('view-type', 'data'),
         Output('metric-selector-container', 'style'),
         Output('quick-goal-container', 'style'),
         Output('summary-controls', 'style')],  # Added this output
        [Input('toggle-summary-view', 'n_clicks')],
        [State('view-type', 'data')]
    )
    def toggle_view(n_clicks, current_view):
        if n_clicks is None:
            return ({'display': 'block'},
                    {'display': 'none'},
                    'detail',
                    {'width': '50%', 'marginBottom': '20px', 'display': 'block'},
                    {'display': 'block'},
                    {'display': 'none'})  # Hide summary controls initially

        if current_view == 'detail':
            return ({'display': 'none'},
                    {'display': 'block'},
                    'summary',
                    {'width': '50%', 'marginBottom': '20px', 'display': 'none'},
                    {'display': 'none'},
                    {'display': 'block'})  # Show summary controls
        else:
            return ({'display': 'block'},
                    {'display': 'none'},
                    'detail',
                    {'width': '50%', 'marginBottom': '20px', 'display': 'block'},
                    {'display': 'block'},
                    {'display': 'none'})  # Hide summary controls

    @app.callback(
        Output('summary-metrics-dropdown', 'style'),
        [Input('summary-type', 'value')]
    )
    def toggle_metrics_dropdown(summary_type):
        if summary_type == 'custom':
            return {'display': 'block'}
        return {'display': 'none'}

def create_goals_display(goals):
    """Create a formatted display of all current goals with editable inputs"""
    if not goals:
        return html.Div("No goals set")

    # Sort the metrics by their label rather than their key
    sorted_metrics = sorted(goals.keys(), key=lambda m: METRIC_LABEL_MAP.get(m, m))

    # Create table header
    header = html.Tr([
        html.Th("Metric", style={'width': '40%', 'textAlign': 'left'}),
        html.Th("Goal", style={'width': '30%', 'textAlign': 'left'}),
        html.Th("Units", style={'width': '30%', 'textAlign': 'left'})
    ])

    rows = []
    for metric in sorted_metrics:
        value = goals[metric]
        units = get_metric_units(metric)
        # Use the same label as in the dropdown
        metric_label = METRIC_LABEL_MAP.get(metric, metric.replace('_', ' ').title())

        row = html.Tr([
            html.Td(metric_label),
            html.Td(
                dcc.Input(
                    id={'type': 'goal-input', 'metric': metric},
                    type='number',
                    value=value,
                    style={
                        'width': '100px',
                        'padding': '5px',
                        'border': '1px solid #ddd',
                        'borderRadius': '4px'
                    }
                )
            ),
            html.Td(units)
        ], style={'borderBottom': '1px solid #eee'})

        rows.append(row)

    # Create table
    table = html.Table(
        [header] + rows,
        style={
            'width': '100%',
            'borderCollapse': 'collapse',
            'marginTop': '10px'
        }
    )

    return html.Div([
        table
    ], style={
        'maxHeight': '500px',
        'overflowY': 'auto',
        'padding': '15px',
        'border': '1px solid #ddd',
        'borderRadius': '5px',
        'marginTop': '10px',
        'backgroundColor': 'white'
    })