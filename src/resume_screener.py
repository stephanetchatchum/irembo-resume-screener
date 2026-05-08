from google import genai
from google.genai import types
import json
import os
from dotenv import load_dotenv


load_dotenv()
client = genai.Client()

JD = """
Senior Backend Engineer - Irembo

Requirements:
- 3+ years Python (Django or Flask)
- PostgreSQL and database design
- RESTful API development
- Cloud infrastructure (AWS preferred)
- CI/CD and DevOps practices

Nice to have:
- GovTech experience
- Docker and Kubernetes
"""

def analyze_resume(pdf_bytes: bytes, filename: str) -> dict:
    """
    Analyze a single resume PDF against the job description.

    Args:
        pdf_bytes: the raw content of the PDF file
        filename: the name of the file, e.g. 'john_doe.pdf'
    """
    print(f" Analyzing {filename}...")

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
            f"""Analyze this resume against the job description below.

            <job_description>
            {JD}
            </job_description>

            Return a JSON object with:
            - candidate_name
            - experience_years
            - overall_score (1 to 10)
            - matched_skills (list)
            - missing_skills (list)
            - strengths (list of top 3)
            - hidden_gems (list)
            - summary (2-3 sentences)
            - recommendation: advance, hold, or reject"""
        ],
        config=types.GenerateContentConfig(
            system_instruction="""You are an expert recruiter at Irembo. 
            Analyze objectively. 
            Never judge by name, gender, age, or school. 
            Look for hidden gems — transferable skills beyond keywords.
            """,
            response_mime_type="application/json",
            temperature = 0.0
        )
    )

    result = json.loads(response.text)
    result["source_file"] = filename
    return result

def screen_all_resumes(resume_dir: str) -> list:
    """
    Screen all PDF resumes in a directory.

    Args:
        resume_dir: path to the folder containing resume PDFs
    """

    candidates = []
    pdf_files = [f for f in os.listdir(resume_dir) if f.endswith(".pdf")]

    if not pdf_files:
        print(f"No PDF file found in {resume_dir}")
        return []
    
    print(f"Found {len(pdf_files)} resumes to screen...\n")

    for filename in pdf_files:
        filepath = os.path.join(resume_dir, filename)
        try:
            with open(filepath, "rb") as f:
                pdf_bytes = f.read()
            result = analyze_resume(pdf_bytes, filename)
            candidates.append(result)
        except Exception as e:
            print(f" ERROR processing {filename}: {e}")

    candidates.sort(key=lambda x: x.get("overall_score", 0), reverse=True)

    return candidates