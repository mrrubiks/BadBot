from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By
import email
import imaplib
import os
import json
import time as t
import concurrent.futures

def readEmail(config): 
    #Read email and return verification link
    # Connect to the IMAP server
    imap_server = imaplib.IMAP4_SSL(config["IMAPDomain"])
    try:
        imap_server.login(config["emailAddr"], config["password"])
    except:
        print("Failed to login to email server")
        return "wrong password"

    # Select the mailbox (e.g., INBOX)
    imap_server.select("INBOX")

    # Search for emails with the subject containing the verification code and unread
    result, data = imap_server.search(None, '(UNSEEN SUBJECT "Verify your email") FROM "noreply@frontdesksuite.com"')
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

    # Extract the verification link from the email
    linkIdx = email_message.get_payload().strip().find('https://ca.fdesk.click')
    if linkIdx == -1:
        return "fail"
    verificationLink = email_message.get_payload().strip()[linkIdx:]
    # Close the connection to the IMAP server
    imap_server.logout()
    return verificationLink

def verifyEmail(verificationLink, browser):
    browser.get(verificationLink)
    try:
        browser.find_element(By.CLASS_NAME, "content").find_element(By.TAG_NAME,"label").get_attribute("innerHTML")
        return 1
    except:
        return 0

def book(config, time, people, browser):
    browser.get(config["url"])
    # First click on the sport
    try:
        elements = browser.find_elements(By.CLASS_NAME, "content")
        for element in elements:
            if element.get_attribute("innerHTML").lower() == config["sport"].lower():
                element.click()
                break
    except:
        print("No sport found in this Sportplex")
        return -1
    # print("Sport selected")
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
        if config["day"].lower() in text.lower():
            # print("Day selected")
            element.click()
            elements = browser.find_elements(By.CLASS_NAME, "available-time")
            for element in elements:
                text = element.get_attribute("innerHTML")
                if time.lower().replace(" ","") in text.lower().replace(" ",""):
                    # print("Time selected")
                    parent = element.find_element(By.XPATH, "..")
                    browser.execute_script(parent.get_attribute("onclick"))
                    #info page
                    phonenumber = browser.find_element(By.NAME, "PhoneNumber")
                    phonenumber.send_keys(config["phoneNum"])
                    email = browser.find_element(By.NAME, "Email")
                    email.send_keys(config["emailAddr"])
                    name =browser.find_element(By.XPATH, "//input[contains(@id,'field')]")
                    name.send_keys(config["name"])
                    # print("Info filled")
                    submit = browser.find_element(By.ID, "submit-btn")
                    submit.click()
                    try:
                        # Retry if the submission fails
                        while browser.find_element(By.CLASS_NAME, "field-validation-error").get_attribute("innerHTML") == "Retry":
                            # Sleep for 500ms before retrying
                            t.sleep(0.5)
                            submit = browser.find_element(By.ID, "submit-btn")
                            submit.click()
                            # print("Retrying Submit")
                    except:
                        pass
                    if config["autoVerify"]:
                        print("Submitted, waiting for email")
                    else:
                        print("Submitted, please check your email and click on the verification link")
                        print("The booking will be confirmed moments after the verification link is clicked")
                    # wait the other worker to click the verification link
                    # Check if the verification link is clicked by checking if the page is redirected to the booking page
                    current_url = browser.current_url
                    while browser.current_url == current_url:
                        t.sleep(1)
                    submit = browser.find_element(By.ID, "submit-btn")
                    submit.click()
                    # print("Confirm clicked")
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

def testPeoplePerSlot(config):
    options = Options()
    if config["runHeadless"]:
        options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    browser.get(config["url"])
    people = 2
    try:
        elements = browser.find_elements(By.CLASS_NAME, "content")
        for element in elements:
            if element.get_attribute("innerHTML") == config["sport"]:
                element.click()
                break
    except:
        print("No sport found in this Sportplex")
        return -1
    try: 
        numPeople = browser.find_element(By.ID, "reservationCount")
        numPeople.clear()
        numPeople.send_keys(str(people))
        submit = browser.find_element(By.ID, "submit-btn")
        submit.click()
    except:
        people = 1
    browser.quit()
    return people

def booking_worker(config, time, people):
    # Create a new browser instance
    options = Options()
    if config["runHeadless"]:
        options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    result = book(config, time, people, browser)
    while(result == 0):
        print("No slots available, trying again...")
        result = book(config, time, people, browser)
    if result > 0:
        print(f'Booking {config["sport"]} on {config["day"]} at {time} for {result} people was successful')
    else:
        print(f'Booking {config["sport"]} on {config["day"]} at {time} failed')
    t.sleep(3)
    browser.quit()
    return result

def verify_worker(config, numLinks):
    # Create a new browser instance
    options = Options()
    if config["runHeadless"]:
        options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    while numLinks > 0:
        verificationLink = readEmail(config)
        while verificationLink == "fail":
            verificationLink = readEmail(config)
        result = verifyEmail(verificationLink, browser)
        print(f"Verified for {result} bookings")
        numLinks -= result
    browser.quit()
    return

def checkConfig(config):
    # Check if the config file exists, if is, read from it
    config_file = "./config.json"  # Replace with the actual path to your config file
    if os.path.isfile(config_file):
        # Read from the config file
        with open(config_file, "r") as file:
            config = json.load(file)
            if config["totalPeople"] <= 0:
                print("Invalid number of people")
                return
            if not config["day"].lower() in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                print("Invalid day")
                return
    else: #Terminate
        print("Config file not found, create a config file and try again")
        return
    autoVerify = "password" in config and "emailAddr" in config and "IMAPDomain" in config and config["IMAPDomain"] != "" and config["emailAddr"] != "" and config["password"] != ""
    config["autoVerify"] = autoVerify
    if not autoVerify:
        print("Auto verification disabled, please verify your bookings manually")
    if autoVerify:
        while readEmail(config) != "fail":
            if readEmail(config) == "wrong password":
                print("Email login failed, using manual verification!")
                autoVerify = False
                config["autoVerify"] = False
                break
            print("Clearing emails...")
        print("Email server is connected, auto verification is enabled!")
    return config

def foo():
    ChromeDriverManager().install()
    # Check if config file exists, if is, read from it
    config_file = "./config.json"  # Replace with the actual path to your config file
    config = checkConfig(config_file)
    if config == None:
        return
    autoVerify = config["autoVerify"]
    if not autoVerify:
        print("Auto verification is disabled, please verify your bookings manually")
    if autoVerify:
        while readEmail(config) != "fail":
            if readEmail(config) == "wrong password":
                print("Email login failed, using manual verification!")
                autoVerify = False
                config["autoVerify"] = False
                break
            print("Clearing emails...")
        print("Auto verification enabled")
    print(f"Booking {config["totalPeople"]} people for {config["sport"]} on {config["day"]} at {config["timeSlots"]}")
    totalPeople = config["totalPeople"]
    #totalPeoplePerSlot = testPeoplePerSlot(config)
    totalPeoplePerSlot = 2
    numWorkers = len(config["timeSlots"])*(totalPeople//totalPeoplePerSlot + totalPeople%totalPeoplePerSlot) + 1
    # Create a thread pool executor
    with concurrent.futures.ThreadPoolExecutor(max_workers=numWorkers) as executor:
        # Submit the booking tasks to the executor
        while totalPeople > 0:
            numPeople = min(totalPeople, totalPeoplePerSlot)
            for time in config["timeSlots"]:
                booking_futures = [executor.submit(booking_worker, config, time, numPeople) for _ in range(numPeople//totalPeoplePerSlot +  numPeople%totalPeoplePerSlot)]
            totalPeople -= numPeople
        if autoVerify:
            # Submit the verification tasks to the executor
            booking_futures.append(executor.submit(verify_worker, config, numWorkers - 1))
        # Wait for all the booking tasks to complete
        concurrent.futures.wait(booking_futures)

    print("Cancel your bookings here: https://reservation.frontdesksuite.ca/rcfs/cancel")
    input("All Booked. Press Enter to exit...")

foo()
