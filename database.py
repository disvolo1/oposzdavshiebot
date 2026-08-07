import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


print("SUPABASE URL:", SUPABASE_URL)

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


async def save_late_requests(user_id, username, text):

    data = {
        "user_id": user_id,
        "username": username,
        "text": text
    }

    print("SENDING:", data)

    response = (
        supabase
        .table("late_requests")
        .insert(data)
        .execute()
    )

    print("SUPABASE RESPONSE:", response)

    return response
