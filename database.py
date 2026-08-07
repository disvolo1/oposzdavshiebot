import os

from supabase import create_client, Client


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


async def save_late_request(
    user_id: int,
    username: str,
    message: str
):
    data = {
        "user_id": user_id,
        "username": username,
        "message": message
    }

    response = (
        supabase
        .table("late_requests")
        .insert(data)
        .execute()
    )

    return response
