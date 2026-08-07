import re
import requests

from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo


# ==========================================
# НАШ ПОСТ
# ==========================================

POST_URL = "https://t.me/s/pingtablet/3977"


# ==========================================
# МЕСЯЦЫ
# ==========================================

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


# ==========================================
# ЧАСОВОЙ ПОЯС МОСКВЫ
# ==========================================

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


# ==========================================
# ЗАГРУЗКА ПОСТА
# ==========================================

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

    # Ищем именно сообщение с нужным ID
    post = soup.find(
        "div",
        class_="tgme_widget_message_text"
    )

    if not post:
        raise Exception(
            "Не удалось получить текст поста"
        )

    text = post.get_text(
        "\n",
        strip=True
    )

    return text


# ==========================================
# ОЧИСТКА ТЕКСТА
# ==========================================

def clean_text(text):

    # Убираем невидимые символы Telegram
    text = re.sub(
        r"[\u200b\u200c\u200d\u2060\ufeff]",
        "",
        text
    )

    # Убираем лишние пробелы
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ==========================================
# ПАРСИНГ ВСЕХ ТУРНИРОВ
# ==========================================

def parse_tournaments():

    text = load_post()

    print(
        "========== НАШ ПОСТ =========="
    )

    print(text)

    print(
        "========== КОНЕЦ =========="
    )


    lines = []

    for raw_line in text.splitlines():

        line = clean_text(raw_line)

        if line:
            lines.append(line)


    tournaments = []


    current_day = None
    current_month = None


    for line in lines:

        # ==================================
        # ИЩЕМ ДАТУ
        # Например:
        # 7 августа
        # ==================================

        date_match = re.match(
            r"^\*?\*?\s*(\d{1,2})\s+([а-яё]+)",
            line.lower()
        )


        if date_match:

            day = int(
                date_match.group(1)
            )

            month_name = (
                date_match.group(2)
                .strip()
                .lower()
            )


            if month_name in MONTHS:

                current_day = day

                current_month = (
                    MONTHS[month_name]
                )


            continue


        # Если даты ещё нет,
        # турниры не парсим

        if current_day is None:

            continue


        # ==================================
        # ИЩЕМ ВРЕМЯ
        #
        # 17:00
        # • 17:00
        # ==================================

        time_match = re.search(
            r"(?:^|[•\-\s])(\d{1,2}:\d{2})(?:\s|$)",
            line
        )


        if not time_match:

            continue


        time = time_match.group(1)


        # ==================================
        # УБИРАЕМ ВРЕМЯ И МАРКЕР •
        # ==================================

        rest = line[
            time_match.end():
        ].strip()


        # ==================================
        # ЕСЛИ НАЗВАНИЕ ПРОДОЛЖАЕТСЯ
        # НА СЛЕДУЮЩЕЙ СТРОКЕ,
        # ДОБИРАЕМ ЕГО НИЖЕ
        #
        # Например:
        #
        # • 15:00 одиночный
        # турнир
        # на фестивале круто
        #
        # ==================================

        title_parts = []


        if rest:

            title_parts.append(
                rest
            )


        # Следующие строки могут быть
        # продолжением текущего турнира

        current_index = lines.index(line)


        for next_line in lines[
            current_index + 1:
        ]:

            # Если началась новая дата —
            # прекращаем

            if re.match(
                r"^\*?\*?\s*\d{1,2}\s+[а-яё]+",
                next_line.lower()
            ):

                break


            # Если начался новый турнир —
            # прекращаем

            if re.search(
                r"\d{1,2}:\d{2}",
                next_line
            ):

                break


            # Служебные строки пропускаем

            if next_line in [
                "календарь событий:",
                "лайв",
                "лагерь",
                "чат",
                "мерч",
                "связаться",
                "посотрудничать",
                "привет,",
                "первый раз?",
                "рассказываем о нас",
            ]:

                continue


            # Добавляем продолжение

            if next_line:

                title_parts.append(
                    next_line
                )


            # Ограничиваем количество
            # строк продолжения

            if len(title_parts) >= 3:

                break


        title = " ".join(
            title_parts
        )


        title = clean_text(
            title
        )


        # ==================================
        # УБИРАЕМ СЛУЧАЙНЫЕ СИМВОЛЫ
        # ==================================

        title = title.replace(
            "‎",
            ""
        )

        title = title.replace(
            "‌",
            ""
        )


        title = clean_text(
            title
        )


        if not title:

            continue


        # ==================================
        # СОХРАНЯЕМ
        # ==================================

        tournament = {

            "day": current_day,

            "month": current_month,

            "time": time,

            "title": title

        }


        # Не допускаем дубликаты

        duplicate = False


        for existing in tournaments:

            if (
                existing["day"]
                == tournament["day"]
                and
                existing["month"]
                == tournament["month"]
                and
                existing["time"]
                == tournament["time"]
                and
                existing["title"]
                == tournament["title"]
            ):

                duplicate = True

                break


        if not duplicate:

            tournaments.append(
                tournament
            )


    print(
        "========== ВСЕ ТУРНИРЫ =========="
    )


    for tournament in tournaments:

        print(
            tournament
        )


    return tournaments


# ==========================================
# ТУРНИРЫ СЕГОДНЯ
# ==========================================

def today_tournaments():

    # ВАЖНО:
    # используем московское время,
    # а не время Railway/UTC

    today = datetime.now(
        MOSCOW_TZ
    )


    print(
        "========== СЕГОДНЯ =========="
    )

    print(
        "Москва:",
        today.strftime(
            "%d.%m.%Y %H:%M"
        )
    )


    all_tournaments = (
        parse_tournaments()
    )


    result = []


    for tournament in all_tournaments:

        if (
            tournament["day"]
            == today.day
            and
            tournament["month"]
            == today.month
        ):

            result.append(
                tournament
            )


    print(
        "Сегодняшние:",
        result
    )


    return result


# ==========================================
# ТЕСТ ПАРСЕРА
# ==========================================

if __name__ == "__main__":

    print(
        "========== TEST =========="
    )

    today_tournaments()
