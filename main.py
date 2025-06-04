from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os
import time
import datetime

# Parametry wyszukiwania
MAX_PRICE = 1200
MEAL = "All Inclusive"  # fraza do sprawdzania w tytule
ADULTS = 1

import os

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

if EMAIL is None:
    print("EMAIL is not set!")
else:
    print(f"EMAIL is set to: {EMAIL}")

if APP_PASSWORD is None:
    print("APP_PASSWORD is not set!")
else:
    print("APP_PASSWORD is set.")

def send_email(subject, body):
    if not EMAIL or not APP_PASSWORD:
        print("EMAIL or APP_PASSWORD is not set!")
        return

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['To'] = EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
        print("E-mail sent.")
    except Exception as e:
        print(f"Email error: {e}")

def scrape_wakacje():
    print("Scraping wakacje.pl...")

    options = Options()
    options.headless = True

    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)

    url = "https://www.wakacje.pl/wczasy/?all-inclusive,dla-singli,tanio&src=fromSearch"
    driver.get(url)

    time.sleep(7)  # Czekamy na załadowanie ofert

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "lxml")
    offers = []

    for offer in soup.select('div.offer-box'):
        try:
            title = offer.select_one('h2.offer-title').text.strip()
            price_text = offer.select_one('span.price-current').text
            price = int(price_text.replace("zł", "").replace(" ", "").replace("PLN", "").strip())
            link = "https://www.wakacje.pl" + offer.select_one('a.offer')['href']
            if price <= MAX_PRICE and MEAL.lower() in title.lower():
                offers.append(f"{title} - {price} zł\n{link}\n")
        except Exception:
            continue

    return offers

def main():
    found_offers = scrape_wakacje()
    if found_offers:
        body = "Znalezione oferty wakacji:\n\n" + "\n".join(found_offers)
        send_email("Tanie wakacje poniżej 1200 zł!", body)
    else:
        print("Brak ofert spełniających kryteria.")

if __name__ == "__main__":
    main()
