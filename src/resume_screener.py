# ============================================================
# Irembo Resume Screener
# Reads PDF resumes, analyzes them against a job description,
# and ranks candidates using AI (Groq/LLaMA)
# ============================================================

# --- External libraries we need ---
from groq import Groq          # AI model provider (free)
from pypdf import PdfReader    # Extracts text from PDF files
import json                    # For parsing AI responses
import os                      # For file and folder operations
import time                    # For adding delays between API calls
import io                      # For reading PDF bytes as a file object
from dotenv import load_dotenv # For loading API keys from .env file

# --- Load API key from .env and connect to Groq ---
load_dotenv()
client = Groq()


# ============================================================
# FUNCTION 1: Load the job description from a text file
# ============================================================
def load_job_description(filepath: str) -> str:
    """
    Load a job description from a text file.

    Args:
        filepath: path to the .txt file containing the job description
    """
    # If the file doesn't exist, tell the user and stop the program
    if not os.path.exists(filepath):
        print(f"ERROR: Job description file not found at {filepath}")
        print("Please create data/job_description.txt with your job description.")
        exit()
    
    # Open the file and return its content as a string
    with open(filepath, "r") as f:
        return f.read()


# ============================================================
# FUNCTION 2: Extract plain text from a PDF file
# ============================================================
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract plain text from a PDF file.

    Args:
        pdf_bytes: the raw content of the PDF file
    """
    # PdfReader needs a file-like object, not raw bytes
    # io.BytesIO converts bytes into something PdfReader can read
    reader = PdfReader(io.BytesIO(pdf_bytes))
    
    text = ""
    # Loop through every page and extract the text
    for page in reader.pages:
        text += page.extract_text() or ""  # "or ''" handles pages with no text
    
    return text


# ============================================================
# FUNCTION 3: Analyze ONE resume against the job description
# ============================================================
def analyze_resume(pdf_bytes: bytes, filename: str, jd: str) -> dict:
    """
    Analyze a single resume PDF against the job description.

    Args:
        pdf_bytes: the raw content of the PDF file
        filename: the name of the file, e.g. 'john_doe.pdf'
        jd: the job description text to screen against
    """
    print(f"  Analyzing {filename}...")

    # Step 1: Extract text from the PDF
    resume_text = extract_text_from_pdf(pdf_bytes)

    # Step 2: If no text was extracted, skip this file
    if not resume_text.strip():
        print(f"  WARNING: Could not extract text from {filename}")
        return {}
    
    # Step 3: Send the resume + JD to Groq and ask for analysis
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                # System message: sets the AI's role and behavior
                "role": "system",
                "content": """You are an expert recruiter at Irembo.
Analyze objectively.
Never judge by name, gender, age, or school.
Look for hidden gems — transferable skills beyond keywords.
Always respond with valid JSON only, no extra text."""
            },
            {
                # User message: the actual task with the JD and resume
                "role": "user",
                "content": f"""Analyze this resume against the job description below.

<job_description>
{jd}
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
        temperature=0.0,                          # 0.0 = consistent, no randomness
        response_format={"type": "json_object"}   # Force JSON response
    )

    # Step 4: Parse the JSON response into a Python dictionary
    result = json.loads(response.choices[0].message.content)
    
    # Step 5: Add the filename so we know which file this came from
    result["source_file"] = filename
    
    return result


# ============================================================
# FUNCTION 4: Screen ALL resumes in a folder
# ============================================================
def screen_all_resumes(resume_dir: str, jd: str) -> list:
    """
    Screen all PDF resumes in a directory.

    Args:
        resume_dir: path to the folder containing resume PDFs
        jd: the job description text to screen against
    """
    candidates = []
    
    # Get a list of all PDF files in the folder
    pdf_files = [f for f in os.listdir(resume_dir) if f.endswith(".pdf")]

    # If no PDFs found, stop early
    if not pdf_files:
        print(f"No PDF files found in {resume_dir}")
        return []
    
    print(f"Found {len(pdf_files)} resumes to screen...\n")

    # Loop through each PDF and analyze it
    for filename in pdf_files:
        filepath = os.path.join(resume_dir, filename)  # Full path to file
        try:
            # Read the PDF as raw bytes
            with open(filepath, "rb") as f:
                pdf_bytes = f.read()
            
            # Analyze this resume
            result = analyze_resume(pdf_bytes, filename, jd)
            candidates.append(result)
            
            # Wait 5 seconds before next request to avoid hitting API limits
            time.sleep(5)
            
        except Exception as e:
            # If something goes wrong with one file, skip it and continue
            print(f"  ERROR processing {filename}: {e}")

    # Sort candidates by score, highest first
    candidates.sort(key=lambda x: x.get("overall_score", 0), reverse=True)

    return candidates


# ============================================================
# FUNCTION 5: Print a clean ranking report to the terminal
# ============================================================
def print_rankings(candidates: list):
    """Print a clean ranking report to the terminal."""

    print("\n" + "=" * 60)
    print("CANDIDATE RANKINGS")
    print("=" * 60)

    # enumerate(candidates, 1) gives us rank 1, 2, 3... automatically
    for rank, c in enumerate(candidates, 1):
        print(f"\n#{rank}. {c.get('candidate_name', 'Unknown')}")
        print(f"   Score:          {c.get('overall_score', '?')}/10")
        print(f"   Recommendation: {c.get('recommendation', '?').upper()}")
        print(f"   Experience:     {c.get('experience_years', '?')} years")
        print(f"   Summary:        {c.get('summary', '')}")

        # Only print these sections if they have data
        if c.get("hidden_gems"):
            print(f"   Hidden Gems:    {', '.join(c['hidden_gems'])}")
        
        if c.get("matched_skills"):
            print(f"   Matched Skills: {', '.join(c['matched_skills'])}")
        
        if c.get("missing_skills"):
            print(f"   Missing Skills: {', '.join(c['missing_skills'])}")


# ============================================================
# MAIN — This runs when you execute the script directly
# ============================================================
if __name__ == "__main__":

    # Load the job description from file
    JD = load_job_description("data/job_description.txt")
    
    resume_dir = "data/sample_resumes"

    print("=== Irembo Resume Screener ===\n")
    print("Job description loaded ✅\n")
    
    # Screen all resumes and get ranked results
    candidates = screen_all_resumes(resume_dir, JD)

    if not candidates:
        print("No candidates to rank")
    else:
        # Print rankings to terminal
        print_rankings(candidates)

        # Save full results to JSON file
        os.makedirs("output", exist_ok=True)
        with open("output/screening_results.json", "w") as f:
            json.dump(candidates, f, indent=2)

        print(f"\n{'='*60}")
        print(f"✅ Results saved to output/screening_results.json")
        print(f"Total candidates screened: {len(candidates)}")