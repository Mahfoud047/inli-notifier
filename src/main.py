import requests
from bs4 import BeautifulSoup
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os



SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
BASE_URL = os.getenv("BASE_URL")
URL = os.getenv("URL")

CACHE_FILE = "cache_ids.txt"

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return set()
    with open(CACHE_FILE, "r") as f:
        return set(f.read().splitlines())

# Save cache
def save_to_cache(new_ids):
    with open("cache.txt", "w") as f:
       f.write("\n".join(new_ids))

# Send email notification
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    print(EMAIL_SENDER)
    server.login(EMAIL_SENDER, EMAIL_PASSWORD)
    server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
    server.quit()



def scrape():
    cache = load_cache()
    resp = requests.get(URL)
    soup = BeautifulSoup(resp.text, "html.parser")

    for block in soup.select("div.featured-item"):
        link_tag = block.select_one("a[href^='/locations/offre']")
        details = block.select_one("div.featured-details span")
        if not link_tag or not details:
            continue

        text = details.get_text(strip=True)
        unique_id = hashlib.md5(text.encode("utf-8")).hexdigest()

        if unique_id not in cache:
            send_email("New Item Found", f"Details:\n{text}\nLink: {BASE_URL}{link_tag['href']}")
            cache.add(unique_id)

    save_to_cache(cache)

if __name__ == "__main__":
    scrape()
