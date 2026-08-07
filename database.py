import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

print("SUPABASE URL:", SUPABASE_URL)

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


async def save_late_request(user_id, username, text):

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

    print("RESULT:", result)

    return result
