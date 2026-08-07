import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("SUPABASE URL:", SUPABASE_URL)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Нет SUPABASE_URL или SUPABASE_KEY в переменных окружения")


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


async def save_late_request(user_id: int, username: str, text: str):

    data = {
        "user_id": user_id,
        "username": username,
        "text": text
    }

    print("SENDING:", data)

    result = (
        supabase
        .table("late_requests")
        .insert(data)
        .execute()
    )

    print("SUPABASE RESPONSE:", result)

    return result
