import os
from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


def save_late_request(
    telegram_id: int,
    username: str,
    name: str,
    message: str
):
    """
    Сохраняем заявку об опоздании
    """

    data = {
        "telegram_id": telegram_id,
        "username": username,
        "name": name,
        "message": message
    }

    response = (
        supabase
        .table("late_requests")
        .insert(data)
        .execute()
    )

    return response.data


def get_active_tournament():
    """
    Получаем текущий турнир
    """

    response = (
        supabase
        .table("tournaments")
        .select("*")
        .eq("status", "active")
        .limit(1)
        .execute()
    )

    return response.data
