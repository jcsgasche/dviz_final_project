# modules/callbacks/barchart_callbacks.py
from dash import Input, Output, State, callback_context, html, dcc, ALL
import pandas as pd
from modules.charts.barchart import create_activity_chart, get_default_goals, get_metric_units
import json
import dash

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
            # Handle initial load
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

            # Find which input triggered the callback
            trigger_index = next(i for i, id_dict in enumerate(input_ids) if id_dict == trigger_dict)
            new_value = goal_values[trigger_index]

            if new_value is not None:
                metric = trigger_dict['metric']
                if metric == 'quick-set':
                    # Update the selected metric's goal when quick-set changes
                    stored_goals[selected_metric] = float(new_value)
                else:
                    # Update the specific metric's goal when table input changes
                    stored_goals[metric] = float(new_value)

        # Update all input values
        updated_values = []
        for input_id in input_ids:
            if input_id['metric'] == 'quick-set':
                # Quick-set always shows the selected metric's value
                updated_values.append(stored_goals.get(selected_metric, get_default_goals()[selected_metric]))
            else:
                # Table inputs show their respective metric values
                updated_values.append(stored_goals.get(input_id['metric'], get_default_goals()[input_id['metric']]))

        return stored_goals, create_goals_display(stored_goals), updated_values

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