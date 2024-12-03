from garminconnect import Garmin, GarminConnectAuthenticationError
import getpass

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
        else:
            print("Login failed due to authentication error.")
    except Exception as e:
        print("Error logging in to Garmin Connect:", e)

if __name__ == "__main__":
    main()
