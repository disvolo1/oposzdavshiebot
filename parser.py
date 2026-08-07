import re
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo


POST_URL = "https://t.me/s/pingtablet/3977"

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


def clean(text):

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

    response = requests.get(
        POST_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
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
            "Пост 3977 не найден"
        )

    return post.get_text(
        "\n"
    )


def parse_tournaments():

    raw_text = load_post()

    print(
        "========== НАШ ПОСТ =========="
    )

    print(raw_text)

    print(
        "========== КОНЕЦ =========="
    )


    # ---------------------------------
    # Нормализуем текст
    # ---------------------------------

    text = raw_text

    text = re.sub(
        r"[\u200b\u200c\u200d\u2060\ufeff]",
        "",
        text
    )

    text = text.replace(
        "\xa0",
        " "
    )


    # ---------------------------------
    # Ищем ВСЕ даты
    #
    # 7 августа
    # 8 августа
    # 9 августа
    # ---------------------------------

    date_pattern = re.compile(
        r"(?<!\d)"
        r"(\d{1,2})"
        r"\s+"
        r"(января|февраля|марта|апреля|мая|июня|"
        r"июля|августа|сентября|октября|ноября|декабря)"
        r"(?![а-яё])",
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


    # ---------------------------------
    # Каждый блок между датами
    # ---------------------------------

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


        print(
            f"========== БЛОК {day} {month_name} =========="
        )

        print(block)


        # ---------------------------------
        # Ищем время
        # ---------------------------------

        times = list(
            re.finditer(
                r"(?<!\d)(\d{1,2}:\d{2})(?!\d)",
                block
            )
        )


        for j, time_match in enumerate(times):

            time = time_match.group(1)


            description_start = (
                time_match.end()
            )


            if j + 1 < len(times):

                description_end = (
                    times[j + 1].start()
                )

            else:

                description_end = len(block)


            description = block[
                description_start:
                description_end
            ]


            description = clean(
                description
            )


            # Убираем маркеры

            description = re.sub(
                r"^[•\-–—]+",
                "",
                description
            )

            description = clean(
                description
            )


            # ---------------------------------
            # Иногда Telegram переносит:
            #
            # • 15:00 одиночный
            # турнир
            # на фестивале круто
            #
            # В итоге description уже содержит
            # весь кусок.
            # ---------------------------------


            if not description:

                continue


            # ---------------------------------
            # Убираем служебный мусор
            # ---------------------------------

            bad = [
                "календарь событий",
                "лайв",
                "лагерь",
                "чат",
                "мерч",
                "связаться",
                "посотрудничать",
            ]


            if description.lower() in bad:

                continue


            # ---------------------------------
            # Сохраняем
            # ---------------------------------

            tournament = {
                "day": day,
                "month": month,
                "time": time,
                "title": description
            }


            tournaments.append(
                tournament
            )


    # ---------------------------------
    # Дубликаты
    # ---------------------------------

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

    # =================================
    # БЕРЁМ ВРЕМЯ МОСКВЫ
    # =================================

    now = datetime.now(
        MOSCOW_TZ
    )


    today_day = now.day
    today_month = now.month


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
        today_day,
        today_month
    )


    all_tournaments = (
        parse_tournaments()
    )


    today = []


    for tournament in all_tournaments:

        if (
            tournament["day"] == today_day
            and
            tournament["month"] == today_month
        ):

            today.append(
                tournament
            )


    print(
        "СЕГОДНЯШНИЕ:",
        today
    )


    return today


if __name__ == "__main__":

    today_tournaments()
