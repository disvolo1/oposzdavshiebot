import os

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception(
        "Нет SUPABASE_URL или SUPABASE_KEY"
    )


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)



# =====================================
# СОХРАНИТЬ ОПАЗДАВШЕГО
# =====================================

async def save_late_request(
    user_id,
    username,
    tournament
):

    print(
        "СОХРАНЕНИЕ:",
        user_id,
        username,
        tournament
    )


    data = {
        "user_id": user_id,
        "username": username,
        "tournament": tournament
    }


    result = (
        supabase
        .table("late_requests")
        .insert(data)
        .execute()
    )


    print(
        "СОХРАНЕНО:",
        result.data
    )


    return result.data



# =====================================
# ПОЛУЧИТЬ УЧАСТНИКОВ ТУРНИРА
# =====================================

async def get_late_users(
    tournament
):

    result = (
        supabase
        .table("late_requests")
        .select(
            "username, user_id"
        )
        .eq(
            "tournament",
            tournament
        )
        .execute()
    )


    users = []


    for row in result.data:

        users.append(
            {
                "username": row["username"],
                "user_id": row["user_id"]
            }
        )


    print(
        "УЧАСТНИКИ:",
        users
    )


    return users



# =====================================
# НАЙТИ СООБЩЕНИЕ АДМИНА
# =====================================

async def get_admin_message(
    tournament
):

    result = (
        supabase
        .table("late_admin_messages")
        .select(
            "message_id"
        )
        .eq(
            "tournament",
            tournament
        )
        .execute()
    )


    if result.data:

        return result.data[0][
            "message_id"
        ]


    return None



# =====================================
# СОХРАНИТЬ СООБЩЕНИЕ АДМИНА
# =====================================

async def save_admin_message(
    tournament,
    message_id
):

    result = (
        supabase
        .table("late_admin_messages")
        .insert(
            {
                "tournament": tournament,
                "message_id": message_id
            }
        )
        .execute()
    )


    print(
        "ADMIN MESSAGE SAVED:",
        result.data
    )


    return result.data
