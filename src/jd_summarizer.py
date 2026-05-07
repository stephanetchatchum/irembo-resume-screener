from google import genai
from google.genai import types
from dotenv import load_dotenv
import json, os

load_dotenv()
client = genai.Client()

jd_text = """
Senior Backend Engineer - Irembo

Irembo is Rwanda's leading e-government platform. We're looking for 
a Senior Backend Engineer to design and build APIs powering Rwanda's 
digital government.

Requirements:
- 3+ years Python (Django or Flask)
- PostgreSQL and database design
- RESTful API development
- Cloud infrastructure (AWS preferred)
- CI/CD and DevOps practices

Nice to have:
- GovTech experience
- Docker and Kubernetes
- Data privacy knowledge
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"""Analyze this job description and extract the key information.

<job_description>
{jd_text}
</job_description>

Return a JSON object with these fields:
- job_title
- seniority_level (junior/mid/senior/lead)
- summary (2-3 sentences)
- must_have (list of required skills)
- nice_to_have (list of preferred skills)""",
    config=types.GenerateContentConfig(
        system_instruction="You are an HR analytics expert. Be precise.",
        response_mime_type="application/json",
        temperature=0.0
    )
)

result = json.loads(response.text)

print("Title:", result.get("job_title"))
print("Level:", result.get("seniority_level"))
print("Summary:", result.get("summary"))
print("\nRequired skills:")
for skill in result.get("must_have", []):
    print(f" -{skill}")

for skill in result.get("nice_to_have", []):
    print(f" -{skill}")

os.makedirs("output", exist_ok=True)
with open("output/jd_summary.json", "w") as f:
    json.dump(result, f, indent=2)

print("\n✅ Summary saved to output/jd_summary.json")