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


def clean_text(text):
    """
    Убираем невидимые символы Telegram
    и лишние пробелы.
    """

    text = re.sub(
        r"[\u200b\u200c\u200d\u2060\ufeff]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
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
        "\n",
        strip=True
    )


def parse_tournaments():

    raw_text = load_post()

    print("========== НАШ ПОСТ ==========")
    print(raw_text)
    print("========== КОНЕЦ ==========")


    # ----------------------------------
    # Нормализуем переносы
    # ----------------------------------

    text = raw_text

    text = re.sub(
        r"[\u200b\u200c\u200d\u2060\ufeff]",
        "",
        text
    )


    # ----------------------------------
    # Удаляем служебные строки
    # ----------------------------------

    text = re.sub(
        r"(?im)^.*календарь событий:.*$",
        "",
        text
    )


    # ----------------------------------
    # Находим даты
    #
    # 7 августа
    # 8 августа
    # 9 августа
    # ----------------------------------

    date_pattern = re.compile(
        r"(?<!\d)(\d{1,2})\s+"
        r"(января|февраля|марта|апреля|мая|июня|"
        r"июля|августа|сентября|октября|ноября|декабря)"
        r"(?![а-яё])",
        re.IGNORECASE
    )


    dates = list(
        date_pattern.finditer(text)
    )


    tournaments = []


    # ----------------------------------
    # Обрабатываем каждый блок даты
    # ----------------------------------

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

        if not month:
            continue


        # Начало блока

        block_start = (
            date_match.end()
        )


        # Конец блока —
        # следующая дата

        if i + 1 < len(dates):

            block_end = (
                dates[i + 1].start()
            )

        else:

            block_end = len(text)


        block = text[
            block_start:block_end
        ]


        print(
            f"========== БЛОК {day} {month_name} =========="
        )

        print(block)


        # ----------------------------------
        # Разбираем турниры
        #
        # Ищем время:
        #
        # 17:00
        # • 17:00
        # ----------------------------------

        time_matches = list(
            re.finditer(
                r"(?<!\d)(\d{1,2}:\d{2})(?!\d)",
                block
            )
        )


        for j, time_match in enumerate(
            time_matches
        ):

            time = time_match.group(1)


            # Начало описания

            start = time_match.end()


            # До следующего времени

            if j + 1 < len(time_matches):

                end = (
                    time_matches[j + 1].start()
                )

            else:

                end = len(block)


            description = block[
                start:end
            ]


            description = clean_text(
                description
            )


            # ----------------------------------
            # Убираем мусор
            # ----------------------------------

            description = re.sub(
                r"^[•\-–—\s]+",
                "",
                description
            )


            description = clean_text(
                description
            )


            # ----------------------------------
            # Иногда перед названием
            # находится лишняя точка/маркер
            # ----------------------------------

            description = description.strip(
                "•-–—: "
            )


            description = clean_text(
                description
            )


            if not description:
                continue


            # ----------------------------------
            # Пропускаем служебный мусор
            # ----------------------------------

            if description.lower() in [
                "календарь событий",
                "лайв",
                "лагерь",
                "чат",
                "мерч",
                "связаться",
                "посотрудничать",
            ]:

                continue


            tournament = {
                "day": day,
                "month": month,
                "time": time,
                "title": description
            }


            tournaments.append(
                tournament
            )


    # ----------------------------------
    # Удаляем дубликаты
    # ----------------------------------

    unique = []

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

    # ==================================
    # ВАЖНО:
    # ВСЕГДА МОСКОВСКОЕ ВРЕМЯ
    # ==================================

    now = datetime.now(
        MOSCOW_TZ
    )


    print(
        "========== СЕГОДНЯ =========="
    )

    print(
        "Москва:",
        now.strftime(
            "%d.%m.%Y %H:%M"
        )
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
        "Сегодняшние:",
        result
    )


    return result


if __name__ == "__main__":

    today_tournaments()
