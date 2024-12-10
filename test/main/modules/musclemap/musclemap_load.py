# musclemap_load.py
import json
import os
import sys

# Define the list of known exercises and muscle groups
# (These can be dynamically updated at runtime)
known_exercises = [
    "BENCH_PRESS",
    "PUSH_UP",
    "SIT_UP",
    "LATERAL_RAISE",
    "CURL",
    "ROW",
    "SQUAT",
    "PULL_UP",
    "FLYE",
    "UNKNOWN",
]

muscle_groups = [
    "FrontQuadsRight",
    "FrontQuadsLeft",
    "Ab-AdductorsRight",
    "FrontHipsRight",
    "Ab-AductorsLeft",
    "FrontHipsLeft",
    "FrontAbsRight",
    "FrontAbsLeft",
    "FrontObliquesRight",
    "FrontObliquesLeft",
    "FrontChestRight",
    "FrontChestLeft",
    "FrontDeltsRight",
    "FrontDeltsLeft",
    "FrontBicepsRight",
    "FrontBicepsLeft",
    "FrontForearmsRight",
    "FrontForearmsLeft",
    "BackCalvesRight",
    "BackCalvesLeft",
    "BackHamstringsRight",
    "BackHamstringsLeft",
    "BackAdductorsRight",
    "BackAdductorsLeft",
    "BackGlutesRight",
    "BackGlutesLeft",
    "BackAbductorsRight",
    "BackAbductorsLeft",
    "BackLowerbackRight",
    "BackLowerbackLeft",
    "BackLatsRight",
    "BackLatsLeft",
    "BackTrapsRight",
    "BackTrapsLeft",
    "BackDeltsRight",
    "BackDeltsLeft",
    "BackTricepsRight",
    "BackTricepsLeft",
    "BackForearmsRight",
    "BackForearmsLeft",
    "Undefined",
]

# Default exercise-to-muscle mapping
exercise_to_musclegroup = {
    "BENCH_PRESS": {
        "primary": ["FrontChestRight", "FrontChestLeft"],
        "secondary": ["FrontDeltsRight", "FrontDeltsLeft", "BackTricepsRight", "BackTricepsLeft"],
    },
    "FLYE": {
        "primary": ["FrontChestRight", "FrontChestLeft"],
        "secondary": ["FrontBicepsRight", "FrontBicepsLeft"]
    },
    "SIT_UP": {
        "primary": ["FrontAbsRight", "FrontAbsLeft"],
        "secondary": ["FrontObliquesRight", "FrontObliquesLeft"]
    },
    "LATERAL_RAISE": {
        "primary": ["FrontDeltsRight", "FrontDeltsLeft"],
        "secondary": ["BackDeltsRight", "BackDeltsLeft"]
    },
    "ROW": {
        "primary": ["BackLatsRight", "BackLatsLeft"],
        "secondary": ["FrontBicepsRight", "FrontBicepsLeft"]
    },
    "SQUAT": {
        "primary": ["FrontQuadsRight", "FrontQuadsLeft"],
        "secondary": ["BackGlutesRight", "BackGlutesLeft", "BackHamstringsRight", "BackHamstringsLeft"]
    },
    "CURL": {
        "primary": ["FrontBicepsRight", "FrontBicepsLeft"],
        "secondary": ["FrontForearmsRight", "FrontForearmsLeft"]
    },
    "PUSH_UP": {
        "primary": ["FrontChestRight", "FrontChestLeft"],
        "secondary": ["BackTricepsRight", "BackTricepsLeft"]
    },
    "UNKNOWN": {
        "primary": ["Undefined"],
        "secondary": ["Undefined"]
    }
}


def load_exercise_mappings():
    """
    Load the exercise_to_musclegroup mapping if exercise_to_musclegroup.json exists.
    Otherwise, use the default mapping defined above.
    """
    global known_exercises, exercise_to_musclegroup
    if os.path.exists("exercise_to_musclegroup.json"):
        with open("exercise_to_musclegroup.json", "r") as f:
            exercise_to_musclegroup.update(json.load(f))
        known_exercises = list(exercise_to_musclegroup.keys())


def save_exercise_mappings():
    """
    Save the current exercise_to_musclegroup mapping to exercise_to_musclegroup.json.
    """
    with open("exercise_to_musclegroup.json", "w") as f:
        json.dump(exercise_to_musclegroup, f, indent=4)


def get_muscle_groups_for_exercise(exercise_name):
    """
    Prompt the user to select muscle groups for a new, unknown exercise.
    This can be integrated into a web UI by returning lists of muscle groups
    and letting the UI handle the selection, rather than using input().
    """

    print(f"\nNew exercise detected: {exercise_name}")
    print("Please select primary muscle groups for this exercise.")
    print("Enter the numbers corresponding to the muscle groups, separated by commas.")
    print("Available muscle groups:")
    for idx, muscle in enumerate(muscle_groups):
        print(f"{idx + 1}. {muscle}")

    # Get primary muscles
    while True:
        primary_input = input("Primary muscles (e.g., 1,2,3): ")
        try:
            primary_indices = [int(i.strip()) - 1 for i in primary_input.split(",")]
            primary_muscles = [muscle_groups[i] for i in primary_indices]
            break
        except (ValueError, IndexError):
            print("Invalid input. Please enter valid numbers separated by commas.")

    # Get secondary muscles
    print("\nPlease select secondary muscle groups for this exercise (if any).")
    print("Leave blank if there are no secondary muscles.")
    secondary_input = input("Secondary muscles (e.g., 4,5): ")
    if secondary_input.strip():
        try:
            secondary_indices = [int(i.strip()) - 1 for i in secondary_input.split(",")]
            secondary_muscles = [muscle_groups[i] for i in secondary_indices]
        except (ValueError, IndexError):
            print("Invalid input. No secondary muscles will be recorded.")
            secondary_muscles = []
    else:
        secondary_muscles = []

    # Update the exercise_to_musclegroup mapping
    exercise_to_musclegroup[exercise_name] = {
        "primary": primary_muscles,
        "secondary": secondary_muscles,
    }

    # Add the new exercise to known exercises
    known_exercises.append(exercise_name)
    
    # Save the updated exercise_to_musclegroup mapping immediately
    save_exercise_mappings()

    return exercise_to_musclegroup[exercise_name]


def process_strength_activities(strength_activities):
    """
    Given a list of strength activities (as loaded from Garmin or from a file),
    assign muscle groups based on exercise_to_musclegroup mappings.
    If unknown exercises are encountered, prompt the user to add them.
    Returns a list of processed data and also updates exercise_to_musclegroup.json.
    """

    load_exercise_mappings()  # Ensure we have the latest mappings

    processed_data = []

    for activity in strength_activities:
        activity_date_str = activity.get("startTimeLocal", activity.get("startTimeGMT"))
        if not activity_date_str:
            # Skip activities with no date
            continue

        # Parse date (assuming it's always valid here; otherwise, handle errors)
        try:
            # Support both with and without milliseconds
            from datetime import datetime
            try:
                activity_date = datetime.strptime(activity_date_str, "%Y-%m-%d %H:%M:%S").date()
            except ValueError:
                activity_date = datetime.strptime(activity_date_str, "%Y-%m-%d %H:%M:%S.%f").date()
        except ValueError:
            # If date parsing fails, skip this activity
            continue

        exercise_sets = activity.get("summarizedExerciseSets", [])
        if not exercise_sets:
            continue  # skip if no exercise sets

        activity_exercises = []

        for exercise_set in exercise_sets:
            exercise_name = exercise_set.get("category", "UNKNOWN")
            repetitions = exercise_set.get("reps", 0)
            sets = exercise_set.get("sets", 1)  # default to 1 if not provided

            # Handle unknown exercises
            if exercise_name not in known_exercises:
                # Prompt user or handle logic to add them
                muscle_groups_info = get_muscle_groups_for_exercise(exercise_name)
            else:
                # Get muscle groups from the mapping
                muscle_groups_info = exercise_to_musclegroup.get(
                    exercise_name,
                    {"primary": ["Undefined"], "secondary": ["Undefined"]},
                )

            exercise_info = {
                "exercise_name": exercise_name,
                "repetitions": repetitions,
                "sets": sets,
                "primary_muscles": muscle_groups_info["primary"],
                "secondary_muscles": muscle_groups_info["secondary"],
            }

            activity_exercises.append(exercise_info)

        processed_data.append({
            "date": activity_date.isoformat(),
            "exercises": activity_exercises,
        })

    # Save processed data
    with open("processed_strength_activities.json", "w") as f:
        json.dump(processed_data, f, indent=4)

    # Also save the latest exercise_to_musclegroup mapping
    save_exercise_mappings()

    return processed_data
