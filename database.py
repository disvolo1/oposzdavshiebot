import os

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()


SUPABASE_URL = os.getenv(
    "SUPABASE_URL"
)

SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY"
)


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)



# сохраняем заявку игрока

async def save_late_request(
    user_id,
    username,
    tournament
):

    data = {
        "user_id": user_id,
        "username": username,
        "tournament": tournament
    }


    supabase.table(
        "late_requests"
    ).insert(
        data
    ).execute()



# получаем всех опоздавших на турнир

async def get_late_users(
    tournament
):

    response = (
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


    for row in response.data:

        users.append(
            row["username"]
        )


    return users



# получаем id сообщения админа

async def get_admin_message(
    tournament
):

    response = (
        supabase
        .table("late_requests")
        .select("admin_message_id")
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


    if response.data:

        return response.data[0][
            "admin_message_id"
        ]


    return None



# сохраняем id сообщения админа

async def save_admin_message(
    tournament,
    message_id
):

    (
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
