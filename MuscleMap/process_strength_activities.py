import json
import datetime
import os
import sys

# Define the list of known exercises
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

# Define the muscle groups
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

# Initialize the exercise to muscle group mapping
exercise_to_musclegroup = {
    "BENCH_PRESS": {
        "primary": ["FrontChestRight", "FrontChestLeft"],
        "secondary": [
            "FrontDeltsRight",
            "FrontDeltsLeft",
            "BackTricepsRight",
            "BackTricepsLeft",
        ],
    },
    # Add other exercises with their primary and secondary muscles
    # You can fill these in as needed
}

# Function to prompt the user for muscle groups of a new exercise
def get_muscle_groups_for_exercise(exercise_name):
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

    return exercise_to_musclegroup[exercise_name]

def main():
    # Check if the strength activities JSON file exists
    if not os.path.exists("strength_activities.json"):
        print("The file 'strength_activities.json' does not exist.")
        print("Please ensure you have run the script to fetch strength activities.")
        sys.exit()

    # Read the strength activities data
    with open("strength_activities.json", "r") as f:
        activities = json.load(f)

    # Initialize the list to hold processed data
    processed_data = []

    # Process each activity
    for activity in activities:
        activity_date_str = activity.get("startTimeLocal", activity.get("startTimeGMT"))
        try:
            activity_date = datetime.datetime.strptime(
                activity_date_str, "%Y-%m-%d %H:%M:%S"
            ).date()
        except ValueError:
            # Handle activities with milliseconds in the timestamp
            activity_date = datetime.datetime.strptime(
                activity_date_str, "%Y-%m-%d %H:%M:%S.%f"
            ).date()

        # Check if 'summarizedExerciseSets' exists in the activity
        exercise_sets = activity.get("summarizedExerciseSets", [])
        if not exercise_sets:
            continue  # Skip if no exercise sets are found

        # Initialize a list to hold exercises for this activity
        activity_exercises = []

        # Process each exercise set
        for exercise_set in exercise_sets:
            exercise_name = exercise_set.get("exerciseName", "UNKNOWN")
            repetitions = exercise_set.get("repetitions", 0)
            sets = exercise_set.get("sets", 1)  # Default to 1 if not provided

            # Check if the exercise is known
            if exercise_name not in known_exercises:
                # Get muscle groups for the new exercise
                muscle_groups_info = get_muscle_groups_for_exercise(exercise_name)
            else:
                # Get muscle groups from the mapping
                muscle_groups_info = exercise_to_musclegroup.get(
                    exercise_name,
                    {"primary": ["Undefined"], "secondary": []},
                )

            # Create a dictionary for the exercise
            exercise_info = {
                "exercise_name": exercise_name,
                "repetitions": repetitions,
                "sets": sets,
                "primary_muscles": muscle_groups_info["primary"],
                "secondary_muscles": muscle_groups_info["secondary"],
            }

            activity_exercises.append(exercise_info)

        # Add the processed activity data to the list
        processed_data.append(
            {
                "date": activity_date.isoformat(),
                "exercises": activity_exercises,
            }
        )

    # Save the processed data to a new JSON file
    with open("processed_strength_activities.json", "w") as f:
        json.dump(processed_data, f, indent=4)

    print("\nProcessed data has been saved to 'processed_strength_activities.json'.")

if __name__ == "__main__":
    main()
