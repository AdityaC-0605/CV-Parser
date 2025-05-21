import google.generativeai as genai
from typing import List
import os

class GeminiSkillsAdvisor:
    def __init__(self, api_key=None):
        """
        Initialize the Gemini API client
        Args:
            api_key: The Gemini API key, if None will try to get from environment
        """
        if api_key is None:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("No API key provided and GEMINI_API_KEY not found in environment variables")
        
        # Configure the Gemini API
        genai.configure(api_key="AIzaSyCKf18vh6Llc-2nZT3uToA-zwS-0y5GT2Y")
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def get_skill_information(self, skill_name: str) -> str:
        """
        Get information about a specific skill from Gemini
        Args:
            skill_name: The name of the skill
        Returns:
            str: Detailed information about the skill
        """
        prompt = f"""
        Provide concise information about the technical skill "{skill_name}" for someone who wants to learn it:
        1. Brief explanation of what {skill_name} is (1-2 sentences)
        2. Why it's important in tech/industry (1 sentence)
        3. Resources to learn it (1-2 top resources)
        4. Approximate time to learn basics (1 sentence)
        
        Keep the entire response under 150 words.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error fetching information about {skill_name}: {str(e)}"
    
    def get_missing_skills_info(self, missing_skills: List[str]) -> dict:
        """
        Get information about multiple missing skills
        Args:
            missing_skills: List of skills to get information about
        Returns:
            dict: Dictionary mapping each skill to its information
        """
        skills_info = {}
        
        for skill in missing_skills:
            skills_info[skill] = self.get_skill_information(skill)
            
        return skills_info


# Add this function to your ResumeParser class
    def get_missing_skills_advice(self, missing_skills, gemini_advisor):
        """
        Get advice about missing skills from Gemini
        Args:
            missing_skills (list): List of missing skills
            gemini_advisor: Initialized GeminiSkillsAdvisor object
        Returns:
            dict: Dictionary with information about each missing skill
        """
        if not missing_skills:
            return {}
        
        return gemini_advisor.get_missing_skills_info(missing_skills)