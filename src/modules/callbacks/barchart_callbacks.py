from dash import Input, Output, State, callback_context, html, dcc, ALL
import pandas as pd
from modules.charts.barchart import create_activity_chart, get_default_goals, get_metric_units, create_summary_chart, METRIC_LABEL_MAP, create_empty_chart
import json

def register_barchart_callbacks(app):
    @app.callback(
        [Output('stored-goals', 'data'),
         Output('current-goals-display', 'children'),
         Output({'type': 'goal-input', 'metric': ALL}, 'value')],
        [Input('reset-goals-button', 'n_clicks'),
         Input({'type': 'goal-input', 'metric': ALL}, 'value')],
        [State({'type': 'goal-input', 'metric': ALL}, 'id'),
         State('metric-selector', 'value'),
         State('stored-goals', 'data')]
    )
    def update_goals(reset_clicks, goal_values, input_ids, selected_metric, stored_goals):
        ctx = callback_context
        if not ctx.triggered:
            updated_values = []
            for input_id in input_ids:
                if input_id['metric'] == 'quick-set':
                    updated_values.append(stored_goals.get(selected_metric, get_default_goals()[selected_metric]))
                else:
                    updated_values.append(stored_goals.get(input_id['metric'], get_default_goals()[input_id['metric']]))
            return stored_goals, create_goals_display(stored_goals), updated_values

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'reset-goals-button':
            stored_goals = get_default_goals()
        else:
            stored_goals = stored_goals or get_default_goals()
            trigger_dict = json.loads(trigger_id)

            trigger_index = next(i for i, id_dict in enumerate(input_ids) if id_dict == trigger_dict)
            new_value = goal_values[trigger_index]

            if new_value is not None:
                metric = trigger_dict['metric']
                if metric == 'quick-set':
                    stored_goals[selected_metric] = float(new_value)
                else:
                    stored_goals[metric] = float(new_value)

        updated_values = []
        for input_id in input_ids:
            if input_id['metric'] == 'quick-set':
                updated_values.append(stored_goals.get(selected_metric, get_default_goals()[selected_metric]))
            else:
                updated_values.append(stored_goals.get(input_id['metric'], get_default_goals()[input_id['metric']]))

        return stored_goals, create_goals_display(stored_goals), updated_values

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
        Output("activity-graph", "figure"),
        [Input('stored-data', 'data'),
         Input('metric-selector', 'value'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('stored-goals', 'data'),
         Input('global-colorblind-toggle', 'value')]
    )
    def update_activity_graph(data, selected_metric, start_date, end_date, stored_goals, colorblind_mode):
        if data is None:
            return create_empty_chart("Waiting for you to add<br>your personal fitness data")

        colorblind_enabled = bool(colorblind_mode and True in colorblind_mode)

        try:
            if isinstance(data, str):
                df = pd.read_json(data)
            else:
                df = pd.DataFrame(data)

            goal_value = stored_goals.get(selected_metric, get_default_goals()[selected_metric])
            return create_activity_chart(df, selected_metric, start_date, end_date, goal_value, colorblind_enabled)
        except Exception as e:
            print(f"Error updating activity graph: {e}")
            return create_empty_chart("Error loading data")

    @app.callback(
        Output("summary-graph", "figure"),
        [Input('stored-data', 'data'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('stored-goals', 'data'),
         Input('summary-type', 'value'),
         Input('summary-metrics-selector', 'value'),
         Input('global-colorblind-toggle', 'value')]
    )
    def update_summary_graph(data, start_date, end_date, stored_goals, summary_type, selected_metrics, colorblind_mode):
        if data is None:
            return create_empty_chart("Waiting for you to add<br>your personal fitness data")

        colorblind_enabled = bool(colorblind_mode and True in colorblind_mode)

        try:
            if isinstance(data, str):
                df = pd.DataFrame(json.loads(data))
            else:
                df = pd.DataFrame(data)

            metrics_to_show = None if summary_type == 'all' else selected_metrics
            return create_summary_chart(df, start_date, end_date, stored_goals, metrics_to_show, colorblind_enabled)
        except Exception as e:
            print(f"Error updating summary graph: {e}")
            return create_empty_chart("Error loading data")

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
         Output('summary-controls', 'style')],
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
                    {'display': 'none'})

        if current_view == 'detail':
            return ({'display': 'none'},
                    {'display': 'block'},
                    'summary',
                    {'width': '50%', 'marginBottom': '20px', 'display': 'none'},
                    {'display': 'none'},
                    {'display': 'block'})
        else:
            return ({'display': 'block'},
                    {'display': 'none'},
                    'detail',
                    {'width': '50%', 'marginBottom': '20px', 'display': 'block'},
                    {'display': 'block'},
                    {'display': 'none'})

    @app.callback(
        Output('summary-metrics-dropdown', 'style'),
        [Input('summary-type', 'value')]
    )
    def toggle_metrics_dropdown(summary_type):
        if summary_type == 'custom':
            return {'display': 'block'}
        return {'display': 'none'}

    @app.callback(
        [Output('goals-collapse', 'is_open'),
         Output('collapse-goals-button', 'children')],
        [Input('collapse-goals-button', 'n_clicks')],
        [State('goals-collapse', 'is_open')]
    )
    def toggle_goals_collapse(n_clicks, is_open):
        if n_clicks is None:
            return True, '⯆'
        return not is_open, '⯆' if not is_open else '⯈'

def create_goals_display(goals):
    """Create a formatted display of all current goals with editable inputs"""
    if not goals:
        return html.Div("No goals set")

    sorted_metrics = sorted(goals.keys(), key=lambda m: METRIC_LABEL_MAP.get(m, m))

    header = html.Tr([
        html.Th("Metric", style={'width': '40%', 'textAlign': 'left'}),
        html.Th("Goal", style={'width': '30%', 'textAlign': 'left'}),
        html.Th("Units", style={'width': '30%', 'textAlign': 'left'})
    ])

    rows = []
    for metric in sorted_metrics:
        value = goals[metric]
        units = get_metric_units(metric)
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