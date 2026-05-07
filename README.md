# Irembo Resume Screener

An intelligent resume screening and ranking system that uses AI to automatically analyze job descriptions and match them with candidate resumes. Built for Irembo's e-government platform hiring process.

## Features

- **Job Description Analysis**: Automatically extract key requirements from job descriptions using Google Gemini AI
- **Resume Parsing**: Parse and extract relevant information from resumes
- **Intelligent Ranking**: Score and rank resumes based on job description match using machine learning
- **Gmail Integration**: Fetch resumes and communicate results directly via email
- **API Client**: RESTful API interface for integration with external systems
- **JSON Output**: Export job summaries and rankings in structured JSON format

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- Gmail credentials (for email integration)
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd irembo-resume-screener
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   Create a `.env` file in the project root with:
   ```
   GOOGLE_API_KEY=your_google_gemini_api_key
   GMAIL_USER=your_email@gmail.com
   GMAIL_PASSWORD=your_gmail_app_password
   ```

## Project Structure

```
.
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── data/
│   ├── sample_jd.txt     # Sample job description
│   └── sample_resumes/   # Sample resume files
├── output/
│   └── jd_summary.json   # Generated job analysis output
└── src/
    ├── __init__.py
    ├── api_client.py      # API client for external integrations
    ├── gmail_integration.py # Email functionality
    ├── jd_analyzer.py     # Job description analysis
    ├── jd_summarizer.py   # AI-powered JD summarization
    ├── ranker.py          # Resume ranking algorithm
    └── resume_parser.py   # Resume parsing logic
└── tests/
    ├── test_api.py        # API client tests
    ├── test_json.py       # JSON handling tests
    └── test_ranker.py     # Ranking algorithm tests
```

## Usage

### Basic Workflow

1. **Analyze a Job Description**
   ```python
   from src.jd_summarizer import analyze_job_description
   
   jd_text = "Your job description here..."
   summary = analyze_job_description(jd_text)
   ```

2. **Parse Resumes**
   ```python
   from src.resume_parser import parse_resume
   
   resume_data = parse_resume("path/to/resume.pdf")
   ```

3. **Rank Candidates**
   ```python
   from src.ranker import rank_resumes
   
   rankings = rank_resumes(jd_summary, resumes)
   ```

### API Usage

Start the API server and integrate with external systems for automated hiring workflows.

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Contributing

1. Create a feature branch (`git checkout -b feature/improvement`)
2. Commit your changes (`git commit -am 'Add improvement'`)
3. Push to the branch (`git push origin feature/improvement`)
4. Submit a Pull Request

## License

This project is confidential and proprietary to Irembo.

## Support

For questions or issues, please contact the development team or create an issue in the repository.
