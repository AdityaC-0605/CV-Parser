# NextLeap Resume Parser

An AI-powered resume parsing tool that extracts key information from resumes for the NextLeap career navigator platform. This tool uses natural language processing (NLP) to accurately extract skills and work experience from PDF and DOCX resumes.


## Features

- 📄 Support for PDF and DOCX resume formats
- 🔍 Advanced NLP-based skill extraction
- 💼 Accurate work experience identification
- 🔄 Modern web interface with drag & drop functionality
- 📊 Clean visualization of parsed results
- 🚀 Easy to integrate with existing systems

## Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/AdityaC-0605/CV-Parser.git
   cd CV-parser
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download the spaCy language model:
   ```bash
   python -m spacy download en_core_web_lg
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
nextleap-resume-parser/
├── app.py                  # Flask web application
├──parser.py                # Core resume parsing functionality
├── requirements.txt        # Python dependencies
├── templates/
│   └── index.html          # Web interface
└── README.md               # This documentation
```

## How It Works

1. **Document Processing**: Converts PDF/DOCX files to text
2. **Section Identification**: Identifies different sections in the resume
3. **Skill Extraction**: Uses NLP and pattern matching to identify skills
4. **Experience Extraction**: Extracts job titles, companies, dates, and descriptions
5. **Result Compilation**: Organizes extracted information into structured data

## API Reference

### Endpoint: `/parse-resume`

**Method**: POST

**Request**:
- Form data with 'resume' file field (PDF or DOCX)

**Response**:
```json
{
  "skills": ["Python", "NLP", "Machine Learning", "Flask", "React"],
  "experience": [
    {
      "job_title": "Senior Software Engineer",
      "company": "Tech Company Inc.",
      "dates": "2020 - Present",
      "description": "Led development of AI-powered solutions..."
    },
    {
      "job_title": "Software Developer",
      "company": "Startup Labs",
      "dates": "2018 - 2020",
      "description": "Developed and maintained web applications..."
    }
  ]
}
```

## Integration with NextLeap

This resume parser is designed to seamlessly integrate with the larger NextLeap AI career navigator platform:

1. **Job Matching**: Use extracted skills to match candidates with job opportunities
2. **Culture Fit Analysis**: Process work experience to analyze workplace culture compatibility
3. **Career Path Prediction**: Leverage work history data to predict optimal career moves

## Customization

### Adding New Skills Recognition

Edit the `tech_skills` list in the `ResumeParser` class to add more skills:

```python
# In resume_parser.py
self.tech_skills = [
    'python', 'java', 'javascript',
    # Add your skills here
    'kubernetes', 'terraform', 'blockchain'
]
```

### Changing Resume Sections

Modify the `section_headers` dictionary to adjust section recognition:

```python
# In resume_parser.py
self.section_headers = {
    'experience': ['experience', 'work experience', 'employment history'],
    'skills': ['skills', 'technical skills', 'core competencies'],
    # Add or modify sections here
    'projects': ['projects', 'personal projects', 'key projects']
}
```

## Future Improvements

- [ ] Extract education details
- [ ] Add support for more resume formats (HTML, TXT)
- [ ] Implement better date parsing for experience
- [ ] Enhance skill categorization (technical, soft, languages)
- [ ] Improve accuracy with machine learning models
- [ ] Add batch processing capabilities
- [ ] Implement user authentication for security
- [ ] Develop a dashboard for resume analytics


## Acknowledgments

- [spaCy](https://spacy.io/) for NLP capabilities
- [PyPDF2](https://pythonhosted.org/PyPDF2/) for PDF processing
- [docx2txt](https://github.com/ankushshah89/python-docx2txt) for DOCX processing
- [Flask](https://flask.palletsprojects.com/) for the web framework

---

Built with ❤️ for NextLeap - AI-powered career navigator
