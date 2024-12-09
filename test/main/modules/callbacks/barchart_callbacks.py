# modules/callbacks/barchart_callbacks.py
from dash import Input, Output, State, callback_context, html, dcc, ALL
import pandas as pd
from modules.charts.barchart import create_activity_chart, get_default_goals, get_metric_units
import json

def register_barchart_callbacks(app):
    @app.callback(
        Output('activity-graph', 'figure'),
        [Input('metric-selector', 'value'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('stored-data', 'data'),
         Input('stored-goals', 'data'),
         Input('activity-graph', 'relayoutData')]
    )
    def update_chart(selected_metric, start_date, end_date, stored_data, stored_goals, relayout_data):
        if not stored_data or not stored_goals:
            return {}

        df = pd.DataFrame(stored_data)
        df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])

        goal_value = stored_goals.get(selected_metric, get_default_goals()[selected_metric])

        if relayout_data and 'xaxis.range[0]' in relayout_data:
            start_date = relayout_data['xaxis.range[0]'][:10]
            end_date = relayout_data['xaxis.range[1]'][:10]

        return create_activity_chart(df, selected_metric, start_date, end_date, goal_value)

    @app.callback(
        Output('stored-goals', 'data'),
        Output('current-goals-display', 'children'),
        [Input('reset-goals-button', 'n_clicks'),
         Input({'type': 'goal-input', 'metric': ALL}, 'value')],
        [State({'type': 'goal-input', 'metric': ALL}, 'id'),
         State('metric-selector', 'value'),
         State('stored-goals', 'data')]
    )
    def update_goals(reset_clicks, goal_values, input_ids, selected_metric, stored_goals):
        ctx = callback_context
        if not ctx.triggered:
            return stored_goals, create_goals_display(stored_goals)

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'reset-goals-button':
            stored_goals = get_default_goals()
        else:
            stored_goals = stored_goals or get_default_goals()
            # Update goals from all inputs including quick-set
            for input_id, new_value in zip(input_ids, goal_values):
                if new_value is not None:
                    metric = input_id['metric']
                    if metric != 'quick-set':  # Only update from table inputs
                        stored_goals[metric] = float(new_value)

        return stored_goals, create_goals_display(stored_goals)

    @app.callback(
        Output({'type': 'goal-input', 'metric': 'quick-set'}, 'value'),
        [Input('metric-selector', 'value')],
        [State('stored-goals', 'data')]
    )
    def update_quick_set_display(selected_metric, stored_goals):
        if not stored_goals:
            return get_default_goals()[selected_metric]
        return stored_goals.get(selected_metric, get_default_goals()[selected_metric])

    @app.callback(
        Output('stored-goals', 'data', allow_duplicate=True),
        [Input({'type': 'goal-input', 'metric': 'quick-set'}, 'value')],
        [State('metric-selector', 'value'),
         State('stored-goals', 'data')],
        prevent_initial_call=True
    )
    def update_from_quick_set(quick_set_value, selected_metric, stored_goals):
        if quick_set_value is None:
            raise dash.exceptions.PreventUpdate

        stored_goals = stored_goals or get_default_goals()
        stored_goals[selected_metric] = float(quick_set_value)
        return stored_goals

def create_goals_display(goals):
    """Create a formatted display of all current goals with editable inputs"""
    if not goals:
        return html.Div("No goals set")

    # Create table header
    header = html.Tr([
        html.Th("Metric", style={'width': '40%', 'textAlign': 'left'}),
        html.Th("Goal", style={'width': '30%', 'textAlign': 'left'}),
        html.Th("Units", style={'width': '30%', 'textAlign': 'left'})
    ])

    # Create table rows
    rows = []
    for metric, value in sorted(goals.items()):
        units = get_metric_units(metric)
        metric_name = metric.replace('_', ' ').title()

        row = html.Tr([
            html.Td(metric_name),
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