from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import email
import imaplib

# Default values, change if needed
url = "https://reservation.frontdesksuite.ca/rcfs/nepeansportsplex/Home/Index?Culture=en&PageId=b0d362a1-ba36-42ae-b1e0-feefaf43fe4c&ShouldStartReserveTimeFlow=False&ButtonId=00000000-0000-0000-0000-000000000000"
phoneNum = "6475677418"
emailAddr = "nick.zhang418@gmail.com"
IMAPDomain = "imap.gmail.com"
password = "dzmt lost bibs fyey"
name = "Nick Zhang"

browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def readEmail(): 
    #Read email and return verification code
    # Connect to the IMAP server
    imap_server = imaplib.IMAP4_SSL(IMAPDomain)
    imap_server.login(emailAddr, password)

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

def book(sport, day, time, phoneNumber, emailAddress, bookingName, people = 2):
    browser.get(url)
    # First click on the sport
    try:
        elements = browser.find_elements(By.CLASS_NAME, "content")
        for element in elements:
            if element.get_attribute("innerHTML") == sport:
                element.click()
                break
    except:
        print("No sport found in this Sportplex")
        return -1
    #Fill in details
    #time select
    elements = browser.find_elements(By.CLASS_NAME, "header-text")
    for element in elements:
        text = element.get_attribute("innerHTML")
        if day in text:
            element.click()
            elements = browser.find_elements(By.CLASS_NAME, "available-time")
            for element in elements:
                text = element.get_attribute("innerHTML")
                if time in text:
                    parent = element.find_element(By.XPATH, "./..")
                    parent.click()
                    #info page
                    phonenumber = browser.find_element(By.NAME, "PhoneNumber")
                    phonenumber.send_keys(phoneNumber)
                    email = browser.find_element(By.NAME, "Email")
                    email.send_keys(emailAddress)
                    name = browser.find_element(By.NAME, "field2021")
                    name.send_keys(bookingName)
                    submit = browser.find_element(By.ID, "submit-btn")
                    submit.click()
                    # wait for the email to come in
                    verification = "fail"
                    while verification == "fail":
                        verification = readEmail()
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
                            return 1
                        else:
                            return -1
                    except:
                        return -1
    # No slots available
    return 0



def foo():
    while readEmail() != "fail":
        print("Clearing emails...")
    totalPeople = int(input("How many people are you booking for? Press Enter for default 2\n") or 2)
    sport = input("What sport are you booking for? Press Enter for default (Badminton)\n") or "Badminton"
    day = input("What day are you booking for? (Only book for one day at a time, put 1 for Monday, 2 for Tuesday, etc.) Press Enter for default (1)\n") or 1
    day = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][int(day) - 1]
    timeSlots = input("How many time slots are you booking? Format: 6:00 PM,7:00 PM,8:00 PM, no spaces around comma\n").split(",")
    print("Using default sportsplex, phone number, email address and name, change in code if needed")
    print(f"Booking {totalPeople} people for {sport} on {day} at {timeSlots}")
    while totalPeople > 0:
        if totalPeople >= 2:
            numPeople = 2
        else:
            numPeople = 1
        for time in timeSlots:
            result = book(sport, day, time, phoneNum, emailAddr, name, numPeople)
            while(result == 0):
                print("No slots available, trying again...")
                result = book(sport, day, time, phoneNum, emailAddr, name, numPeople)
            if result > 0:
                print(f'Booking {sport} on {day} at {time} for {numPeople} people was successful')
                totalPeople -= numPeople
            else:
                print(f'Booking {sport} on {day} at {time} failed')
    print("Cancel your bookings here: https://reservation.frontdesksuite.ca/rcfs/cancel")
foo()