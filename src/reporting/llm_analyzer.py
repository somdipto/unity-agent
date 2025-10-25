"""
LLM Integration - Module for using LLMs to provide qualitative assessment
"""
import openai
import json
from typing import Dict, Any, Optional
from ..utils.config import get_api_key


class LLMAnalyzer:
    """
    Uses LLMs to provide qualitative assessment of game fun and engagement
    """
    
    def __init__(self, api_key: Optional[str] = None):
        if api_key:
            openai.api_key = api_key
        else:
            # Try to get API key from config
            key = get_api_key()
            if key:
                openai.api_key = key
            else:
                raise ValueError("No OpenAI API key provided or found in config")
    
    def assess_fun_factor(self, structured_data: Dict[str, Any]) -> str:
        """
        Use LLM to assess the fun factor based on structured analytics data
        """
        prompt = self._create_fun_assessment_prompt(structured_data)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert game designer and analyst. Assess the fun factor and engagement of a game based on playtesting data."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"LLM assessment failed: {str(e)}"
    
    def suggest_improvements(self, structured_data: Dict[str, Any]) -> str:
        """
        Use LLM to suggest game improvements based on issues found
        """
        prompt = self._create_improvement_suggestions_prompt(structured_data)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert game designer. Provide specific suggestions to improve a game based on playtesting data."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"LLM improvement suggestions failed: {str(e)}"
    
    def _create_fun_assessment_prompt(self, data: Dict[str, Any]) -> str:
        """Create a prompt for fun assessment"""
        return f"""
        Based on the following playtesting data, assess the fun factor and engagement of the game:

        {json.dumps(data, indent=2)}

        Please provide:
        1. An overall fun score from 1-10
        2. Explanation of your score with specific justification
        3. Key factors that enhance or detract from fun
        4. Potential user experience issues
        """
    
    def _create_improvement_suggestions_prompt(self, data: Dict[str, Any]) -> str:
        """Create a prompt for improvement suggestions"""
        return f"""
        Based on the following playtesting data, suggest specific improvements to the game:

        {json.dumps(data, indent=2)}

        Please provide:
        1. Priority issues that need immediate attention
        2. Specific, actionable suggestions for improvements
        3. Design recommendations to enhance fun and engagement
        4. Areas that are working well to preserve
        """
    
    def generate_narrative_report(self, analytics_data: Dict[str, Any]) -> str:
        """
        Generate a narrative report using LLM to explain the findings in story form
        """
        prompt = f"""
        Transform the following playtesting data into a narrative report that tells the story of how AI agents experienced the game:

        {json.dumps(analytics_data, indent=2)}

        Write in the style of a game reviewer, describing the journey of the AI agents through the game, highlighting notable events, challenges, and experiences. Focus on making it readable and insightful for human game developers.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a game designer creating a narrative report of an AI playtesting session."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"LLM narrative report failed: {str(e)}"