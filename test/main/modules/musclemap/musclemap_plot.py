# modules/musclemap/musclemap_plot.py
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
                        # If there's no path or it's empty, skip
                        continue
                    parsed_coords = parse_svg_path(path_data["path"])
                    transformed_coords = apply_transformation(
                        parsed_coords, path_data.get("transform", {})
                    )
                    # Only append if we have at least 3 points for a polygon
                    if len(transformed_coords) >= 3:
                        parsed_data[view][muscle].append({
                            "coords": transformed_coords,
                            "style": path_data["style"]
                        })
    return parsed_data.get("Front", {})

def plot_muscle_map(processed_strength_activities, muscle_coordinates, title, zoom_out_factor=1.5):
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
                # Not enough data to form a polygon
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

    ax.set_title(title, fontsize=16, weight='bold')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    img_data = base64.b64encode(buf.read()).decode('utf-8')
    return img_data
