import json
import datetime
import os
import sys
import getpass
from garminconnect import Garmin, GarminConnectAuthenticationError

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
    "FLYE": {
        "primary": [
            "FrontChestRight",
            "FrontChestLeft"
        ],
        "secondary": [
            "FrontBicepsRight",
            "FrontBicepsLeft"
        ]
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
        "secondary": ["BackBicepsRight", "BackBicepsLeft"]
    },
    "SQUAT": {
        "primary": ["FrontQuadsRight", "FrontQuadsLeft"],
        "secondary": ["BackGlutesRight", "BackGlutesLeft", "BackHamstringsRight", "BackHamstringsLeft"]
    },
    "CURL": {
        "primary": [
            "FrontBicepsRight",
            "FrontBicepsLeft"
        ],
        "secondary": [
            "FrontForearmsRight",
            "FrontForearmsLeft"
        ]
    },
    "PUSH_UP": {
        "primary": [
            "FrontChestRight",
            "FrontChestLeft"
        ],
        "secondary": [
            "BackTricepsRight",
            "BackTricepsLeft"
        ]
    },
    # Map UNKNOWN to Undefined muscles
    "UNKNOWN": {
        "primary": ["Undefined"],
        "secondary": ["Undefined"]
    }
}

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
    
    # Save the updated exercise_to_musclegroup mapping immediately
    with open("exercise_to_musclegroup.json", "w") as f:
        json.dump(exercise_to_musclegroup, f, indent=4)


    return exercise_to_musclegroup[exercise_name]

def main():
    # Prompt the user for Garmin Connect credentials
    username = input("Enter your Garmin username: ")
    password = getpass.getpass("Enter your Garmin password: ")

    # Initialize the Garmin client
    try:
        api = Garmin(username, password)
    except Exception as e:
        print("Error initializing Garmin client:", e)
        return

    # Login to Garmin Connect
    try:
        api.login()
        print("Successfully logged in to Garmin Connect.")
    except GarminConnectAuthenticationError as auth_err:
        print("Authentication error:", auth_err)
        # Check if MFA is required
        if "two-factor" in str(auth_err).lower() or "multi-factor" in str(auth_err).lower():
            mfa_code = input("Enter the MFA code sent to your device: ")
            try:
                api.login(mfa_code)
                print("Successfully logged in with MFA.")
            except Exception as e:
                print("Error logging in with MFA:", e)
                return
        else:
            print("Login failed due to authentication error.")
            return
    except Exception as e:
        print("Error logging in to Garmin Connect:", e)
        return

    # Prompt for start and end dates
    start_date_str = input("Enter the start date (YYYY-MM-DD): ")
    end_date_str = input("Enter the end date (YYYY-MM-DD): ")

    try:
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError as e:
        print("Invalid date format:", e)
        return

    # Initialize variables for fetching activities
    start = 0
    limit = 100  # Number of activities to fetch per request
    strength_activities = []
    more_activities = True

    # Fetch activities in batches and filter by date range and activity type
    while more_activities:
        print(f"Fetching activities {start + 1} to {start + limit}...")
        try:
            batch = api.get_activities(start, limit)
        except Exception as e:
            print("Error fetching activities:", e)
            return

        if not batch:
            break

        for activity in batch:
            # Parse the activity date
            activity_date_str = activity.get('startTimeLocal', activity.get('startTimeGMT'))
            try:
                activity_date = datetime.datetime.strptime(
                    activity_date_str, '%Y-%m-%d %H:%M:%S'
                ).date()
            except ValueError:
                # Handle activities with milliseconds in the timestamp
                activity_date = datetime.datetime.strptime(
                    activity_date_str, '%Y-%m-%d %H:%M:%S.%f'
                ).date()

            # Check if activity is within the date range
            if activity_date < start_date:
                # Since activities are ordered from newest to oldest, we can stop
                more_activities = False
                break
            elif activity_date > end_date:
                continue  # Skip activities after the end date

            # Filter activities by type 'strength_training'
            if activity['activityType']['typeKey'] == 'strength_training':
                strength_activities.append(activity)

        # Check if we've fetched all activities
        if len(batch) < limit:
            break

        start += limit

    # Save the strength activities to a JSON file
    if strength_activities:
        with open('strength_activities.json', 'w') as f:
            json.dump(strength_activities, f, indent=4)
        print(
            f"Found {len(strength_activities)} strength activities between {start_date} and {end_date}."
        )
        print("Strength activities have been saved to 'strength_activities.json'.")
    else:
        print(f"No strength activities found between {start_date} and {end_date}.")
        return

    # Now process the strength activities
    # Initialize the list to hold processed data
    processed_data = []

    # Load existing exercise_to_musclegroup mapping if exists
    if os.path.exists("exercise_to_musclegroup.json"):
        with open("exercise_to_musclegroup.json", "r") as f:
            exercise_to_musclegroup.update(json.load(f))
        known_exercises = list(exercise_to_musclegroup.keys())

    # Process each activity
    for activity in strength_activities:
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
            exercise_name = exercise_set.get("category", "UNKNOWN")
            repetitions = exercise_set.get("reps", 0)
            sets = exercise_set.get("sets", 1)  # Default to 1 if not provided

            # Handle UNKNOWN category
            if exercise_name == "UNKNOWN":
                muscle_groups_info = {
                    "primary": ["Undefined"],
                    "secondary": ["Undefined"]
                }
            else:
                # Check if the exercise is known
                if exercise_name not in known_exercises:
                    # Get muscle groups for the new exercise
                    muscle_groups_info = get_muscle_groups_for_exercise(exercise_name)
                else:
                    # Get muscle groups from the mapping
                    muscle_groups_info = exercise_to_musclegroup.get(
                        exercise_name,
                        {"primary": ["Undefined"], "secondary": ["Undefined"]},
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

    # Save the updated exercise_to_musclegroup mapping
    with open("exercise_to_musclegroup.json", "w") as f:
        json.dump(exercise_to_musclegroup, f, indent=4)

if __name__ == "__main__":
    main()