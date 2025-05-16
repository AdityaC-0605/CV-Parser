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

        self.job_roles_skills = {
            "Software Developer / Engineer": [
                "Data Structures & Algorithms", "Object-Oriented Programming", "Version Control (Git)",
                "Software Development Lifecycle (SDLC)", "Debugging & Troubleshooting",
                "Database Management", "Agile Methodologies", "Unit Testing"
            ],
            "Full Stack Developer": [
                "HTML/CSS/JavaScript", "React.js or Angular", "Node.js or Django", 
                "RESTful APIs", "Database Systems (SQL/NoSQL)", "Authentication & Authorization",
                "DevOps Basics", "Version Control (Git)"
            ],
            "Front-End Developer (React, Angular, etc.)": [
                "HTML/CSS", "JavaScript/TypeScript", "React.js/Angular/Vue.js",
                "Responsive Design", "Cross-Browser Compatibility", "State Management (Redux, Context API)",
                "Webpack/Vite", "UI/UX Principles"
            ],
            "Back-End Developer (Node.js, Django, Spring Boot, etc.)": [
                "Server-Side Languages (Java, Python, JS)", "Database Design", "RESTful API Development",
                "Authentication & Authorization", "ORMs (Hibernate, Sequelize, etc.)",
                "Microservices Architecture", "Caching (Redis, Memcached)", "Security Best Practices"
            ],
            "Mobile App Developer (Android/iOS)": [
                "Kotlin/Java (Android)", "Swift/Objective-C (iOS)", "Flutter/React Native",
                "Mobile UI/UX Design", "APIs & JSON Parsing", "App Deployment", 
                "State Management", "Version Control"
            ],
            "DevOps Engineer": [
                "CI/CD Pipelines", "Docker & Kubernetes", "Infrastructure as Code (Terraform/Ansible)",
                "Cloud Platforms (AWS/Azure/GCP)", "Monitoring Tools (Prometheus, Grafana)",
                "Scripting (Bash/Python)", "Version Control", "System Administration"
            ],
            "Site Reliability Engineer (SRE)": [
                "System Monitoring", "Incident Management", "Automation & Scripting",
                "Cloud Infrastructure", "CI/CD", "Performance Tuning", "SLIs/SLOs", "Containerization"
            ],
            "Embedded Software Engineer": [
                "C/C++", "RTOS", "Microcontrollers (ARM, AVR)", "Low-Level Programming",
                "Embedded Linux", "I2C/SPI/UART", "PCB Debugging", "Memory Optimization"
            ],
            "Game Developer": [
                "C++/C#", "Unity/Unreal Engine", "Game Physics", "3D Math", 
                "Graphics APIs (OpenGL/DirectX)", "Version Control", "Shader Programming", "AI for Games"
            ],
            "API Developer": [
                "RESTful API Design", "GraphQL", "Swagger/OpenAPI", "Authentication (OAuth2, JWT)",
                "Rate Limiting", "Error Handling", "API Versioning", "Testing Tools (Postman, Insomnia)"
            ],
            "Software Architect": [
                "System Design", "Design Patterns", "Architecture Styles (Microservices, Monoliths)",
                "UML Diagrams", "Scalability & Performance", "Security Architecture",
                "Tech Stack Evaluation", "DevOps Integration"
            ],
            "Cloud Developer (AWS/GCP/Azure)": [
                "Cloud Services (EC2, Lambda, S3)", "Infrastructure as Code", 
                "Serverless Computing", "Containers", "Cloud Security", 
                "CI/CD Pipelines", "Monitoring & Logging", "SDKs & APIs"
            ],

            # 📊 Data Science & Analytics
            "Data Scientist": [
                "Python/R", "Statistics", "Machine Learning", "Data Cleaning",
                "Data Visualization", "SQL", "Model Evaluation", "Big Data Tools"
            ],
            "Data Analyst": [
                "Excel", "SQL", "Data Visualization Tools (Tableau, Power BI)", 
                "Python (Pandas, NumPy)", "Business Acumen", "Descriptive Statistics", 
                "Reporting & Dashboards", "Data Wrangling"
            ],
            "Business Intelligence Analyst": [
                "Data Warehousing", "SQL", "ETL Processes", "BI Tools (Tableau, Power BI)",
                "KPI Analysis", "Data Modeling", "Reporting Automation", "Data Governance"
            ],
            "Machine Learning Engineer": [
                "Supervised/Unsupervised Learning", "Model Deployment (Flask/FastAPI)",
                "Feature Engineering", "Scikit-learn", "Deep Learning Frameworks (TensorFlow, PyTorch)",
                "MLOps Basics", "Data Pipelines", "Model Optimization"
            ],
            "Data Engineer": [
                "ETL Pipelines", "Big Data Technologies (Hadoop, Spark)", "SQL & NoSQL",
                "Data Warehousing", "Cloud Data Services", "Python/Scala", "Airflow/Luigi", "Streaming Data"
            ],
            "Big Data Engineer": [
                "Apache Spark", "Hadoop Ecosystem", "Kafka", "HDFS", 
                "Distributed Computing", "SQL/NoSQL", "Data Ingestion", "Data Lake Architecture"
            ],
            "Decision Scientist": [
                "A/B Testing", "Causal Inference", "Statistical Modeling", "R/Python",
                "Experiment Design", "Business KPIs", "Visualization", "Data Interpretation"
            ],
            "AI/ML Research Scientist": [
                "Mathematics (Linear Algebra, Probability)", "Deep Learning", "Research Methodology",
                "Model Architectures", "Paper Reading & Writing", "Experimentation",
                "Python + PyTorch/TensorFlow", "High-Performance Computing"
            ],
            "NLP Engineer": [
                "Text Preprocessing", "Language Modeling", "Transformers (BERT, GPT)", 
                "NER & POS Tagging", "Word Embeddings", "SpaCy/NLTK", 
                "Text Classification", "Question Answering"
            ],
            "Deep Learning Engineer": [
                "Neural Networks", "CNNs/RNNs", "PyTorch/TensorFlow", 
                "Model Training & Evaluation", "Hyperparameter Tuning", 
                "Transfer Learning", "GPU Computing", "Data Augmentation"
            ],
            "Computer Vision Engineer": [
                "Image Processing", "OpenCV", "CNNs", "Object Detection (YOLO, SSD)",
                "Segmentation Techniques", "Deep Learning Frameworks", 
                "Dataset Annotation", "Model Optimization"
            ],
            "MLOps Engineer": [
                "Model Deployment", "CI/CD for ML", "Model Monitoring", 
                "Docker & Kubernetes", "Data Versioning (DVC)", 
                "MLflow/TensorBoard", "Pipeline Automation", "Cloud ML Tools"
            ],

            # 🔐 Cybersecurity
            "Cybersecurity Analyst": [
                "Threat Detection", "SIEM Tools", "Incident Response", "Network Security",
                "Risk Assessment", "Log Analysis", "Firewalls & IDS/IPS", "Security Policies"
            ],
            "Security Engineer": [
                "System Hardening", "Vulnerability Management", "Penetration Testing",
                "Cloud Security", "Network Protocols", "Secure Coding", "Encryption", "Monitoring Tools"
            ],
            "Penetration Tester / Ethical Hacker": [
                "Reconnaissance Techniques", "Exploitation Frameworks (Metasploit)", "Network Scanning",
                "Web App Security", "OWASP Top 10", "Social Engineering", "Scripting", "Report Writing"
            ],
            "Security Architect": [
                "Security Frameworks (NIST, ISO)", "Architecture Design", "Zero Trust",
                "Cloud Security Architecture", "IAM", "Risk Management", "DevSecOps", "Threat Modeling"
            ],
            "Network Security Engineer": [
                "Firewall Configuration", "VPNs", "IDS/IPS", "Routing Protocols",
                "Security Audits", "Network Monitoring", "NAC", "Packet Analysis"
            ],
            "SOC Analyst": [
                "Security Alerts Analysis", "SIEM Tools", "Log Management", "Incident Response Playbooks",
                "Threat Intelligence", "Triage & Escalation", "Ticketing Systems", "Shift Work Experience"
            ],
            "Information Security Analyst": [
                "Security Policies", "Data Loss Prevention", "Access Control", 
                "Compliance Standards", "Risk Assessment", "Antivirus/EDR", 
                "Incident Handling", "Vulnerability Scanning"
            ],
            "Cryptographer": [
                "Symmetric/Asymmetric Encryption", "Cryptographic Protocols", 
                "Public Key Infrastructure (PKI)", "Blockchain Basics", "Mathematics", 
                "Hash Functions", "Digital Signatures", "Secure Communication"
            ],

            # ☁ Cloud & Infrastructure
            "Cloud Solutions Architect": [
                "Cloud Platforms (AWS/GCP/Azure)", "Solution Design", "Scalability & Redundancy", 
                "Security Best Practices", "Hybrid Architecture", "Networking", 
                "Cost Optimization", "Cloud Migrations"
            ],
            "Cloud Engineer": [
                "Cloud Services Deployment", "Automation Scripts", "Containers & Orchestration", 
                "Monitoring Tools", "Networking", "Cloud Security", 
                "DevOps Tools", "IAM Management"
            ],
            "System Administrator": [
                "Linux/Windows Administration", "Shell Scripting", "User Management", 
                "Backup & Recovery", "Monitoring Tools", "Networking Basics", 
                "Patch Management", "Server Configuration"
            ],
            "Network Engineer": [
                "TCP/IP", "Routing/Switching", "Network Troubleshooting", 
                "Firewalls", "VPNs", "Cisco Devices", "QoS", "LAN/WAN Design"
            ],
            "IT Infrastructure Engineer": [
                "Hardware Management", "Network Configuration", "Server Administration", 
                "Virtualization", "Storage Solutions", "Disaster Recovery", 
                "Monitoring Tools", "Compliance Standards"
            ],
            "Database Administrator (DBA)": [
                "SQL", "Database Design", "Backup & Recovery", "Indexing & Optimization", 
                "Replication", "Security & Access Control", "Monitoring", "Stored Procedures"
            ],
            "Virtualization Engineer": [
                "VMware/Hyper-V", "Virtual Machine Management", "Storage Integration",
                "Disaster Recovery", "Network Configuration", "Automation Tools", 
                "Patch Management", "Security Settings"
            ],
            "Storage Engineer": [
                "SAN/NAS", "RAID Configurations", "Backup Solutions", 
                "Storage Provisioning", "Performance Tuning", "Data Migration", 
                "Disaster Recovery", "Monitoring Tools"
            ],

            # 🖥 IT Support & Systems
            "Technical Support Engineer": [
                "Troubleshooting Skills", "Remote Desktop Tools", "Ticketing Systems", 
                "Networking Basics", "OS Installation", "Hardware Support", 
                "Communication Skills", "User Training"
            ],
            "IT Support Specialist": [
                "Technical Documentation", "Customer Support", "Problem Solving", 
                "Windows/Mac/Linux Support", "Software Installation", "System Monitoring", 
                "Printer/Peripheral Setup", "Email/Outlook Support"
            ],
            "Help Desk Technician": [
                "Basic Networking", "Account Setup", "Password Resets", 
                "Customer Service", "Documentation", "Antivirus Installation", 
                "Incident Logging", "Remote Assistance"
            ],
            "System Support Engineer": [
                "OS & Server Maintenance", "Hardware Diagnosis", "Performance Monitoring", 
                "Scripting (PowerShell/Bash)", "User Access Management", "Network Tools", 
                "Patch Updates", "System Logs Analysis"
            ],
            "Desktop Support Engineer": [
                "Workstation Setup", "Troubleshooting", "Hardware Replacement", 
                "Remote Support", "OS Configuration", "Software Installation", 
                "Printer Issues", "Asset Management"
            ],

            # 🧪 Testing & Quality Assurance
            "QA Engineer": [
                "Test Planning", "Bug Reporting", "Functional Testing", 
                "Regression Testing", "Test Case Design", "Automation Basics", 
                "JIRA/TestRail", "Agile Testing"
            ],
            "Automation Test Engineer": [
                "Selenium", "TestNG/JUnit", "CI/CD Tools", 
                "Java/Python Scripting", "API Testing", "Test Automation Frameworks", 
                "Bug Tracking Tools", "Reporting"
            ],
            "Manual Test Engineer": [
                "Test Cases Design", "Functional Testing", "Regression Testing", 
                "Exploratory Testing", "Defect Reporting", "Cross-Browser Testing", 
                "Test Documentation", "Agile Practices"
            ],
            "Performance Tester": [
                "JMeter/LoadRunner", "Load Testing", "Stress Testing", 
                "Bottleneck Analysis", "Monitoring Tools", "Scripting Skills", 
                "Test Data Preparation", "Result Analysis"
            ],
            "SDET (Software Development Engineer in Test)": [
                "OOP Concepts", "Selenium/Test Automation", "API Testing", 
                "Unit Testing", "CI/CD Integration", "Framework Development", 
                "Java/Python", "Agile/DevOps Practices"
            ],
            "Test Architect": [
                "Test Strategy", "Automation Architecture", "Tool Selection", 
                "Framework Design", "CI/CD Integration", "Mentoring Test Teams", 
                "Performance & Security Testing", "Scalability Testing"
            ],

            # 📱 UI/UX and Web Technology
            "UI Developer": [
                "HTML/CSS/JavaScript", "Responsive Design", "Cross-Browser Compatibility", 
                "UI Frameworks", "Design to Code Conversion", "CSS Preprocessors", 
                "Version Control", "Accessibility Standards"
            ],
            "UX Designer": [
                "User Research", "Wireframing", "Prototyping Tools (Figma, Adobe XD)", 
                "Information Architecture", "User Journey Mapping", "Usability Testing", 
                "Interaction Design", "Design Thinking"
            ],
            "Web Developer": [
                "HTML/CSS/JavaScript", "Frontend Frameworks", "Backend Technologies", 
                "Databases", "API Integration", "Responsive Design", 
                "Web Hosting", "Version Control"
            ],
            "Frontend Engineer": [
                "React/Angular/Vue", "JavaScript/TypeScript", "Performance Optimization", 
                "Unit Testing", "State Management", "CI/CD", "Accessibility", "CSS-in-JS"
            ],
            "Interaction Designer": [
                "Animation Principles", "Wireframes & Prototypes", "Microinteractions", 
                "Design Systems", "Figma/Sketch", "Usability Testing", 
                "Motion Design", "User Flow Design"
            ],

            # 🧠 AI Research & Emerging Tech
            "AI Research Scientist": [
                "Mathematical Modeling", "Deep Learning", "Research Paper Writing", 
                "Neural Architecture Search", "Experimentation", "Data Collection", 
                "Model Evaluation", "Scientific Computing"
            ],
            "Robotics Engineer": [
                "Robot Kinematics", "Embedded Systems", "Sensor Integration", 
                "ROS (Robot Operating System)", "Path Planning", "Control Theory", 
                "Computer Vision", "Simulation Tools"
            ],
            "Quantum Computing Researcher": [
                "Quantum Mechanics", "Qiskit/Cirq", "Linear Algebra", 
                "Quantum Algorithms", "Quantum Gates", "Complexity Theory", 
                "Simulation Tools", "Research & Publications"
            ],
            "Blockchain Developer": [
                "Smart Contracts (Solidity)", "Ethereum/BTC Protocols", "DApp Development", 
                "Cryptography", "Consensus Mechanisms", "Web3.js", "Blockchain Security", "Decentralized Storage"
            ],
            "AR/VR Developer": [
                "Unity/Unreal", "3D Modeling", "ARKit/ARCore", 
                "Computer Vision", "XR Interaction", "Shader Programming", 
                "VR Hardware Integration", "Spatial Audio"
            ],
            "Computer Vision Researcher": [
                "Object Detection", "Segmentation", "Deep Learning", 
                "Mathematical Modeling", "Dataset Preparation", "Custom Architectures", 
                "Paper Implementation", "Benchmarking"
            ],

            # 🧑‍🏫 Technical Management & Consulting
            "Technical Program Manager (TPM)": [
                "Project Management", "Agile/Scrum", "Technical Documentation", 
                "Stakeholder Communication", "Risk Management", "Resource Planning", 
                "Roadmap Definition", "Cross-Team Coordination"
            ],
            "Engineering Manager": [
                "Team Leadership", "Code Reviews", "Hiring & Mentoring", 
                "Project Management", "Technical Strategy", "Sprint Planning", 
                "Architecture Oversight", "Performance Reviews"
            ],
            "Product Manager (Technical)": [
                "Product Lifecycle", "User Research", "Technical Background", 
                "Roadmapping", "Wireframing", "Agile Methodology", 
                "Stakeholder Management", "Data-Driven Decisions"
            ],
            "IT Consultant": [
                "Requirement Analysis", "System Integration", "Technology Evaluation", 
                "Client Communication", "Solution Architecture", "Documentation", 
                "Change Management", "IT Governance"
            ]
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
    
    def parse_resume(self, file_path, job_role=None):
        """Main function to parse a resume"""
        text = self.extract_text(file_path)
        if not text:
            return {
                'error': 'Could not extract text from the file',
                'file_path': file_path
            }
        
        skills = self.extract_skills(text)
        result = {'skills': skills}
        
        # If job role is specified, find missing skills
        if job_role and job_role in self.job_roles_skills:
            required_skills = self.job_roles_skills[job_role]
            user_skills = [skill.lower() for category in skills.values() for skill in category]
            
            # Find missing skills by comparing with required skills
            missing_skills = []
            for required_skill in required_skills:
                skill_found = False
                required_skill_lower = required_skill.lower()
                
                # Check if any part of the required skill matches user skills
                for user_skill in user_skills:
                    # Split skills into parts to handle variations
                    required_parts = set(re.split(r'[/\s&(),.]', required_skill_lower))
                    user_parts = set(re.split(r'[/\s&(),.]', user_skill))
                    
                    # Remove empty strings
                    required_parts = {part.strip() for part in required_parts if part.strip()}
                    user_parts = {part.strip() for part in user_parts if part.strip()}
                    
                    # If there's any significant overlap, consider it a match
                    if required_parts.intersection(user_parts):
                        skill_found = True
                        break
                
                if not skill_found:
                    missing_skills.append(required_skill)
            
            result['required_skills'] = required_skills
            result['missing_skills'] = missing_skills
            result['job_role'] = job_role
        
        return result


# Example usage
if __name__ == "__main__":
    parser = ResumeParser()
    
    # Replace with your actual resume file path
    resume_path = "your_resume.pdf"  # or "your_resume.docx"
    result = parser.parse_resume(resume_path)
    print(json.dumps(result, indent=2))