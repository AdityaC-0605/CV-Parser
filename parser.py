import re
import os
import json
from PyPDF2 import PdfReader
import docx2txt
import spacy

class ResumeParser:
    def __init__(self):
        # Load the spaCy model for NER and text processing
        self.nlp = spacy.load('en_core_web_lg')
        
        # Define common section headers in resumes
        self.section_headers = {
            'skills': ['skills', 'technical skills', 'core skills', 'competencies', 'expertise', 'technologies', 'tech stack'],
            'education': ['education', 'academic background', 'qualifications', 'academic qualifications'],
            'contact': ['contact', 'personal details', 'contact information', 'personal information']
        }
        
        # Comprehensive technical skills categorized
        self.technical_skills = {
            "Programming Languages": [
                "python", "javascript", "java", "c++", "c#", "go", "rust", "typescript",
                "ruby", "php", "swift", "kotlin", "scala", "r", "matlab"
            ],
            "Database Technologies": [
                "sql", "mysql", "postgresql", "mongodb", "oracle", "microsoft sql server",
                "sqlite", "redis", "cassandra", "dynamodb", "elasticsearch"
            ],
            "Cloud Platforms": [
                "aws", "azure", "google cloud platform", "gcp", "ibm cloud",
                "oracle cloud", "heroku", "digitalocean"
            ],
            "Web Frameworks & Libraries": [
                "react", "angular", "vue.js", "django", "flask", "spring boot",
                "express.js", "ruby on rails", "asp.net", "laravel"
            ],
            "DevOps & Deployment": [
                "docker", "kubernetes", "jenkins", "gitlab ci/cd", "github actions",
                "terraform", "ansible", "puppet", "chef", "circleci"
            ],
            "Data Science & AI": [
                "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
                "keras", "nltk", "spacy", "apache spark", "hadoop"
            ],
            "Frontend Technologies": [
                "html5", "css3", "sass", "scss", "bootstrap", "tailwind",
                "jquery", "redux", "webpack", "graphql", "material ui"
            ],
            "Mobile Development": [
                "react native", "flutter", "xamarin", "ionic", "android sdk",
                "ios sdk", "cordova"
            ],
            "Version Control": [
                "git", "svn", "mercurial"
            ],
            "Testing Tools": [
                "jest", "selenium", "junit", "mocha", "cypress", "testng", "pytest"
            ],
            "Project Management & Methodologies": [
                "agile", "scrum", "kanban", "jira", "confluence", "trello"
            ]
        }
        
        # Flatten the technical skills for easier searching
        self.all_skills = set()
        for category in self.technical_skills.values():
            self.all_skills.update([skill.lower() for skill in category])
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
        return text
    
    def extract_text_from_docx(self, docx_path):
        """Extract text from DOCX file"""
        try:
            text = docx2txt.process(docx_path)
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ""
    
    def extract_text(self, file_path):
        """Extract text based on file extension"""
        _, file_extension = os.path.splitext(file_path)
        
        if file_extension.lower() == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension.lower() == '.docx':
            return self.extract_text_from_docx(file_path)
        else:
            print(f"Unsupported file format: {file_extension}")
            return ""
    
    def extract_sections(self, text):
        """Split resume text into sections"""
        sections = {}
        current_section = "unknown"
        section_text = []
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a section header
            section_found = False
            for section, headers in self.section_headers.items():
                if any(header.lower() in line.lower() for header in headers):
                    # Save previous section before starting new one
                    if section_text:
                        sections[current_section] = '\n'.join(section_text)
                    current_section = section
                    section_text = []
                    section_found = True
                    break
            
            if not section_found:
                section_text.append(line)
        
        # Add the last section
        if section_text:
            sections[current_section] = '\n'.join(section_text)
            
        return sections
    
    def extract_skills(self, text):
        """Extract skills from resume text"""
        skills = set()
        
        # Extract skills from skills section if available
        sections = self.extract_sections(text)
        if 'skills' in sections:
            skills_text = sections['skills']
            # Use NLP to extract skills
            doc = self.nlp(skills_text)
            
            # Extract noun phrases and check against our comprehensive skills list
            for chunk in doc.noun_chunks:
                skill_text = chunk.text.lower()
                if skill_text in self.all_skills:
                    skills.add(skill_text)
            
            # Look for exact matches of technical skills
            for skill in self.all_skills:
                if re.search(r'\b' + re.escape(skill) + r'\b', skills_text.lower()):
                    skills.add(skill)
        
        # Also look for skills in the entire document
        doc = self.nlp(text)
        for token in doc:
            if token.text.lower() in self.all_skills:
                skills.add(token.text.lower())
        
        # Categorize found skills
        categorized_skills = {}
        for category, category_skills in self.technical_skills.items():
            category_matches = [skill for skill in skills if skill.lower() in [s.lower() for s in category_skills]]
            if category_matches:
                categorized_skills[category] = sorted(category_matches)
        
        return categorized_skills
    
    def parse_resume(self, file_path):
        """Main function to parse a resume"""
        text = self.extract_text(file_path)
        if not text:
            return {
                'error': 'Could not extract text from the file',
                'file_path': file_path
            }
        
        skills = self.extract_skills(text)
        
        return {
            'skills': skills
        }


# Example usage
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Replace with your actual resume file path
    resume_path = "your_resume.pdf"  # or "your_resume.docx"
    result = parser.parse_resume(resume_path)
    print(json.dumps(result, indent=2))