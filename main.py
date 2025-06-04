# wakacje-scraper: Wyszukiwarka tanich wakacji (wakacje.pl + itaka.pl)
# Działa w Render.com (bez Selenium)

import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import datetime

# Parametry wyszukiwania
MAX_PRICE = 1200
MEAL = "AI"  # AI = All Inclusive
ADULTS = 1

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['To'] = EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL, APP_PASSWORD)
        smtp.send_message(msg)

def scrape_wakacje_pl():
    print("[wakacje.pl] Szukanie ofert...")
    url = f"https://www.wakacje.pl/wczasy/?od-when=any&od-city=any&adults={ADULTS}&meal={MEAL}&price-to={MAX_PRICE}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')

    offers = []
    for offer in soup.select('div.offer-box'):
        try:
            title = offer.select_one('h2.offer-title').text.strip()
            price = int(offer.select_one('span.price-current').text.strip().replace("zł", "").replace(" ", "").replace("PLN", ""))
            link = 'https://www.wakacje.pl' + offer.select_one('a.offer')['href']
            if price <= MAX_PRICE:
                offers.append(f"[wakacje.pl] {title} - {price} zł\n{link}\n")
        except Exception:
            continue
    return offers

def scrape_itaka_pl():
    print("[itaka.pl] Szukanie ofert...")
    url = f"https://www.itaka.pl/wyszukiwarka/?adults={ADULTS}&departure=any&priceTo={MAX_PRICE}&meal={MEAL}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')

    offers = []
    for offer in soup.select(".product-list-item"):
        try:
            title = offer.select_one(".product-name").text.strip()
            price = int(offer.select_one(".price-value").text.strip().replace("zł", "").replace(" ", ""))
            link = "https://www.itaka.pl" + offer.select_one("a")['href']
            if price <= MAX_PRICE:
                offers.append(f"[itaka.pl] {title} - {price} zł\n{link}\n")
        except Exception:
            continue
    return offers

def main():
    all_offers = []
    all_offers += scrape_wakacje_pl()
    all_offers += scrape_itaka_pl()

    if all_offers:
        body = "Znalezione tanie wakacje (" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + ")\n\n"
        body += "\n".join(all_offers)
        send_email("Tanie wakacje poniżej 1200 zł!", body)
        print("Wysłano e-mail.")
    else:
        print("Brak ofert spełniających kryteria.")

if __name__ == "__main__":
    main()
