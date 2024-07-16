from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import email
import imaplib
import os
import json
import time as t

# Default values, change if needed
config = {
    "url": "https://reservation.frontdesksuite.ca/rcfs/nepeansportsplex/Home/Index?Culture=en&PageId=b0d362a1-ba36-42ae-b1e0-feefaf43fe4c&ShouldStartReserveTimeFlow=False&ButtonId=00000000-0000-0000-0000-000000000000",
    "phoneNum": "6470000000",
    "emailAddr": "email@gmail.com",
    "IMAPDomain": "imap.gmail.com",
    "password": "psw",
    "name": "Your Name in the Booking System",
    "sport": "Badminton",
    "day": "Wednesday",
    "timeSlots": ["7:00 AM"],
    "totalPeople": 2
}

browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def readEmail(config): 
    #Read email and return verification code
    # Connect to the IMAP server
    imap_server = imaplib.IMAP4_SSL(config["IMAPDomain"])
    imap_server.login(config["emailAddr"], config["password"])

    # Select the mailbox (e.g., INBOX)
    imap_server.select("INBOX")

    # Search for emails with the subject containing the verification code and unread
    result, data = imap_server.search(None, '(UNSEEN SUBJECT "Verify your email")')
    if result != "OK" or len(data[0]) == 0:
        return "fail"
    # Get the latest email
    latest_email_id = data[0].split()[-1]
    result, email_data = imap_server.fetch(latest_email_id, "(RFC822)")
    if not email_data:
        return "fail"
    # Parse the email data
    raw_email = email_data[0][1]
    email_message = email.message_from_bytes(raw_email)

    # Extract the verification code from the email body
    # Extract the verification code from the email body
    verification_code = None
    if email_message.is_multipart():
        for part in email_message.get_payload():
            if part.get_content_type() == "text/plain":
                verification_code = part.get_payload().strip().split(":")[1].split(".")[0]
                break
    else:
        verification_code = email_message.get_payload().strip().split(":")[1].split(".")[0]

    # Close the connection to the IMAP server
    imap_server.logout()

    # Strip any leading/trailing whitespaces
    verification_code = verification_code.strip()
    return verification_code

def book(config, time, people):
    browser.get(config["url"])
    # First click on the sport
    try:
        elements = browser.find_elements(By.CLASS_NAME, "content")
        for element in elements:
            if element.get_attribute("innerHTML") == config["sport"]:
                element.click()
                break
    except:
        print("No sport found in this Sportplex")
        return -1
    #Some sportsplexes require you to select the number of people before selecting the sport
    try: 
        numPeople = browser.find_element(By.ID, "reservationCount")
        numPeople.clear()
        numPeople.send_keys(str(people))
        submit = browser.find_element(By.ID, "submit-btn")
        submit.click()
    except:
        people = 1
    #Fill in details
    #time select
    elements = browser.find_elements(By.CLASS_NAME, "header-text")
    for element in elements:
        text = element.get_attribute("innerHTML")
        if config["day"] in text:
            element.click()
            elements = browser.find_elements(By.CLASS_NAME, "available-time")
            for element in elements:
                text = element.get_attribute("innerHTML")
                if time in text:
                    parent = element.find_element(By.XPATH, "./..")
                    parent.click()
                    #info page
                    phonenumber = browser.find_element(By.NAME, "PhoneNumber")
                    phonenumber.send_keys(config["phoneNum"])
                    email = browser.find_element(By.NAME, "Email")
                    email.send_keys(config["emailAddr"])
                    name = browser.find_element(By.NAME, "field2021")
                    name.send_keys(config["name"])
                    submit = browser.find_element(By.ID, "submit-btn")
                    submit.click()
                    try:
                        # Retry if the submission fails
                        while browser.find_element(By.CLASS_NAME, "field-validation-error").get_attribute("innerHTML") == "Retry":
                            # Sleep for 500ms before retrying
                            t.sleep(0.5)
                            submit = browser.find_element(By.ID, "submit-btn")
                            submit.click()
                    except:
                        pass
                    # wait for the email to come in
                    verification = "fail"
                    while verification == "fail":
                        verification = readEmail(config)
                    verificationBox = browser.find_element(By.ID, "code")
                    verificationBox.send_keys(str(verification))
                    submit = browser.find_element(By.CLASS_NAME, "mdc-button")
                    submit.click()
                    submit = browser.find_element(By.ID, "submit-btn")
                    submit.click()
                    # Check if the booking is successful by checking if there is a confirmation message displayed
                    try:
                        confirmation_message = browser.find_element(By.CLASS_NAME, "main-content").find_element(By.CLASS_NAME,"section").find_element(By.TAG_NAME, "h1").get_attribute("innerHTML")
                        if confirmation_message == "Confirmation":
                            return people
                        else:
                            return -1
                    except:
                        return -1
    # No slots available
    return 0



def foo(config):
    # Check if config file exists, if is, read from it
    config_file = "./config.json"  # Replace with the actual path to your config file
    if os.path.isfile(config_file):
        # Read from the config file
        with open(config_file, "r") as file:
            config = json.load(file)
    else:
        print("Config file not found, using default values!")
    while readEmail(config) != "fail":
        print("Clearing emails...")
    print(f"Booking {config["totalPeople"]} people for {config["sport"]} on {config["day"]} at {config["timeSlots"]}")
    totalPeople = config["totalPeople"]
    while totalPeople > 0:
        if totalPeople >= 2:
            numPeople = 2
        else:
            numPeople = 1
        for time in config["timeSlots"]:
            result = book(config, time, numPeople)
            while(result == 0):
                print("No slots available, trying again...")
                result = book(config, time, numPeople)
            if result > 0:
                print(f'Booking {config["sport"]} on {config["day"]} at {time} for {result} people was successful')
                totalPeople -= result
            else:
                print(f'Booking {config["sport"]} on {config["day"]} at {time} failed')
    print("Cancel your bookings here: https://reservation.frontdesksuite.ca/rcfs/cancel")
    print("Done! Quitting in 5 seconds...")
    t.sleep(5)
    browser.quit()
    input("Press Enter to exit...")

foo(config)
