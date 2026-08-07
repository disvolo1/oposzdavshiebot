import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(url, key)


async def save_late_requests(
    user_id: int,
    username: str,
    text: str
):
    data = {
        "user_id": user_id,
        "username": username,
        "message": text
    }

    supabase.table("late_requests").insert(data).execute()
