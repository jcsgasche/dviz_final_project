# modules/callbacks/barchart_callbacks.py
from dash import Input, Output, State, callback_context, html
import pandas as pd
from modules.charts.barchart import create_activity_chart, get_default_goals, get_metric_units
import json

def register_barchart_callbacks(app):
    @app.callback(
        Output('activity-graph', 'figure'),
        Output('goal-input', 'value'),
        [Input('metric-selector', 'value'),
         Input('date-range', 'start_date'),
         Input('date-range', 'end_date'),
         Input('stored-data', 'data'),
         Input('stored-goals', 'data'),
         Input('activity-graph', 'relayoutData')]
    )
    def update_chart(selected_metric, start_date, end_date, stored_data, stored_goals, relayout_data):
        if not stored_data or not stored_goals:
            return {}, None

        df = pd.DataFrame(stored_data)
        df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])

        # Get the goal for the selected metric
        goal_value = stored_goals.get(selected_metric, get_default_goals()[selected_metric])

        if relayout_data and 'xaxis.range[0]' in relayout_data:
            start_date = relayout_data['xaxis.range[0]'][:10]
            end_date = relayout_data['xaxis.range[1]'][:10]

        return create_activity_chart(df, selected_metric, start_date, end_date, goal_value), goal_value

    @app.callback(
        Output('stored-goals', 'data'),
        Output('current-goals-display', 'children'),
        [Input('save-goal-button', 'n_clicks'),
         Input('reset-goals-button', 'n_clicks')],
        [State('metric-selector', 'value'),
         State('goal-input', 'value'),
         State('stored-goals', 'data')]
    )
    def update_goals(save_clicks, reset_clicks, selected_metric, new_goal, stored_goals):
        ctx = callback_context
        if not ctx.triggered:
            return stored_goals, create_goals_display(stored_goals)

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == 'reset-goals-button':
            stored_goals = get_default_goals()
        elif button_id == 'save-goal-button' and new_goal is not None:
            stored_goals = stored_goals or get_default_goals()
            stored_goals[selected_metric] = new_goal

        return stored_goals, create_goals_display(stored_goals)

def create_goals_display(goals):
    """Create a formatted display of all current goals"""
    if not goals:
        return html.Div("No goals set")

    goal_items = []
    for metric, value in sorted(goals.items()):
        units = get_metric_units(metric)
        metric_name = metric.replace('_', ' ').title()
        goal_items.append(
            html.Div([
                f"{metric_name}: {value} {units}"
            ], style={
                'margin': '5px 0',
                'padding': '5px',
                'borderBottom': '1px solid #eee'
            })
        )

    return html.Div(
        goal_items,
        style={
            'maxHeight': '300px',
            'overflowY': 'auto',
            'padding': '10px',
            'border': '1px solid #ddd',
            'borderRadius': '5px',
            'marginTop': '10px'
        }
    )