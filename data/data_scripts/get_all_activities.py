import logging
from garminconnect import Garmin
import calendar
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

def main():
    # User credentials
    email = 'janicksteffen@hotmail.com'
    password = '07@Janick@98'

    try:
        # Initialize Garmin client
        client = Garmin(email, password)
        client.login()
        logging.info('Logged in to Garmin Connect\n')

        # activities = client.get_activities_fordate("2024-08-01")
        activities = client.get_activities(0,30)
        with open('../activities.json', 'w') as json_file:
            json.dump(activities, json_file, indent=4)
            logging.info('Activities saved to activities.json\n')

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise ConnectionError

if __name__ == "__main__":
    main()