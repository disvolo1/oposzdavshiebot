import re
import requests

from bs4 import BeautifulSoup


POST_URL = "https://t.me/s/pingtablet/3977"


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
        raise Exception("Пост не найден")


    text = post.get_text("\n")


    print("========== ТЕКСТ ПОСТА ==========")
    print(text)
    print("========== КОНЕЦ ==========")


    return text



def parse_tournaments():

    text = load_post()


    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]


    print("========== СТРОКИ ==========")

    for line in lines:
        print(repr(line))

    print("========== КОНЕЦ СТРОК ==========")


    return []



if __name__ == "__main__":

    parse_tournaments()
