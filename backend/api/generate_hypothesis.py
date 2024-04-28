from fastapi import APIRouter, HTTPException
from models.therapeutic_hypothesis import TherapeuticHypothesis
from models.drug_list import DrugList
from scraper.url_scraper import scrape_url
from supabase import create_client
from openai import AsyncOpenAI, OpenAI, RateLimitError
import os, uuid, instructor, json, asyncio

# initialize API router
router = APIRouter()

# get Supabase URL and key from environment variables and create client
supabase_url = os.environ["SUPABASE_URL"]
supabase_key = os.environ["SUPABASE_KEY"]
supabase_client = create_client(supabase_url, supabase_key)

# define endpoint to generate therapeutic hypothesis
@router.post("/generate_hypothesis/")
async def generate_hypothesis(front_data: dict):
    try:
        # extract URL from request data
        url = front_data.get("url")

        # check if data for the URL already exists in results.json
        json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../results.json")
        with open(json_file_path, 'r') as results_file:
            json_data = json.load(results_file)

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
        drug_messages = [
            {"role": "system", "content": "The following is a research paper on a novel. Do not use any outside information other than this excerpt. Find every drug described in this excerpt. If there is no information about the drug other than the name, do not include it."},
            {"role": "user", "content": unstructured_text}
        ]

        # initialize OpenAI client
        client = OpenAI(
            base_url="https://api.together.xyz/v1",
            api_key=os.environ["TOGETHER_API_KEY"],
        )
        drug_client = instructor.from_openai(client, mode=instructor.Mode.TOOLS)
        client = instructor.apatch(AsyncOpenAI(api_key=os.environ["OPENAI_KEY"]))

        # create chat completion using OpenAI client using Pydantic model for validation
        drug_response: DrugList = drug_client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            response_model=DrugList,
            messages=drug_messages,
        )

        tasks = []
        # llm_responses = {}

        # throttle to first 25 drugs seen on page to prevent overuse of OpenAI tokens
        for i in range(min(len(drug_response.drugs), 25)):
            drug = drug_response.drugs[i]

            llm_messages = [
                {"role": "system", "content": f'The following is a research paper on a novel. Do not use any outside information other than this excerpt, and if a specific field is not mentioned say "not mentioned". Given the name of the drug, {drug}, find the protein target and disease addressed by {drug} if mentioned in the excerpt. Add the short section of verbatim text that supports these claims into the citation, the speakers who are making the extracted claims, and the name of any past or upcoming clinical trials that will feature {drug}, and return a list ["not mentioned"] if these fields are not mentioned. Do not make the citation too long. Finally, include the the results (e.g., overall survival, progression-free survival) of {drug}. Be concise.'},
                {"role": "user", "content": unstructured_text}
            ]

            # create chat completion using OpenAI client using Pydantic model for validation
            tasks.append(
                client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    response_model=TherapeuticHypothesis,
                    messages=llm_messages,
                )
            )
            # llm_response: TherapeuticHypothesis = client.chat.completions.create(
            #         model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            #         response_model=TherapeuticHypothesis,
            #         messages=llm_messages,
            #     )
            
            # llm_responses[drug] = llm_response.json()

        # batch process LLM processing to generate hypotheses asynchronously
        llm_responses = await asyncio.gather(*tasks)

        # convert Pydantic models into JSONs for frontend
        llm_responses = {hypothesis.drug: json.dumps(hypothesis.dict()) for hypothesis in llm_responses}

        # generate UUID for database and URL sharing
        new_uuid = str(uuid.uuid4())

        # define data to be inserted into Supabase table
        response_data = {
            "UUID": new_uuid,
            "URL": url,
            "Content": json.dumps(llm_responses)
        }

        # insert response data into Supabase table
        response_builder = supabase_client.table("ResponseTable").insert(response_data)
        response, error = response_builder.execute()
        if error[1]:
            raise HTTPException(status_code=500, detail="Error storing response in database")

        # return the chat completion response and UUID
        return {"llm_response": json.dumps(llm_responses), "new_uuid": new_uuid}

    except RateLimitError as e:
            error_message = f"Rate limit reached: {e}"
            print(error_message)
            raise HTTPException(status_code=429, detail=error_message)