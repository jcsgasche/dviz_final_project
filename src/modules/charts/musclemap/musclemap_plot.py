import matplotlib
matplotlib.use('Agg')

import os
import sys
import json
import re
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import io
import base64
import numpy as np

def parse_svg_path(d):
    """Parse raw SVG paths into coordinate lists."""
    path_data = re.findall(r"[-+]?[0-9]*\.?[0-9]+", d)
    coords = []
    for i in range(0, len(path_data), 2):
        x = float(path_data[i])
        y = float(path_data[i + 1])
        coords.append((x, -y))
    return coords

def apply_transformation(coords, transform):
    """Apply translation transformation to a list of coordinates."""
    if not coords:
        return coords
    return [
        (x + transform.get("translateX", 0), y + transform.get("translateY", 0))
        for x, y in coords
    ]

def create_spider_chart(ax, muscle_activity, position, size):
    # Format category names by adding spaces before capital letters
    def format_muscle_name(name):
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', name)

    categories = [format_muscle_name(key) for key in muscle_activity.keys()]
    N = len(categories)

    if N == 0:
        return

    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    values = list(muscle_activity.values())
    # Always normalize to percentage of maximum value
    max_value = max(values) if values and max(values) > 0 else 1
    # Normalize values between 0 and 1
    values = [v / max_value if max_value != 0 else 0 for v in values]
    # Close the polygon by appending the first value
    values += values[:1]

    # Make sure we display all tick marks even with zero values
    if all(v == 0 for v in values):
        values = [0] * (len(values))

    ax_spider = plt.axes(position, projection='polar')
    # Use fixed styling
    ax_spider.plot(angles, values, 'o-', linewidth=2, color='blue')
    ax_spider.fill(angles, values, alpha=0.25, color='blue')

    ax_spider.set_xticks(angles[:-1])
    labels = ax_spider.set_xticklabels(categories, size=14)
    ax_spider.set_rlabel_position(0)

    for idx, label in enumerate(labels):
        angle = angles[idx] * 180/np.pi
        if angle < 90:
            label.set_rotation(angle)
            label.set_horizontalalignment('left')
        elif angle < 180:
            label.set_rotation(angle - 180)
            label.set_horizontalalignment('right')
        elif angle < 270:
            label.set_rotation(angle - 180)
            label.set_horizontalalignment('right')
        else:
            label.set_rotation(angle)
            label.set_horizontalalignment('left')

    # Set fixed tick marks at 20% intervals
    yticks = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    ax_spider.set_ylim(0, 1)
    ax_spider.set_facecolor('white')
    ax_spider.patch.set_alpha(0.8)
    ax_spider.set_rticks(yticks)
    yticklabels = [f'{int(y*100)}%' for y in yticks]
    ax_spider.set_yticklabels(yticklabels, fontsize=12)

    # Add gridlines
    ax_spider.grid(True, color='gray', alpha=0.3)

    # Make sure the ticks are always visible
    for tick in ax_spider.yaxis.get_ticklabels():
        tick.set_visible(True)

    return ax_spider


def add_legend(fig, ax):
    """Add the legend to the muscle map"""
    legend_height = 0.05
    legend_ax = fig.add_axes([0.85, 0.75, 0.2, legend_height])
    legend_ax.set_xlim(0, 1)
    legend_ax.set_ylim(0, 2)
    legend_ax.set_yticks([])
    legend_ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    legend_ax.set_xticklabels(["100 %", "75 %", "50 %", "25 %", "0 %"], fontsize=14)  # Increased font size

    # Create background rectangle
    legend_bg = plt.Rectangle(
        (0, 0), 1, 1,
        transform=legend_ax.transAxes,
        facecolor=(0.9, 0.9, 0.9),
        zorder=0
    )
    legend_ax.add_patch(legend_bg)

    legend_ax.spines["left"].set_visible(True)
    legend_ax.spines["right"].set_visible(True)
    legend_ax.spines["top"].set_visible(True)
    legend_ax.spines["bottom"].set_visible(True)

    # Add legend entries with adjusted position and larger font size
    legend_ax.text(-0.15, 1.3, "Primary Trained Muscles", ha='right', va='center', fontsize=16)
    for i in range(5):
        alpha_val = 1.0 - 0.25 * i
        xstart = i * 0.2
        rect = plt.Rectangle((xstart, 1.1), 0.2, 0.4, facecolor=(1, 0, 0, alpha_val))
        legend_ax.add_patch(rect)

    legend_ax.text(-0.15, 0.1, "Secondary Trained Muscles", ha='right', va='center', fontsize=16)
    for i in range(5):
        alpha_val = 1.0 - 0.25 * i
        xstart = i * 0.2
        rect = plt.Rectangle((xstart, 0.1), 0.2, 0.4, facecolor=(1, 1, 0, alpha_val))
        legend_ax.add_patch(rect)

def plot_muscle_map(processed_strength_activities, muscle_coordinates, zoom_out_factor=1.5):
    """Plot the muscle map with activity data and integrated spider chart"""
    if not processed_strength_activities:
        return create_empty_muscle_map(muscle_coordinates, zoom_out_factor,
                                       message="No data available\nin this period of time")

    # Calculate repetitions for both visualizations
    primary_reps = {}
    secondary_reps = {}
    muscle_activity = {}

    for activity in processed_strength_activities:
        for exercise in activity['exercises']:
            reps = exercise.get('repetitions', 0) * exercise.get('sets', 1)

            # Process for muscle map
            for muscle in exercise['primary_muscles']:
                if muscle != 'Undefined':
                    primary_reps[muscle] = primary_reps.get(muscle, 0) + reps
                    # Aggregate for spider chart (removing Right/Left)
                    base_muscle = muscle.replace('Right', '').replace('Left', '')
                    muscle_activity[base_muscle] = muscle_activity.get(base_muscle, 0) + reps

            for muscle in exercise['secondary_muscles']:
                if muscle != 'Undefined':
                    secondary_reps[muscle] = secondary_reps.get(muscle, 0) + reps * 0.5
                    # Add secondary muscles with half weight
                    base_muscle = muscle.replace('Right', '').replace('Left', '')
                    muscle_activity[base_muscle] = muscle_activity.get(base_muscle, 0) + reps * 0.5

    # Create main figure with larger size
    fig = plt.figure(figsize=(27, 15))  # Increased from (19.8, 10.8)

    # Create main axes for muscle map with adjusted width
    ax_main = plt.axes([0.1, 0.1, 0.8, 0.8])

    xlim = (-110 * zoom_out_factor, 700 * zoom_out_factor)
    ylim = (-25 * zoom_out_factor, 575 * zoom_out_factor)
    ax_main.set_xlim(xlim)
    ax_main.set_ylim(ylim)
    ax_main.set_aspect('equal')
    ax_main.axis('off')

    # Draw muscle map
    max_primary_reps = max(primary_reps.values(), default=1)
    max_secondary_reps = max(secondary_reps.values(), default=1)

    for muscle_group, polygons in muscle_coordinates.items():
        for polygon_data in polygons:
            coords = polygon_data["coords"]
            if not coords or len(coords) < 3:
                continue

            color = "lightgrey"
            if muscle_group in primary_reps:
                intensity = primary_reps[muscle_group] / max_primary_reps
                color = (1, 0, 0, intensity)
            elif muscle_group in secondary_reps:
                intensity = secondary_reps[muscle_group] / max_secondary_reps
                color = (1, 1, 0, intensity)

            polygon = Polygon(coords, closed=True, facecolor=color, edgecolor="black", linewidth=0.5)
            ax_main.add_patch(polygon)

    # Add legend
    add_legend(fig, ax_main)

    # Initialize a complete muscle activity dictionary with zeros
    complete_muscle_activity = {
        'FrontChest': 0, 'BackLats': 0, 'FrontDelts': 0, 'BackDelts': 0,
        'FrontAbs': 0, 'BackTriceps': 0, 'FrontBiceps': 0, 'FrontQuads': 0,
        'BackGlutes': 0, 'BackHamstrings': 0
    }

    # Update with any actual activity
    for muscle, value in muscle_activity.items():
        if muscle in complete_muscle_activity:
            complete_muscle_activity[muscle] = value

    spider_chart = create_spider_chart(
        ax_main,
        complete_muscle_activity,
        [0.71, 0.2, 0.4, 0.4],
        0.3
    )

    # Save with higher DPI and quality
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=200)  # Increased DPI from 150 to 200
    plt.close(fig)
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode('utf-8')
    return img_data

def create_empty_muscle_map(muscle_coordinates, zoom_out_factor=1.5, message="Waiting for you to add\nyour personal fitness data"):
    """Create an empty muscle map with grey muscles and a message"""
    # Create main figure with larger size
    fig = plt.figure(figsize=(24, 13.5))  # Increased from (19.8, 10.8)

    # Create main axes for muscle map
    ax_main = plt.axes([0.1, 0.1, 0.8, 0.8])

    xlim = (-110 * zoom_out_factor, 700 * zoom_out_factor)
    ylim = (-25 * zoom_out_factor, 575 * zoom_out_factor)
    ax_main.set_xlim(xlim)
    ax_main.set_ylim(ylim)
    ax_main.set_aspect('equal')
    ax_main.axis('off')

    # Draw muscles in grey
    for muscle_group, polygons in muscle_coordinates.items():
        for polygon_data in polygons:
            coords = polygon_data["coords"]
            if not coords or len(coords) < 3:
                continue

            polygon = Polygon(coords, closed=True, facecolor="lightgrey",
                              edgecolor="black", linewidth=0.5)
            ax_main.add_patch(polygon)

    # Add centered message
    center_x = (xlim[0] + xlim[1]) / 2
    center_y = (ylim[0] + ylim[1]) / 2

    bg_box = dict(
        boxstyle='square,pad=0.6',
        facecolor='white',
        alpha=0.9,
        edgecolor='none'
    )

    message = message.replace("<br>", "\n")
    plt.text(center_x, center_y, message,
             horizontalalignment='center',
             verticalalignment='center',
             fontsize=16,
             bbox=bg_box,
             linespacing=1.2)

    # Add legend
    add_legend(fig, ax_main)

    # Create empty spider chart with consistent axes
    empty_muscle_activity = {
        'Front Chest': 0, 'Back Lats': 0, 'Front Deltoids': 0, 'Back Deltoids': 0,
        'Front Abs': 0, 'Back Triceps': 0, 'Front Biceps': 0, 'Front Quads': 0,
        'Back Glutes': 0, 'Back Hamstrings': 0
    }
    create_spider_chart(
        ax_main,
        empty_muscle_activity,  # Use the full set of muscles with zeros
        [0.75, 0.2, 0.3, 0.3],  # Moved left and increased size [left, bottom, width, height]
        0.3
    )

    # Save and return
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=200)  # Increased DPI from 150 to 200
    plt.close(fig)
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode('utf-8')
    return img_data

def load_and_parse_muscle_coordinates(filename):
    file_path = os.path.abspath(filename)

    if not os.path.exists(file_path):
        print(f"Error: '{file_path}' not found.")
        sys.exit(1)

    with open(file_path, 'r') as file:
        raw_data = json.load(file)

    parsed_data = {}
    for view, muscles in raw_data.items():
        if view == "Front":
            parsed_data[view] = {}
            for muscle, paths in muscles.items():
                parsed_data[view][muscle] = []
                for path_data in paths:
                    if "path" not in path_data or not path_data["path"]:
                        continue
                    parsed_coords = parse_svg_path(path_data["path"])
                    transformed_coords = apply_transformation(
                        parsed_coords, path_data.get("transform", {})
                    )
                    if len(transformed_coords) >= 3:
                        parsed_data[view][muscle].append({
                            "coords": transformed_coords,
                            "style": path_data["style"]
                        })
    return parsed_data.get("Front", {})