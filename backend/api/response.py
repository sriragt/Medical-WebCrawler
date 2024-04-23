from fastapi import APIRouter, HTTPException, Path
from supabase import create_client
import os
import json

router = APIRouter()

supabase_url = os.environ["SUPABASE_URL"]
supabase_key = os.environ["SUPABASE_KEY"]
supabase_client = create_client(supabase_url, supabase_key)

@router.get("/response/{uuid}")
async def get_response_by_uuid(uuid: str = Path(...)):
    response, error = supabase_client.table("ResponseTable").select("Content").eq("UUID", uuid).execute()
    if error[1]:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    if response[1] == []:
        raise HTTPException(status_code=404, detail="404 Not Found")
    
    return json.loads(response[1][0]["Content"])