import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

POST_URL = "https://t.me/s/pingtablet/3977"

MONTHS = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


def load_post():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    html = requests.get(POST_URL, headers=headers, timeout=15).text

    soup = BeautifulSoup(html, "html.parser")

    post = soup.find("div", class_="tgme_widget_message_text")

    if not post:
        raise Exception("Не удалось получить текст поста")

    return post.get_text("\n")


def parse_tournaments():

    text = load_post()

    lines = [i.strip() for i in text.split("\n") if i.strip()]

    tournaments = []

    current_day = None
    current_month = None

    for line in lines:

        m = re.match(r"(\d+)\s+([а-я]+)", line.lower())

        if m:

            current_day = int(m.group(1))
            current_month = MONTHS[m.group(2)]

            continue

        t = re.match(r"(\d\d:\d\d)\s+(.*)", line)

        if t and current_day:

            tournaments.append({
                "day": current_day,
                "month": current_month,
                "time": t.group(1),
                "title": t.group(2)
            })

    return tournaments


def today_tournaments():

    today = datetime.now()

    result = []

    for t in parse_tournaments():

        if t["day"] == today.day and t["month"] == today.month:

            result.append(t)

    return result


if __name__ == "__main__":

    for t in today_tournaments():

        print(f'{t["time"]} — {t["title"]}')
