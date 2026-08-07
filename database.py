import os

from supabase import create_client
from dotenv import load_dotenv


load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)



async def save_late_request(
    user_id,
    username,
    text
):

    data = {
        "user_id": user_id,
        "username": username,
        "message": text
    }


    result = (
        supabase
        .table("late_requests")
        .insert(data)
        .execute()
    )


    return result
