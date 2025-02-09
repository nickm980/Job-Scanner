import os
import json
import smtplib
import time
import schedule
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from googlesearch import search


EMAIL_ADDRESS = ""      # Sender's email address
EMAIL_PASSWORD = ""          # app-specific password
RECIPIENT_EMAIL = ""       # Recipient email address

SEEN_LINKS_FILE = "seen_links.json"

# Change based on what jobs you want
SEARCH_QUERY = ('site:boards.greenhouse.io united states intext:"apply" '
                '(intext:"Software Developer intern" OR intext:"Software Engineer intern")')
NUM_RESULTS = 200 


def load_seen_links():
    if os.path.exists(SEEN_LINKS_FILE):
        try:
            with open(SEEN_LINKS_FILE, "r") as f:
                seen_links = json.load(f)
                return set(seen_links)
        except Exception as e:
            print("Error loading seen links:", e)
            return set()
    return set()

def save_seen_links(seen_links):
    try:
        with open(SEEN_LINKS_FILE, "w") as f:
            json.dump(list(seen_links), f)
    except Exception as e:
        print("Error saving seen links:", e)

def send_email(links):
    """Send an email with the provided links along with the listing date."""
    listing_date = time.strftime('%Y-%m-%d %H:%M:%S')
    
    subject = f"Job Listings Update - {listing_date}"
    
    body = f"Job listings as of {listing_date}:\n\n" + "\n".join(links)

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection.
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print("Error sending email:", e)


def search_job_links():
    """Perform the Google search and return a list of URLs."""
    results = []
    try:
        for url in search(SEARCH_QUERY, num_results=NUM_RESULTS):
            results.append(url)
    except Exception as e:
        print("Error during Google search:", e)
    return results


def job_search_task():
    print("Running job search task...")

    current_links = set(search_job_links())
    print(f"Found {len(current_links)} links from the search.")

    if current_links:
        print("Sending email with the current job listings...")
        send_email(list(current_links))
    else:
        print("No job links found to send.")


if __name__ == "__main__":
    job_search_task()

    schedule.every().day.at("09:00").do(job_search_task)

    print("Scheduler started. Waiting for the next scheduled run...")

    while True:
        schedule.run_pending()
        time.sleep(60)
