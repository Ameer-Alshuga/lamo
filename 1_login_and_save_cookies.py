# File: 1_login_and_save_cookies.py

import asyncio
from twikit import Client

# --- Your Login Settings ---
# !!! IMPORTANT: Replace with your credentials !!!
USERNAME = ''
EMAIL = '' 
PASSWORD = ''
COOKIE_FILE_PATH = 'my_cookies.json' # This is where the session will be saved

async def main():
    """
    Logs into Twitter and saves the session cookies to a file.
    """
    client = Client('en-US')
    try:
        print(f"Attempting to log in with account: {USERNAME}...")
        await client.login(
            auth_info_1=USERNAME,
            auth_info_2=EMAIL,
            password=PASSWORD
        )
        # After a successful login, save the cookies
        client.save_cookies(COOKIE_FILE_PATH)
        print(f"\nSUCCESS: Login successful and cookies have been saved to '{COOKIE_FILE_PATH}'")
        print("You can now run the main scraper script.")

    except Exception as e:
        print(f"\nERROR: Login failed. Reason: {e}")
        print("Please log in to twitter.com in a regular web browser first to resolve any CAPTCHAs or security checks, then try running this script again.")

# Run the main asynchronous function
if __name__ == '__main__':
    asyncio.run(main())