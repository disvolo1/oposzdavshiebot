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


def get_player(player_id: int):
    """
    Получить игрока по Telegram ID
    """

    response = (
        supabase
        .table("players")
        .select("*")
        .eq("telegram_id", player_id)
        .execute()
    )

    return response.data


def set_player_late(
    player_id: int,
    reason: str
):
    """
    Отметить игрока как опоздавшего
    """

    response = (
        supabase
        .table("players")
        .update(
            {
                "is_late": True,
                "late_reason": reason
            }
        )
        .eq(
            "telegram_id",
            player_id
        )
        .execute()
    )

    return response.data


def get_active_tournament():
    """
    Получить текущий активный турнир
    """

    response = (
        supabase
        .table("tournaments")
        .select("*")
        .eq(
            "status",
            "active"
        )
        .limit(1)
        .execute()
    )

    return response.data


def add_late_request(
    telegram_id: int,
    username: str,
    message: str
):
    """
    Сохранить заявку об опоздании
    """

    response = (
        supabase
        .table("late_requests")
        .insert(
            {
                "telegram_id": telegram_id,
                "username": username,
                "message": message
            }
        )
        .execute()
    )

    return response.data
