# Usage
## Preparation
1. You need to download all files in this repo
2. You need to install python 3.10 or later, and make sure your python is added to your path. You can confirm this by running "python3" in cmd or powershell or bash(or the shell you are using)
3. Configure the config.json to specify the booking information. More details coming later
4. Run the bot using runit.bat or runit.sh

## Expected behaviour
1. For the first time running the runit.bat(or runit.sh) will install the dependencies automatically, so it's expected to take more time for the first run
2. Then it will spin up multiple browsers (booking workers) to refresh and check the availability. The more time slots requested and more people requested the more booking workers will be opened. For example, if you want to book 6 people for 3 slots, and each slot has 2 people, it will open up (6 people / 2) * (3 slots) = 9 booking workers
3. It will also open one browser (verfication worker) to check your email inbox if automatic verification is enabled. More on that later.
4. Once the booking workers submit the booking form it will wait at the page where you need to put in the verification code. If you are using automatic verification, you just need to sit and wait each of them get confirmed. If you are using manual verification you need to **go to your email inbox and click on the verification links inside the emails one by one**. Once the booking is verified, the booking worker will close itself in 5 seconds.

## Configuration
All the configuration this bot needs is in the config.json it has the following fields:
1. "url": you need to go to the booking page of your sportsplex, copy the url in the browser and paste it into the json file. The url should be inside the double quote
2. "phoneNum": you need to put your phone number there, this is the phone number you used to check and cancel your booking
3. "emailAddr": you need to put your email there, it will be used for receving the confirmation link
4. "IMAPDomain": automatic verification only, will explain it later. **Leave it blank for manual verification**
5. "password": the password for your email, will explain it later. **Leave it blank for manual verification**
6. "name": your name you use for booking
7. "sport": the name of sport you want to book. It's case insensitive but make sure you typed it correctly
8. "day": the day you want to book, e.g., "wednesday". It's case insensitive but make sure you typed it correctly
9. "timeSlots": the time slots you needed. You can put in multiple slots, but you need to put them inside [] and include the time in "", seperate the time slots with ,. For example "timeSlots": ["8:00 AM","9:00pm","10:00aM"]. It's case insensitive and you can put in extra space
10. "totalPeople": total people you want to book. For those sports that you can book two people perslots, it's recommended to book for even number of people to make it less confuse to check the results.
11. "runHeadless": if set true then no browser will show up, and script will run in backstage, possibly save some resources.

## Use auto verification
It's recommended when you already know how to setup imap access of your email.
**Auto verification will be enabled when IMAPDomain and password are provided in the json file and the information is correct.**
It will show a message in the console when email server is connected and confirm the auto verification is working.
When auto verification is enabled it will automatically go through your email inbox and click on the verification links.
When auto verification is not enabled **you need** to check your email and click on all the links you received. Once all the links are clicked, the bookings will be finalized and the script will close all the browsers.
The auto verification might not work as intended, **if you notice the browser stuck at the verification page, please click on the links manually**.
### Information on configuring your imap access (using gmail)
1. Configure your gmail imap https://www.androidauthority.com/gmail-imap-settings-3059177/
2. Maybe you need to set up an app password https://myaccount.google.com/apppasswords
