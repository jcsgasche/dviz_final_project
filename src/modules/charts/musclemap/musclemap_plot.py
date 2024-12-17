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

def parse_svg_path(d):
    """
    Parse raw SVG paths into coordinate lists.
    """
    # Use the given regex and logic directly
    path_data = re.findall(r"[-+]?[0-9]*\.?[0-9]+", d)
    coords = []
    for i in range(0, len(path_data), 2):
        x = float(path_data[i])
        y = float(path_data[i + 1])
        coords.append((x, -y))  # Negate y to match typical plot coordinates
    return coords

def apply_transformation(coords, transform):
    """
    Apply translation transformation to a list of coordinates.
    """
    if not coords:
        return coords
    return [
        (x + transform.get("translateX", 0), y + transform.get("translateY", 0))
        for x, y in coords
    ]

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

def add_legend(fig, ax):
    """Add the legend to the muscle map"""
    legend_height = 0.05
    legend_ax = fig.add_axes([0.85, 0.7, 0.1, legend_height])
    legend_ax.set_xlim(0, 1)
    legend_ax.set_ylim(0, 2)
    legend_ax.set_yticks([])
    legend_ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    legend_ax.set_xticklabels(["0", "0.25", "0.5", "0.75", "1.0"])

    # Create background rectangle
    legend_bg = plt.Rectangle(
        (0, 0), 1, 1,
        transform=legend_ax.transAxes,
        facecolor=(0.9, 0.9, 0.9),
        zorder=0
    )
    legend_ax.add_patch(legend_bg)

    # Draw border
    legend_ax.spines["left"].set_visible(True)
    legend_ax.spines["right"].set_visible(True)
    legend_ax.spines["top"].set_visible(True)
    legend_ax.spines["bottom"].set_visible(True)
    legend_ax.set_facecolor('black')

    # Primary line
    legend_ax.text(-0.15, 1.3, "Primary Trained Muscles", ha='right', va='center', fontsize=12, color='black')
    for i in range(5):
        alpha_val = 1.0 - 0.25 * i
        xstart = i * 0.2
        rect = plt.Rectangle((xstart, 1.1), 0.2, 0.4, facecolor=(1, 0, 0, alpha_val))
        legend_ax.add_patch(rect)

    # Secondary line
    legend_ax.text(-0.15, 0.1, "Secondary Trained Muscles", ha='right', va='center', fontsize=12, color='black')
    for i in range(5):
        alpha_val = 1.0 - 0.25 * i
        xstart = i * 0.2
        rect = plt.Rectangle((xstart, 0.1), 0.2, 0.4, facecolor=(1, 1, 0, alpha_val))
        legend_ax.add_patch(rect)

    # Note below lines
    legend_ax.text(0.5, -1.2, "Muscles that did not get stimulated remain grey.",
                   ha='center', va='top', fontsize=10, color='black')

def create_empty_muscle_map(muscle_coordinates, zoom_out_factor=1.5, message="Waiting for you to add\nyour personal fitness data"):
    """Create an empty muscle map with grey muscles and a message"""
    fig, ax = plt.subplots(figsize=(19.8, 10.8))

    xlim = (-110 * zoom_out_factor, 700 * zoom_out_factor)
    ylim = (-25 * zoom_out_factor, 575 * zoom_out_factor)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    ax.set_aspect('equal')
    ax.axis('off')

    # Draw all muscles in light grey
    for muscle_group, polygons in muscle_coordinates.items():
        for polygon_data in polygons:
            coords = polygon_data["coords"]
            if not coords or len(coords) < 3:
                continue

            polygon = Polygon(coords, closed=True, facecolor="lightgrey",
                              edgecolor="black", linewidth=0.5)
            ax.add_patch(polygon)

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
             fontsize=18,
             color='#000000',
             bbox=bg_box,
             linespacing=1.2)

    # Add the legend
    add_legend(fig, ax)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode('utf-8')
    return img_data

def plot_muscle_map(processed_strength_activities, muscle_coordinates, zoom_out_factor=1.5):
    """Plot the muscle map with activity data"""
    if not processed_strength_activities:
        return create_empty_muscle_map(muscle_coordinates, zoom_out_factor,
                                       message="No data available\nin this period of time")

    # Calculate repetitions
    primary_reps = {}
    secondary_reps = {}

    for activity in processed_strength_activities:
        for exercise in activity['exercises']:
            reps = exercise.get('repetitions', 0) * exercise.get('sets', 1)
            for muscle in exercise['primary_muscles']:
                if muscle != 'Undefined':
                    primary_reps[muscle] = primary_reps.get(muscle, 0) + reps
            for muscle in exercise['secondary_muscles']:
                if muscle != 'Undefined':
                    secondary_reps[muscle] = secondary_reps.get(muscle, 0) + reps

    max_primary_reps = max(primary_reps.values(), default=1)
    max_secondary_reps = max(secondary_reps.values(), default=1)

    fig, ax = plt.subplots(figsize=(19.8, 10.8))

    xlim = (-110 * zoom_out_factor, 700 * zoom_out_factor)
    ylim = (-25 * zoom_out_factor, 575 * zoom_out_factor)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    ax.set_aspect('equal')
    ax.axis('off')

    for muscle_group, polygons in muscle_coordinates.items():
        for polygon_data in polygons:
            coords = polygon_data["coords"]
            if not coords or len(coords) < 3:
                continue

            color = "lightgrey"
            if muscle_group in primary_reps:
                intensity = primary_reps[muscle_group] / max_primary_reps
                color = (1, 0, 0, intensity)  # Red
            elif muscle_group in secondary_reps:
                intensity = secondary_reps[muscle_group] / max_secondary_reps
                color = (1, 1, 0, intensity)  # Yellow

            polygon = Polygon(coords, closed=True, facecolor=color, edgecolor="black", linewidth=0.5)
            ax.add_patch(polygon)

    # Add the legend using the shared function
    add_legend(fig, ax)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode('utf-8')
    return img_data