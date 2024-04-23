from fastapi import APIRouter, HTTPException, Path
from supabase import create_client
import os
import json

# initialize API router
router = APIRouter()

# get Supabase URL and key from environment variables and create client
supabase_url = os.environ["SUPABASE_URL"]
supabase_key = os.environ["SUPABASE_KEY"]
supabase_client = create_client(supabase_url, supabase_key)

# define endpoint to retrieve response by UUID
@router.get("/response/{uuid}")
async def get_response_by_uuid(uuid: str = Path(...)):

    # query Supabase table for content based on UUID
    response, error = supabase_client.table("ResponseTable").select("Content").eq("UUID", uuid).execute()

    # check for errors in the response
    if error[1]:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    # if no corresponding data for UUID is found, raise 404 error
    if response[1] == []:
        raise HTTPException(status_code=404, detail="404 Not Found")
    
    # if no errors, parse JSON content from response and return
    return json.loads(response[1][0]["Content"])