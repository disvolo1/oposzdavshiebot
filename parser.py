import re
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo


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


# Москва
MOSCOW_TZ = ZoneInfo("Europe/Moscow")


def clean_text(text):
    """
    Убираем невидимые символы Telegram.
    """

    text = re.sub(
        r"[\u200b\u200c\u200d\u2060\ufeff]",
        "",
        text
    )

    return text.strip()


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
            "Не удалось получить текст поста"
        )

    return post.get_text(
        "\n"
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


    # --------------------------------
    # Чистим строки
    # --------------------------------

    lines = []

    for raw_line in text.split("\n"):

        line = clean_text(raw_line)

        if line:

            lines.append(line)


    tournaments = []


    current_day = None
    current_month = None


    # --------------------------------
    # Парсим пост построчно
    # --------------------------------

    for line in lines:

        # -----------------------------
        # Дата
        # -----------------------------

        date_match = re.match(
            r"^\*?\*?\s*(\d{1,2})\s+([а-яё]+)",
            line.lower()
        )


        if date_match:

            current_day = int(
                date_match.group(1)
            )

            month_name = (
                date_match.group(2)
                .lower()
            )


            if month_name in MONTHS:

                current_month = MONTHS[
                    month_name
                ]

            else:

                current_day = None
                current_month = None


            continue


        # Если дату ещё не нашли,
        # строку пропускаем

        if current_day is None:

            continue


        # -----------------------------
        # Время
        # -----------------------------

        time_match = re.search(
            r"(\d{1,2}:\d{2})",
            line
        )


        if not time_match:

            continue


        time = time_match.group(1)


        # -----------------------------
        # Получаем текст после времени
        # -----------------------------

        title = line[
            time_match.end():
        ].strip()


        # Убираем маркеры

        title = re.sub(
            r"^[•\-–—\s]+",
            "",
            title
        )


        title = clean_text(
            title
        )


        # -----------------------------
        # Если после времени ничего нет,
        # берём следующую строку
        # -----------------------------

        if not title:

            index = lines.index(
                line
            )


            if index + 1 < len(lines):

                next_line = lines[
                    index + 1
                ]


                # Если следующая строка
                # не новая дата и не новый турнир

                if (
                    not re.match(
                        r"^\d{1,2}\s+[а-яё]+",
                        next_line.lower()
                    )
                    and
                    not re.search(
                        r"\d{1,2}:\d{2}",
                        next_line
                    )
                ):

                    title = next_line


        # -----------------------------
        # Если название начинается
        # со слова "турнир" на следующей
        # строке — добавляем её
        # -----------------------------

        index = lines.index(
            line
        )


        if (
            index + 1 < len(lines)
            and
            "турнир" in lines[index + 1].lower()
            and
            "турнир" not in title.lower()
        ):

            title = (
                title
                + " "
                + lines[index + 1]
            )


        title = clean_text(
            title
        )


        # -----------------------------
        # Сохраняем
        # -----------------------------

        if title:

            tournaments.append({

                "day": current_day,

                "month": current_month,

                "time": time,

                "title": title

            })


    # --------------------------------
    # Удаляем дубликаты
    # --------------------------------

    unique = []

    seen = set()


    for tournament in tournaments:

        key = (
            tournament["day"],
            tournament["month"],
            tournament["time"],
            tournament["title"]
        )


        if key not in seen:

            seen.add(key)

            unique.append(
                tournament
            )


    print(
        "========== ВСЕ ТУРНИРЫ =========="
    )


    for tournament in unique:

        print(
            tournament
        )


    return unique


def today_tournaments():

    # =================================
    # ВАЖНО:
    # берём дату именно Москвы
    # =================================

    today = datetime.now(
        MOSCOW_TZ
    )


    print(
        "========== СЕГОДНЯ =========="
    )

    print(
        "Московское время:",
        today.strftime(
            "%d.%m.%Y %H:%M:%S"
        )
    )

    print(
        "Московская дата:",
        today.day,
        today.month
    )


    all_tournaments = (
        parse_tournaments()
    )


    result = []


    for tournament in all_tournaments:

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

    today_tournaments()
