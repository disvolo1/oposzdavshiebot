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


    html = requests.get(
        POST_URL,
        headers=headers,
        timeout=15
    ).text


    soup = BeautifulSoup(
        html,
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


    text = post.get_text("\n")


    print("========== ТЕКСТ ПОСТА ==========")
    print(text)
    print("========== КОНЕЦ ==========")


    return text



def clean_line(line):

    return (
        line
        .replace("**", "")
        .strip()
    )



def parse_tournaments():

    text = load_post()


    lines = [
        clean_line(line)
        for line in text.split("\n")
        if line.strip()
    ]


    print("========== СТРОКИ ==========")

    for line in lines:
        print(repr(line))

    print("========== КОНЕЦ СТРОК ==========")


    tournaments = []

    current_day = None
    current_month = None


    for line in lines:


        date_match = re.match(
            r"(\d+)\s+([а-яА-Я]+)",
            line
        )


        if date_match:

            current_day = int(
                date_match.group(1)
            )

            month = (
                date_match.group(2)
                .lower()
            )


            if month in MONTHS:

                current_month = MONTHS[month]


            continue



        tournament_match = re.match(
            r"(\d{2}:\d{2})\s+(.*)",
            line
        )


        if tournament_match and current_day:


            tournaments.append(
                {
                    "day": current_day,
                    "month": current_month,
                    "time": tournament_match.group(1),
                    "title": tournament_match.group(2)
                }
            )


    print("========== НАЙДЕНО ==========")

    for tournament in tournaments:
        print(tournament)

    print("=============================")


    return tournaments



def today_tournaments():

    today = datetime.now()


    print(
        "Сегодня:",
        today.day,
        today.month
    )


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
        "Сегодняшние турниры:",
        result
    )


    return result



if __name__ == "__main__":

    today_tournaments()
