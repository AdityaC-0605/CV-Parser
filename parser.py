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
            'experience': ['experience', 'work experience', 'employment history', 'work history', 'professional experience'],
            'skills': ['skills', 'technical skills', 'core skills', 'competencies', 'expertise', 'technologies', 'tech stack'],
            'education': ['education', 'academic background', 'qualifications', 'academic qualifications'],
            'contact': ['contact', 'personal details', 'contact information', 'personal information']
        }
        
        # Common technical skills to look for
        self.tech_skills = ['python', 'java', 'javascript', 'react', 'nodejs', 'sql', 'mongodb', 'aws', 'docker', 
                           'kubernetes', 'machine learning', 'ai', 'data science', 'css', 'html', 'php', 'c++',
                           'c#', 'golang', 'rust', 'swift', 'angular', 'vue', 'django', 'flask', 'ruby', 'rails',
                           'scala', 'hadoop', 'spark', 'tensorflow', 'pytorch', 'nlp', 'computer vision', 'devops',
                           'git', 'ci/cd', 'terraform', 'cloud', 'azure', 'gcp', 'linux', 'agile', 'scrum', 'jira']
    
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
            
            # Extract noun phrases as potential skills
            for chunk in doc.noun_chunks:
                skills.add(chunk.text.lower())
            
            # Look for common tech skills
            for skill in self.tech_skills:
                if re.search(r'\b' + re.escape(skill) + r'\b', skills_text.lower()):
                    skills.add(skill)
        
        # Also look for skills in the entire document
        doc = self.nlp(text)
        for token in doc:
            if token.text.lower() in self.tech_skills:
                skills.add(token.text.lower())
        
        return list(skills)
    
    def extract_experience(self, text):
        """Extract work experience from resume"""
        experiences = []
        
        sections = self.extract_sections(text)
        if 'experience' in sections:
            exp_text = sections['experience']
            
            # Find experience entries using patterns
            # Look for company names, job titles, and dates
            exp_blocks = re.split(r'\n{2,}', exp_text)
            
            for block in exp_blocks:
                # Try to extract job title, company, and dates
                job_title = None
                company = None
                dates = None
                description = []
                
                lines = block.split('\n')
                for i, line in enumerate(lines):
                    # Try to extract dates (MM/YYYY - MM/YYYY or similar formats)
                    date_match = re.search(r'(\d{1,2}/\d{2,4}|\d{4})\s*[-–—to]*\s*(\d{1,2}/\d{2,4}|\d{4}|present|current)', 
                                          line.lower())
                    if date_match and not dates:
                        dates = line.strip()
                        continue
                    
                    # First non-date line is likely job title
                    if i == 0 and not date_match and not job_title:
                        job_title = line.strip()
                        continue
                    
                    # Second non-date line might be company
                    if i == 1 and not date_match and not company:
                        company = line.strip()
                        continue
                    
                    # Rest is description
                    description.append(line.strip())
                
                if job_title or company or dates:
                    experiences.append({
                        'job_title': job_title,
                        'company': company,
                        'dates': dates,
                        'description': ' '.join(description) if description else None
                    })
        
        return experiences
    
    def parse_resume(self, file_path):
        """Main function to parse a resume"""
        text = self.extract_text(file_path)
        if not text:
            return {
                'error': 'Could not extract text from the file',
                'file_path': file_path
            }
        
        skills = self.extract_skills(text)
        experience = self.extract_experience(text)
        
        return {
            'skills': skills,
            'experience': experience
        }


# Example usage
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Example: Parse resume file
    result = parser.parse_resume("path_to_resume.pdf")
    print(json.dumps(result, indent=2))