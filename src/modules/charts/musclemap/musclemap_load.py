import json
import os
import datetime

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
    "FrontQuadsRight", "FrontQuadsLeft", "Ab-AdductorsRight", "FrontHipsRight", "Ab-AductorsLeft",
    "FrontHipsLeft", "FrontAbsRight", "FrontAbsLeft", "FrontObliquesRight", "FrontObliquesLeft",
    "FrontChestRight", "FrontChestLeft", "FrontDeltsRight", "FrontDeltsLeft", "FrontBicepsRight",
    "FrontBicepsLeft", "FrontForearmsRight", "FrontForearmsLeft", "BackCalvesRight", "BackCalvesLeft",
    "BackHamstringsRight", "BackHamstringsLeft", "BackAdductorsRight", "BackAdductorsLeft", "BackGlutesRight",
    "BackGlutesLeft", "BackAbductorsRight", "BackAbductorsLeft", "BackLowerbackRight", "BackLowerbackLeft",
    "BackLatsRight", "BackLatsLeft", "BackTrapsRight", "BackTrapsLeft", "BackDeltsRight", "BackDeltsLeft",
    "BackTricepsRight", "BackTricepsLeft", "BackForearmsRight", "BackForearmsLeft", "Undefined",
]

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
    if os.path.exists("src/modules/charts/musclemap/data/exercise_to_musclegroup.json"):
        with open("src/modules/charts/musclemap/data/exercise_to_musclegroup.json", "r") as f:
            loaded = json.load(f)
        exercise_to_musclegroup.update(loaded)
        # Update known_exercises
        known = list(exercise_to_musclegroup.keys())
        return known
    return known_exercises

def save_exercise_mappings():
    with open("src/modules/charts/musclemap/data/exercise_to_musclegroup.json", "w") as f:
        json.dump(exercise_to_musclegroup, f, indent=4)

def process_strength_activities(strength_activities):
    load_exercise_mappings()

    processed_data = []
    for activity in strength_activities:
        activity_date_str = activity.get("startTimeLocal", activity.get("startTimeGMT"))
        if not activity_date_str:
            continue

        # Parse date
        try:
            try:
                activity_date = datetime.datetime.strptime(activity_date_str, "%Y-%m-%d %H:%M:%S").date()
            except ValueError:
                activity_date = datetime.datetime.strptime(activity_date_str, "%Y-%m-%d %H:%M:%S.%f").date()
        except ValueError:
            continue

        exercise_sets = activity.get("summarizedExerciseSets", [])
        if not exercise_sets:
            continue

        activity_exercises = []

        for exercise_set in exercise_sets:
            exercise_name = exercise_set.get("category", "UNKNOWN")
            repetitions = exercise_set.get("reps", 0)
            sets = exercise_set.get("sets", 1)

            if exercise_name not in exercise_to_musclegroup:
                # Unknown exercise defaults to Undefined muscles
                muscle_groups_info = {"primary": ["Undefined"], "secondary": ["Undefined"]}
                exercise_to_musclegroup[exercise_name] = muscle_groups_info
            else:
                muscle_groups_info = exercise_to_musclegroup[exercise_name]

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

    with open("src/modules/charts/musclemap/data/processed_strength_activities.json", "w") as f:
        json.dump(processed_data, f, indent=4)

    save_exercise_mappings()

    return processed_data
