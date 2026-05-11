from groq import Groq
from pypdf import PdfReader
import json
import os
import time
import io
from dotenv import load_dotenv

load_dotenv()
client = Groq()

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

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract plain text from a PDF file.

    Args:
        pdf_bytes: the raw content of the PDF file
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def analyze_resume(pdf_bytes: bytes, filename: str) -> dict:
    """
    Analyze a single resume PDF against the job description.

    Args:
        pdf_bytes: the raw content of the PDF file
        filename: the name of the file, e.g. 'john_doe.pdf'
    """
    print(f" Analyzing {filename}...")

    resume_text = extract_text_from_pdf(pdf_bytes)

    if not resume_text.strip():
        print(f" WARNING: Could not extract text from {filename}")
        return {}
    


    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
         messages=[
            {
                "role": "system",
                "content": """You are an expert recruiter at Irembo.
                                Analyze objectively.
                                Never judge by name, gender, age, or school.
                                Look for hidden gems — transferable skills beyond keywords.
                                Always respond with valid JSON only, no extra text."""
            },
            {
                "role": "user",
                "content":f"""Analyze this resume against the job description below.

                <job_description>
                {JD}
                </job_description>

                <resume>
                {resume_text}
                </resume>

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
            }
            
        ],
        temperature=0.0,
        response_format={"type": "json_object"}
    )

    result = json.loads(response.choices[0].message.content)
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
            time.sleep(5)
        except Exception as e:
            print(f" ERROR processing {filename}: {e}")

    candidates.sort(key=lambda x: x.get("overall_score", 0), reverse=True)

    return candidates

def print_rankings(candidates: list):
    """Print a clean ranking report to the terminal."""

    print("\n" + "=" * 60)
    print("CANDIDATE RANKING")
    print("=" * 60)

    for rank, c in enumerate(candidates, 1):
        print(f"\n#{rank}. {c.get('candidate_name', 'Unknown')}")
        print(f"   Score:          {c.get('overall_score', '?')}/10")
        print(f"   Recommendation: {c.get('recommendation', '?').upper()}")
        print(f"   Experience:     {c.get('experience_years', '?')} years")
        print(f"   Summary:        {c.get('summary', '')}")

        if c.get("hidden_gems"):
            print(f"   Hidden Gems:    {', '.join(c['hidden_gems'])}")
        
        if c.get("matched_skills"):
            print(f"   Matched Skills: {', '.join(c['matched_skills'])}")
        
        if c.get("missing_skills"):
            print(f"   Missing Skills: {', '.join(c['missing_skills'])}")

if __name__ == "__main__":
    resume_dir = "data/sample_resumes"

    print("=== Irembo Resume Screener ===\n")

    candidates = screen_all_resumes(resume_dir)

    if not candidates:
        print("No candidates to rank")
    else:
        print_rankings(candidates)

        os.makedirs("output", exist_ok=True)
        with open("output/screening_results.json", "w") as f:
            json.dump(candidates, f, indent=2)

        print(f"\n{'='*60}")
        print(f"✅ Results saved to output/screening_results.json")
        print(f"Total candidates screened: {len(candidates)}")