from fastapi import APIRouter, HTTPException, Path
from typing import List
from models.therapeutic_hypothesis import TherapeuticHypothesis
from scraper.url_scraper import scrape_url
from supabase import create_client
import openai
import os
import uuid
import instructor
import json

# initialize API router
router = APIRouter()

# get Supabase URL and key from environment variables and create client
supabase_url = os.environ["SUPABASE_URL"]
supabase_key = os.environ["SUPABASE_KEY"]
supabase_client = create_client(supabase_url, supabase_key)

# define endpoint to generate therapeutic hypothesis
@router.post("/generate_hypothesis/")
async def generate_hypothesis(front_data: dict):

    # extract URL from request data
    url = front_data.get("url")
    with open('results.json', 'r') as results_file:
        json_data = json.load(results_file)
    
    # check if data for the URL already exists in results.json
    for item in json_data:
        if item["url"] == url:
            unstructured_text = item["text"]
            break
    else: # if data doesn't exist, scrape the URL
        new_data = await scrape_url(url)
        json_data.append(new_data)

        # write updated data to results.json for future parsing
        with open("results.json", "w") as json_file:
            json.dump(json_data, json_file, indent=2)
        unstructured_text = new_data["text"]
    
    # define messages for OpenAI LLM chat completion
    llm_messages = [
        {"role": "system", "content": "The following is a research paper on a novel. Do not use any outside information other than this excerpt, and if a specific field is not mentioned say \"not mentioned\". Find the name of the drug given in this excerpt and the protein target and disease addressed by the drug if mentioned in the excerpt. Add the verbatim text that supports these claims into the citation, the speakers who are making the extracted claims, and the name of any past or upcoming clinical trials that will feature this drug. Finally, include the the results (e.g., overall survival, progression-free survival) of the drug and be concise."},
        {"role": "user", "content": unstructured_text}
    ]

    # initialize OpenAI client
    client = openai.OpenAI(
        base_url="https://api.together.xyz/v1",
        api_key=os.environ["TOGETHER_API_KEY"],
    )
    client = instructor.from_openai(client, mode=instructor.Mode.TOOLS)

    # create chat completion using OpenAI client using Pydantic model for validation
    llm_response: TherapeuticHypothesis = client.chat.completions.create(
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        response_model=TherapeuticHypothesis,
        messages=llm_messages,
    )

    # generate UUID for database and URL sharing
    new_uuid = str(uuid.uuid4())

    # define data to be inserted into Supabase table
    response_data = {
        "UUID": new_uuid,
        "URL": url,
        "Content": llm_response.json()
    }

    # insert response data into Supabase table
    response_builder = supabase_client.table("ResponseTable").insert(response_data)
    response, error = response_builder.execute()
    if error[1]:
        raise HTTPException(status_code=500, detail="Error storing response in database")

    # return the chat completion response and UUID
    return {"llm_response": llm_response, "new_uuid": new_uuid}