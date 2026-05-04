from google import genai
from google.genai import types
from dotenv import load_dotenv

# This reads the .env file and loads variables into the environment
load_dotenv()

# Now the client picks up GEMINI_API_KEY automatically
client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Here is a job description for Senior Python Developer at Irembo...",
    config=types.GenerateContentConfig(
        system_instruction="""You are an expert technical recruiter at Irembo...""",
        temperature=0.0
    )
)

print(response.text)