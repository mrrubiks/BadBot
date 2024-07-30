# Usage Guide

## Preparation
1. Download all files from this repository.
2. Install Python 3.10 or later. Ensure Python is added to your PATH. Confirm this by running `python3` in CMD, PowerShell, or your preferred shell.
3. Configure the `config.json` file to specify the booking information. Details are provided below.
4. Run the bot using `runit.bat` (for Windows) or `runit.sh` (for Unix-based systems).

## Expected Behavior
1. On the first run, executing `runit.bat` or `runit.sh` will automatically install the necessary dependencies. This initial setup may take some time.
2. The bot will open multiple browser instances (booking workers) to refresh and check availability. The number of booking workers depends on the number of time slots and people requested. For example, to book 6 people for 3 slots (2 people per slot), the bot will open `(6 people / 2) * 3 slots = 9 booking workers`.
3. If automatic verification is enabled, the bot will also open one browser instance (verification worker) to check your email inbox.
4. After the booking workers submit the booking form, they will wait on the verification code page. If using automatic verification, wait for the bot to confirm each booking. If using manual verification, check your email inbox and click the verification links. Once verified, each booking worker will close itself after 5 seconds.

## Configuration
The bot's configuration is stored in `config.json` and includes the following fields:

1. `"url"`: Copy the booking page URL from your sportsplex's website and paste it here.
2. `"phoneNum"`: Enter the phone number used for checking and canceling bookings.
3. `"emailAddr"`: Enter the email address for receiving confirmation links.
4. `"IMAPDomain"`: For automatic verification only. Leave it blank for manual verification.
5. `"password"`: For automatic verification only. Leave it blank for manual verification.
6. `"name"`: Enter the name used for booking.
7. `"sport"`: Enter the name of the sport you want to book. Case insensitive.
8. `"day"`: Enter the day you want to book (e.g., "Wednesday"). Case insensitive.
9. `"timeSlots"`: Enter the desired time slots inside brackets, each enclosed in quotes and separated by commas. For example, `"timeSlots": ["8:00 AM","9:00 PM","10:00 AM"]`. Case insensitive.
10. `"totalPeople"`: Enter the number of people you want to book for. For sports allowing two people per slot, an even number is recommended.
11. `"runHeadless"`: Set to `true` to run the script without showing browser windows, which can save resources.

## Using Auto Verification
Auto verification is recommended if you have set up IMAP access for your email. Auto verification is enabled when `IMAPDomain` and `password` are provided and correct in the `config.json` file. 

- The console will confirm when the email server is connected and auto verification is active.
- If auto verification is enabled, the bot will automatically process verification links in your inbox.
- If auto verification is not enabled, you must manually check your email and click on all received verification links. The script will finalize bookings and close browsers once all links are clicked.
- If the browser gets stuck on the verification page, manually click the verification links.

### Configuring IMAP Access (Using Gmail)
1. Follow instructions to configure Gmail IMAP: [Gmail IMAP Settings](https://www.androidauthority.com/gmail-imap-settings-3059177/)
2. You may need to set up an app password: [Gmail App Passwords](https://myaccount.google.com/apppasswords)
