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

    response = requests.get(
        POST_URL,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    post = soup.find(
        "div",
        class_="tgme_widget_message_text"
    )


    if not post:
        raise Exception(
            "Пост не найден"
        )


    return post.get_text("\n")



def clean_line(line):

    return (
        line
        .replace("**", "")
        .replace("\xa0", " ")
        .strip()
    )



def parse_tournaments():

    text = load_post()


    lines = [
        clean_line(line)
        for line in text.split("\n")
        if clean_line(line)
    ]


    tournaments = []


    current_day = None
    current_month = None


    i = 0


    while i < len(lines):

        line = lines[i]


        # дата

        date = re.match(
            r"(\d+)\s+([а-яА-Я]+)",
            line
        )


        if date:

            current_day = int(
                date.group(1)
            )


            current_month = MONTHS.get(
                date.group(2).lower()
            )


            i += 1
            continue



        # турнир

        tournament = re.match(
            r"•\s*(\d{1,2}:\d{2})\s+(.*)",
            line
        )


        if tournament and current_day:


            time = tournament.group(1)

            title = tournament.group(2)


            # убираем markdown ссылки
            title = re.sub(
                r"\[([^\]]+)\]\([^)]+\)",
                r"\1",
                title
            )


            tournaments.append(
                {
                    "day": current_day,
                    "month": current_month,
                    "time": time,
                    "title": title
                }
            )


        i += 1


    return tournaments



def today_tournaments():

    today = datetime.now()


    result = []


    for tournament in parse_tournaments():

        if (
            tournament["day"] == today.day
            and
            tournament["month"] == today.month
        ):

            result.append(
                tournament
            )


    print(
        "Сегодняшние:",
        result
    )


    return result



if __name__ == "__main__":

    for t in today_tournaments():
        print(t)
