import re
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo


POST_URL = "https://t.me/s/pingtablet/3977"

CHANNEL = "pingtablet"
POST_ID = "3977"

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


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


def clean_text(text):

    text = re.sub(
        r"[\u200b\u200c\u200d\u2060\ufeff]",
        "",
        text
    )

    text = text.replace(
        "\xa0",
        " "
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def load_post():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        )
    }


    response = requests.get(
        POST_URL,
        headers=headers,
        timeout=20
    )


    response.raise_for_status()


    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    # =====================================
    # ИЩЕМ ИМЕННО POST 3977
    # =====================================

    target = soup.find(
        attrs={
            "data-post": f"{CHANNEL}/{POST_ID}"
        }
    )


    if target:

        post_text = target.find(
            "div",
            class_="tgme_widget_message_text"
        )


        if post_text:

            text = post_text.get_text(
                "\n",
                strip=True
            )


            print(
                "✅ НАЙДЕН ИМЕННО POST:",
                f"{CHANNEL}/{POST_ID}"
            )


            return text


    # =====================================
    # РЕЗЕРВНЫЙ ВАРИАНТ
    # =====================================

    print(
        "⚠️ data-post не найден"
    )


    posts = soup.find_all(
        "div",
        class_="tgme_widget_message"
    )


    for post in posts:

        data_post = post.get(
            "data-post",
            ""
        )


        if data_post == (
            f"{CHANNEL}/{POST_ID}"
        ):

            post_text = post.find(
                "div",
                class_="tgme_widget_message_text"
            )


            if post_text:

                return post_text.get_text(
                    "\n",
                    strip=True
                )


    raise Exception(
        f"Не удалось найти сообщение "
        f"{CHANNEL}/{POST_ID}"
    )


def parse_tournaments():

    text = load_post()


    print(
        "========== НАШ ПОСТ =========="
    )

    print(text)

    print(
        "========== КОНЕЦ =========="
    )


    # =====================================
    # Убираем невидимые символы
    # =====================================

    text = re.sub(
        r"[\u200b\u200c\u200d\u2060\ufeff]",
        "",
        text
    )


    # =====================================
    # Ищем даты
    # =====================================

    date_pattern = re.compile(
        r"(\d{1,2})\s+"
        r"(января|февраля|марта|апреля|мая|июня|"
        r"июля|августа|сентября|октября|ноября|декабря)",
        re.IGNORECASE
    )


    dates = list(
        date_pattern.finditer(text)
    )


    print(
        "НАЙДЕНО ДАТ:",
        len(dates)
    )


    tournaments = []


    for i, date_match in enumerate(dates):

        day = int(
            date_match.group(1)
        )


        month_name = (
            date_match.group(2)
            .lower()
        )


        month = MONTHS.get(
            month_name
        )


        if month is None:

            continue


        # =================================
        # Блок текущей даты
        # =================================

        start = date_match.end()


        if i + 1 < len(dates):

            end = dates[
                i + 1
            ].start()

        else:

            end = len(text)


        block = text[
            start:end
        ]


        # =================================
        # Ищем время
        # =================================

        times = list(
            re.finditer(
                r"(\d{1,2}:\d{2})",
                block
            )
        )


        for j, time_match in enumerate(times):

            time = time_match.group(1)


            start_title = (
                time_match.end()
            )


            if j + 1 < len(times):

                end_title = (
                    times[j + 1].start()
                )

            else:

                end_title = len(block)


            title = block[
                start_title:end_title
            ]


            title = clean_text(
                title
            )


            title = re.sub(
                r"^[•\-–—]+",
                "",
                title
            )


            title = clean_text(
                title
            )


            if not title:

                continue


            tournaments.append({

                "day": day,

                "month": month,

                "time": time,

                "title": title

            })


    # =====================================
    # Дубликаты
    # =====================================

    result = []

    seen = set()


    for tournament in tournaments:

        key = (
            tournament["day"],
            tournament["month"],
            tournament["time"],
            tournament["title"]
        )


        if key in seen:

            continue


        seen.add(key)

        result.append(
            tournament
        )


    print(
        "========== ВСЕ ТУРНИРЫ =========="
    )


    for tournament in result:

        print(
            tournament
        )


    return result


def today_tournaments():

    now = datetime.now(
        MOSCOW_TZ
    )


    print(
        "========== СЕГОДНЯ =========="
    )

    print(
        "МОСКВА:",
        now.strftime(
            "%d.%m.%Y %H:%M:%S"
        )
    )


    print(
        "ИЩЕМ ДАТУ:",
        now.day,
        now.month
    )


    tournaments = parse_tournaments()


    result = []


    for tournament in tournaments:

        if (
            tournament["day"] == now.day
            and
            tournament["month"] == now.month
        ):

            result.append(
                tournament
            )


    print(
        "СЕГОДНЯШНИЕ:",
        result
    )


    return result


if __name__ == "__main__":

    today_tournaments()
