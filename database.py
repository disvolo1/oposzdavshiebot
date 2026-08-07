import os

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception(
        "Нет SUPABASE_URL или SUPABASE_KEY в .env"
    )


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)



# =====================================================
# СОХРАНЕНИЕ ОПАЗДАВШЕГО
# =====================================================

async def save_late_request(
    user_id,
    username,
    tournament
):

    print(
        "ПЫТАЮСЬ СОХРАНИТЬ:",
        user_id,
        username,
        tournament
    )


    data = {

        "user_id": user_id,

        "username": username,

        "tournament": tournament

    }


    try:

        result = (
            supabase
            .table("late_requests")
            .insert(data)
            .execute()
        )


        print(
            "SUPABASE СОХРАНИЛ:",
            result.data
        )


        return result.data


    except Exception as e:

        print(
            "ОШИБКА SUPABASE SAVE:",
            e
        )

        raise e



# =====================================================
# ПОЛУЧИТЬ ВСЕХ ОПАЗДАВШИХ НА ТУРНИР
# =====================================================

async def get_late_users(
    tournament
):

    print(
        "ИЩУ УЧАСТНИКОВ:",
        tournament
    )


    try:

        result = (
            supabase
            .table("late_requests")
            .select("username")
            .eq(
                "tournament",
                tournament
            )
            .execute()
        )


        users = []


        for row in result.data:

            users.append(
                row["username"]
            )


        print(
            "НАЙДЕНЫ:",
            users
        )


        return users


    except Exception as e:

        print(
            "ОШИБКА SUPABASE GET USERS:",
            e
        )

        raise e



# =====================================================
# ПОЛУЧИТЬ ID СООБЩЕНИЯ АДМИНА
# =====================================================

async def get_admin_message(
    tournament
):

    print(
        "ИЩУ MESSAGE ID:",
        tournament
    )


    try:

        result = (
            supabase
            .table("late_requests")
            .select(
                "admin_message_id"
            )
            .eq(
                "tournament",
                tournament
            )
            .not_.is_(
                "admin_message_id",
                "null"
            )
            .limit(1)
            .execute()
        )


        if result.data:

            message_id = result.data[0][
                "admin_message_id"
            ]


            print(
                "MESSAGE ID:",
                message_id
            )


            return message_id



        return None



    except Exception as e:

        print(
            "ОШИБКА SUPABASE MESSAGE:",
            e
        )

        raise e



# =====================================================
# СОХРАНИТЬ ID СООБЩЕНИЯ АДМИНА
# =====================================================

async def save_admin_message(
    tournament,
    message_id
):

    print(
        "СОХРАНЯЮ MESSAGE ID:",
        tournament,
        message_id
    )


    try:

        result = (
            supabase
            .table("late_requests")
            .update(
                {
                    "admin_message_id": message_id
                }
            )
            .eq(
                "tournament",
                tournament
            )
            .execute()
        )


        print(
            "MESSAGE ID СОХРАНЕН:",
            result.data
        )


        return result.data


    except Exception as e:

        print(
            "ОШИБКА UPDATE MESSAGE:",
            e
        )

        raise e
