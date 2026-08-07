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
        timeout=20
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
            "Текст поста не найден"
        )


    return post.get_text("\n")



def clean(line):

    return (
        line
        .replace("**", "")
        .replace("\xa0", " ")
        .replace("•", "")
        .strip()
    )



def parse_tournaments():

    text = load_post()


    lines = [
        clean(x)
        for x in text.split("\n")
        if clean(x)
    ]


    tournaments = []

    current_day = None
    current_month = None

    current_time = None
    current_title = []


    def save_current():

        nonlocal current_time, current_title

        if current_time and current_title:

            tournaments.append(
                {
                    "day": current_day,
                    "month": current_month,
                    "time": current_time,
                    "title": " ".join(current_title)
                }
            )


        current_time = None
        current_title = []



    for line in lines:


        # дата

        date = re.match(
            r"(\d+)\s+([а-яА-Я]+)",
            line.lower()
        )


        if date:

            save_current()


            current_day = int(
                date.group(1)
            )


            current_month = MONTHS.get(
                date.group(2)
            )


            continue



        # время

        time = re.match(
            r"(\d{1,2}:\d{2})",
            line
        )


        if time:

            save_current()


            current_time = time.group(1)


            continue



        # текст турнира

        if current_time:

            current_title.append(
                line
            )


    save_current()


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
