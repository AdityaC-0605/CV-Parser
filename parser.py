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
            'skills': ['skills', 'technical skills', 'core skills', 'competencies', 'expertise', 'technologies', 'tech stack']
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
        text = ""
        try:
            pdf_path = pdf_path.strip('"').strip("'")  # Handle both single and double quotes
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
        return text

    def extract_text_from_docx(self, docx_path):
        try:
            docx_path = docx_path.strip('"').strip("'")  # Handle both single and double quotes
            text = docx2txt.process(docx_path)
            return text
        except Exception as e:
            print(f"Error reading DOCX: {str(e)}")
            return ""

    def extract_text(self, file_path):
        file_path = file_path.strip('"').strip("'")  # Handle both single and double quotes
        
        if not os.path.exists(file_path):
            print(f"Error: File not found at path: {file_path}")
            return ""
            
        if file_path.lower().endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            return self.extract_text_from_docx(file_path)
        else:
            print("Unsupported file format. Please provide a PDF or DOCX file.")
            return ""

    def extract_skills(self, doc):
        """
        Extract skills from the document text and categorize them according to technical_skills
        Args:
            doc: The processed document text
        Returns:
            dict: Categorized skills found in the resume
        """
        categorized_skills = {category: [] for category in self.technical_skills.keys()}
        
        # Convert doc text to lowercase for better matching
        text_lower = doc.text.lower()
        
        # Extract skills from all categories
        for category, skill_list in self.technical_skills.items():
            for skill in skill_list:
                # Check for exact word boundaries
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    categorized_skills[category].append(skill)
        
        # Remove empty categories
        categorized_skills = {k: v for k, v in categorized_skills.items() if v}
        
        return categorized_skills

    def analyze_skill_match(self, candidate_skills, required_skills):
        """Analyze how well the candidate's skills match the required skills"""
        # Flatten the categorized skills into a single list
        all_candidate_skills = []
        for skills in candidate_skills.values():
            all_candidate_skills.extend(skills)
        
        candidate_skills_lower = {skill.lower() for skill in all_candidate_skills}
        required_skills_lower = {skill.lower() for skill in required_skills}
        
        matched_skills = []
        missing_skills = []
        
        for req_skill in required_skills:
            if any(candidate.lower() in req_skill.lower() or req_skill.lower() in candidate.lower() 
                  for candidate in all_candidate_skills):
                matched_skills.append(req_skill)
            else:
                missing_skills.append(req_skill)
        
        match_percentage = (len(matched_skills) / len(required_skills)) * 100 if required_skills else 0
        
        return {
            'match_percentage': match_percentage,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills
        }

    def parse_resume(self, file_path, target_job=None):
        """Parse the resume and extract relevant information"""
        # Extract text from the resume
        text = self.extract_text(file_path)
        if not text:
            return None

        # Process the text with spaCy
        doc = self.nlp(text)

        # Extract information
        categorized_skills = self.extract_skills(doc)

        # Prepare the result
        result = {
            "categorized_skills": categorized_skills,
        }

        # If target job is provided, analyze skill match
        if target_job and target_job in self.job_roles_skills:
            required_skills = self.job_roles_skills[target_job]
            skill_match = self.analyze_skill_match(categorized_skills, required_skills)
            result["skill_match"] = skill_match
            result["target_job"] = target_job

        return result

def main():
    parser = ResumeParser()
    
    # Get file path from user
    file_path = input("Enter the path to your resume (PDF or DOCX): ").strip()
    
    if not file_path:
        print("Error: No file path provided")
        return
        
    if not os.path.exists(file_path.strip('"').strip("'")):
        print(f"Error: File not found at path: {file_path}")
        return
    
    # Parse the resume without target job first to display skills
    initial_results = parser.parse_resume(file_path)
    
    if initial_results and "categorized_skills" in initial_results:
        print("\nExtracted Skills:")
        print("----------------")
        
        for category, skills in initial_results["categorized_skills"].items():
            print(f"\n{category}:")
            for skill in skills:
                print(f"• {skill}")
    else:
        print("No skills were extracted from the resume. Please check the file and try again.")
        return
    
    # Now ask for target job role
    print("\nWould you like to analyze the resume for a specific job role?")
    print("Enter 'y' for yes, any other key for no: ")
    analyze_job = input().lower() == 'y'
    
    if not analyze_job:
        return
        
    # Get target job if user wants analysis
    target_job = None
    print("\nAvailable job roles:")
    job_roles = list(parser.job_roles_skills.keys())
    for i, job in enumerate(job_roles, 1):
        print(f"{i}. {job}")
    
    while True:
        try:
            job_index = int(input("\nEnter the number of the desired job role: ")) - 1
            if 0 <= job_index < len(job_roles):
                target_job = job_roles[job_index]
                break
            else:
                print("Invalid selection. Please enter a number from the list.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Parse the resume with target job for matching analysis
    results = parser.parse_resume(file_path, target_job)
    
    if results and "skill_match" in results:
        print(f"\nSkill Match Analysis for {results['target_job']}:")
        print(f"Match Percentage: {results['skill_match']['match_percentage']:.1f}%")
        
        print("\nMatched Skills:")
        for skill in results["skill_match"]["matched_skills"]:
            print(f"• {skill}")
        
        print("\nMissing Skills:")
        for skill in results["skill_match"]["missing_skills"]:
            print(f"• {skill}")
    else:
        print("Failed to analyze skills for the selected job role.")

if __name__ == "__main__":
    main()