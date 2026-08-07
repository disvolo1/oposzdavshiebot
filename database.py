from supabase import create_client, Client

from config import SUPABASE_URL, SUPABASE_KEY


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
