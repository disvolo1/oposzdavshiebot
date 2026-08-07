import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup


POST_URL = "https://t.me/pingtablet/3977"


MONTHS = {
    1: "января",
    2: "февраля",
    3: "марта",
    4: "апреля",
    5: "мая",
    6: "июня",
    7: "июля",
    8: "августа",
    9: "сентября",
    10: "октября",
    11: "ноября",
    12: "декабря",
}


def get_post_text() -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/137.0 Safari/537.36"
        )
    }

    html = requests.get(POST_URL, headers=headers, timeout=15).text

    soup = BeautifulSoup(html, "html.parser")

    message = soup.select_one(".tgme_widget_message_text")

    if message is None:
        raise Exception("Не удалось получить текст сообщения Telegram")

    return message.get_text("\n")


def get_today_tournaments():
    text = get_post_text()

    today = datetime.now()

    today_header = f"{today.day} {MONTHS[today.month]}"

    lines = text.splitlines()

    collecting = False
    tournaments = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if today_header in line.lower():
            collecting = True
            continue

        if collecting and re.match(r"^\d+\s+[а-я]+$", line.lower()):
            break

        if collecting:
            m = re.match(r"(\d\d:\d\d)\s+(.*)", line)

            if m:
                tournaments.append({
                    "time": m.group(1),
                    "title": m.group(2)
                })

    return tournaments


if __name__ == "__main__":
    print(get_today_tournaments())
