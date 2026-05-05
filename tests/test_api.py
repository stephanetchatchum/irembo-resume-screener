import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize client with explicit API key
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# Encapsulated in a class to avoid global mutable state
class ResumeScreener:
    def __init__(self):
        self.history = []

    def chat(self, user_message):
        self.history.append(
            types.Content(role="user", parts=[types.Part.from_text(user_message)])
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=self.history,
            config=types.GenerateContentConfig(
                system_instruction="You are a resume screening assistant."
            )
        )

        # Guard against blocked or empty responses
        if not response.candidates:
            return "Response was blocked or empty."

        self.history.append(response.candidates[0].content)
        return response.text


# --- Replace these with your actual content ---
jd_text = """
Senior Python Developer — 5+ years Python, FastAPI, AWS experience required.
Strong knowledge of REST APIs, PostgreSQL, and CI/CD pipelines.
"""

resume_text = """
John Doe — 6 years Python experience. Built REST APIs with FastAPI and Flask.
Deployed services on AWS (EC2, Lambda). Familiar with PostgreSQL and GitHub Actions.
"""
# ----------------------------------------------

screener = ResumeScreener()

# First turn — send the job description
print(screener.chat(f"Here is a job description for Senior Python Developer: {jd_text}"))

# Second turn — model remembers the JD from history
print(screener.chat(f"Now analyze this resume against the JD: {resume_text}"))

# Third turn
print(screener.chat("What are this candidate's three biggest strengths for this role?"))