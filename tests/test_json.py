import os, json
from google import genai
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class CandidateAnalysis(BaseModel):
    candidate_name: str
    overall_score: int
    strenghts: list[str]
    gaps: list[str]
    recomendation: str 

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Analyze this resume: [resume text] for this JD: [JD text]",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=CandidateAnalysis
    )
)

result = json.loads(response.text)
print(result)
