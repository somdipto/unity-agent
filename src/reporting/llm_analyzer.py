"""
LLM Integration - Module for using LLMs to provide qualitative assessment
"""
import openai
import json
import time
from typing import Dict, Any, Optional, Union, List
from ..utils.config import get_api_key


class LLMAnalyzer:
    """
    Uses LLMs to provide qualitative assessment of game fun and engagement.
    Implements structured prompting and iterative refinement for reliable JSON outputs.
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
                # Warning: This might fail at runtime if not set
                pass 
    
    def _query_llm_with_retry(self, 
                              system_prompt: str, 
                              user_prompt: str, 
                              max_retries: int = 3,
                              expected_format: str = "json") -> Union[Dict[str, Any], str]:
        """
        Execute LLM query with iterative refinement for JSON validation.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        for attempt in range(max_retries):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
                content = response.choices[0].message.content.strip()

                if expected_format == "json":
                    try:
                        # Attempt to parse JSON
                        parsed_content = json.loads(content)
                        return parsed_content
                    except json.JSONDecodeError as e:
                        print(f"Attempt {attempt + 1} failed JSON validation: {e}")
                        # Iterative Refinement: Feed error back to LLM
                        error_message = f"Your previous response was not valid JSON. Error: {str(e)}. \nPlease correct your output to be valid JSON matching the requested format.\n\nPrevious Output:\n{content}"
                        messages.append({"role": "assistant", "content": content})
                        messages.append({"role": "user", "content": error_message})
                else:
                    return content

            except Exception as e:
                print(f"LLM API Error on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    return {"error": f"LLM query failed after {max_retries} attempts", "details": str(e)}
                time.sleep(1)

        return {"error": "Failed to generate valid JSON response"}

    def assess_fun_factor(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to assess the fun factor based on structured analytics data.
        Returns a structured dictionary.
        """
        system_prompt = "You are an expert Game Design Analyst specialized in interpreting telemetry data."
        
        user_prompt = f"""
        TASK: Analyze the provided playtest data to quantify 'Fun Factor' and 'Engagement'.
        
        DATA:
        {json.dumps(structured_data, indent=2)}

        CONSTRAINTS:
        1. Output MUST be valid JSON.
        2. 'fun_score' must be an integer between 1 and 10.
        3. 'engagement_level' must be 'Low', 'Medium', or 'High'.
        
        REQUIRED JSON FORMAT:
        {{
            "fun_score": <int>,
            "engagement_level": "<str>",
            "justification": "<short summary>",
            "positive_factors": ["<str>", "<str>"],
            "negative_factors": ["<str>", "<str>"],
            "ux_issues": ["<str>"]
        }}
        """
        
        return self._query_llm_with_retry(system_prompt, user_prompt, expected_format="json")
    
    def suggest_improvements(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to suggest game improvements based on issues found.
        Returns a structured dictionary.
        """
        system_prompt = "You are a Senior Gameplay Engineer providing technical feedback."
        
        user_prompt = f"""
        TASK: Review the playtest data and suggest actionable improvements.
        
        DATA:
        {json.dumps(structured_data, indent=2)}
        
        CONSTRAINTS:
        1. Output MUST be valid JSON.
        2. Prioritize 'Critical' issues first.
        
        REQUIRED JSON FORMAT:
        {{
            "summary": "<str>",
            "critical_issues": [
                {{ "issue": "<str>", "fix": "<str>" }}
            ],
            "gameplay_tweaks": [
                {{ "suggestion": "<str>", "reasoning": "<str>" }}
            ],
            "retention_mechanics": ["<str>"]
        }}
        """
        
        return self._query_llm_with_retry(system_prompt, user_prompt, expected_format="json")
    
    def generate_narrative_report(self, analytics_data: Dict[str, Any]) -> str:
        """
        Generate a narrative report using LLM to explain the findings in story form.
        """
        system_prompt = "You are a creative Game Journalist writing a review based on AI bot experiences."
        
        user_prompt = f"""
        TASK: Convert the raw telemetry below into a compelling narrative story.
        
        DATA:
        {json.dumps(analytics_data, indent=2)}
        
        GUIDELINES:
        1. Write from the perspective of the AI agents.
        2. Highlight the 'emotional' highs (successes) and lows (deaths/retries).
        3. Keep it under 300 words.
        4. Use a witty, slightly cynical tone.
        """
        
        return self._query_llm_with_retry(system_prompt, user_prompt, expected_format="text")