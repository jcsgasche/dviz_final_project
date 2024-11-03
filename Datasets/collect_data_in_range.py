import sys
import datetime
import csv
import logging
from garminconnect import Garmin
import calendar
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

def get_months_in_range(start_date, end_date):
    months = []
    current_date = start_date.replace(day=1)
    while current_date <= end_date:
        months.append(current_date)
        # Move to the first day of the next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
        # Corrected the increment to move to next month
        current_date = current_date.replace(day=1)
    return months

def main():
    # User credentials
    email = 'janicksteffen@hotmail.com'
    password = '07@Janick@98'

    # Dates
    start_date_str = '2024-08-01'
    end_date_str = '2024-10-31'

    try:
        # Initialize Garmin client
        client = Garmin(email, password)
        client.login()
        logging.info('Logged in to Garmin Connect')

        # Get user profile to obtain full name and unit system
        user_profile = client.get_user_profile()
        logging.info('Retrieved user profile information')
        
        # Debug: Log the contents of user_profile
        logging.debug(f'user_profile data: {user_profile}')
        
        # Get user's full name
        fullname = user_profile.get('fullName') or user_profile.get('displayName') or user_profile.get('userName', 'UnknownUser')
        if not fullname or fullname == 'UnknownUser':
            logging.warning('Could not retrieve user\'s full name. Using "UnknownUser" as default.')
        else:
            logging.info(f'User\'s full name is: {fullname}')
        fullname = fullname.replace(' ', '_')        

        # Get start and end dates
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

        # Get list of months in date range
        months = get_months_in_range(start_date, end_date)

        for month_start in months:
            # Determine start and end date for the current month
            month_end = month_start.replace(day=calendar.monthrange(month_start.year, month_start.month)[1])
            # Adjust dates to be within the overall date range
            period_start = max(start_date, month_start)
            period_end = min(end_date, month_end)

            logging.info(f"Processing data for {period_start} to {period_end}")

            # Initialize data dictionary
            data_per_date = {}

            # Prepare list of dates in the current month
            date_list = []
            current_date = period_start
            while current_date <= period_end:
                date_list.append(current_date)
                data_per_date[current_date.isoformat()] = {'date': current_date.isoformat()}
                current_date += datetime.timedelta(days=1)

            # Fetch data that supports date ranges
            # 6 -- Body composition data for date range
            try:
                body_comp_data = client.get_body_composition(period_start.isoformat(), period_end.isoformat())
                logging.info('Finished fetching body composition data for date range')

                # Debug logging to inspect the data
                logging.debug(f'Body composition data type: {type(body_comp_data)}')
                logging.debug(f'Body composition data content: {body_comp_data}')

                # Process body composition data
                if body_comp_data:
                    if isinstance(body_comp_data, list):
                        for item in body_comp_data:
                            if isinstance(item, dict):
                                date_str = item.get('date')
                                if date_str and date_str in data_per_date:
                                    data_per_date[date_str].update(item)
                            else:
                                logging.warning(f'Unexpected item type in body_comp_data list: {type(item)}')
                    elif isinstance(body_comp_data, dict):
                        # If it's a single dictionary
                        date_str = body_comp_data.get('date')
                        if date_str and date_str in data_per_date:
                            data_per_date[date_str].update(body_comp_data)
                        else:
                            logging.warning('Date not found in body_comp_data or data_per_date')
                    elif isinstance(body_comp_data, str):
                        # Attempt to parse string as JSON
                        try:
                            parsed_data = json.loads(body_comp_data)
                            logging.debug('Parsed body_comp_data string as JSON')
                            # Process parsed data
                            if isinstance(parsed_data, dict):
                                date_str = parsed_data.get('date')
                                if date_str and date_str in data_per_date:
                                    data_per_date[date_str].update(parsed_data)
                                else:
                                    logging.warning('Date not found in parsed body_comp_data or data_per_date')
                            elif isinstance(parsed_data, list):
                                for item in parsed_data:
                                    if isinstance(item, dict):
                                        date_str = item.get('date')
                                        if date_str and date_str in data_per_date:
                                            data_per_date[date_str].update(item)
                                    else:
                                        logging.warning(f'Unexpected item type in parsed body_comp_data list: {type(item)}')
                            else:
                                logging.warning(f'Unexpected parsed body_comp_data type: {type(parsed_data)}')
                        except json.JSONDecodeError:
                            logging.error('Failed to parse body_comp_data string as JSON')
                    else:
                        logging.warning(f'Unexpected body_comp_data type: {type(body_comp_data)}')
                else:
                    logging.warning('No body composition data returned')
            except Exception as e:
                logging.error(f'Error processing body composition data: {e}')

            # Fetch other data that supports date ranges (apply similar error handling)
            # - -- Daily step data for date range
            try:
                steps_data = client.get_steps_data(period_start.isoformat(), period_end.isoformat())
                logging.info('Finished fetching steps data for date range')

                logging.debug(f'Steps data type: {type(steps_data)}')
                logging.debug(f'Steps data content: {steps_data}')

                if steps_data:
                    if isinstance(steps_data, list):
                        for item in steps_data:
                            if isinstance(item, dict):
                                date_str = item.get('date')
                                if date_str and date_str in data_per_date:
                                    data_per_date[date_str].update({'steps': item.get('steps', 0)})
                            else:
                                logging.warning(f'Unexpected item type in steps_data list: {type(item)}')
                    else:
                        logging.warning(f'Unexpected steps_data type: {type(steps_data)}')
                else:
                    logging.warning('No steps data returned')
            except Exception as e:
                logging.error(f'Error processing steps data: {e}')

            # Fetch data that requires per-day API calls
            for date in date_list:
                date_str = date.isoformat()

                # Example for fetching activity stats
                try:
                    # 3 -- Activity data for the day
                    stats = client.get_stats(date_str)
                    logging.info(f'Finished fetching activity stats for {date_str}')
                    logging.debug(f'Activity stats data: {stats}')
                    if stats:
                        data_per_date[date_str].update(stats)
                except Exception as e:
                    logging.error(f'Error fetching activity stats for {date_str}: {e}')

                # Apply similar error handling for other per-day methods

            # Save data to CSV
            all_data = list(data_per_date.values())

            # Collect all possible fieldnames
            fieldnames = set()
            for data in all_data:
                if isinstance(data, dict):
                    fieldnames.update(data.keys())
                else:
                    logging.warning(f'Unexpected data type in all_data: {type(data)}')

            fieldnames = sorted(fieldnames)

            # Save data to CSV
            filename = f"{fullname}_{period_start.strftime('%Y-%m')}.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for data in all_data:
                    if isinstance(data, dict):
                        writer.writerow(data)
                    else:
                        logging.warning(f'Skipping data with unexpected type: {type(data)}')

            logging.info(f"Data for {period_start.strftime('%B %Y')} saved to {filename}")
            logging.info(f"Finished processing month: {period_start.strftime('%B %Y')}")

        logging.info("Data extraction completed.")

    except Exception as e:
        logging.error("An error occurred: " + str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()


