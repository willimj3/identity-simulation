"""
Claude API service for generating persona responses.
Uses the Anthropic SDK to call Claude with persona-specific system prompts.
"""

import os
import json
import asyncio
from anthropic import Anthropic
from typing import Optional

# Initialize client
client = Anthropic()

# Response format instructions
RESPONSE_FORMAT_INSTRUCTION = """
IMPORTANT: You must respond ONLY with valid JSON. No markdown, no code blocks, no explanations before or after.
Your entire response should be parseable JSON matching this exact structure:
{
  "receptivity_score": <integer 0-100>,
  "initial_reaction": "<string>",
  "emotional_response": "<string>",
  "moral_foundations_analysis": {
    "care_harm": "<string>",
    "fairness_cheating": "<string>",
    "loyalty_betrayal": "<string>",
    "authority_subversion": "<string>",
    "sanctity_degradation": "<string>",
    "liberty_oppression": "<string>"
  },
  "concerns": ["<string>", ...],
  "what_resonates": ["<string>", ...],
  "barriers_to_persuasion": ["<string>", ...],
  "trust_factors": "<string>",
  "suggested_reframings": ["<string>", ...],
  "identity_protective_reasoning": "<string>",
  "authentic_voice_response": "<string>"
}
"""


def build_user_prompt(message: str, context_type: str) -> str:
    """Build the user prompt with the message to analyze."""
    context_descriptions = {
        "tweet": "a tweet or social media post",
        "policy_brief": "a policy brief or white paper excerpt",
        "speech": "a speech or public address",
        "news_article": "a news article or headline",
        "campaign_ad": "a campaign advertisement or political ad",
        "general": "a political message"
    }

    context_desc = context_descriptions.get(context_type, "a political message")

    return f"""Analyze the following {context_desc} and provide your authentic reaction from your political perspective.

MESSAGE TO ANALYZE:
\"\"\"
{message}
\"\"\"

{RESPONSE_FORMAT_INSTRUCTION}"""


async def generate_persona_response(
    persona_config: dict,
    message: str,
    context_type: str = "general"
) -> dict:
    """
    Generate a response from a specific persona.

    Args:
        persona_config: The persona configuration dict with system_prompt
        message: The message to analyze
        context_type: The context type (tweet, policy_brief, etc.)

    Returns:
        Parsed response dict
    """
    system_prompt = persona_config["system_prompt"]
    user_prompt = build_user_prompt(message, context_type)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        # Extract text content
        response_text = response.content[0].text.strip()

        # Try to parse JSON
        # Handle potential markdown code blocks
        if response_text.startswith("```"):
            # Extract content between code blocks
            lines = response_text.split("\n")
            json_lines = []
            in_block = False
            for line in lines:
                if line.startswith("```"):
                    in_block = not in_block
                    continue
                if in_block or not line.startswith("```"):
                    json_lines.append(line)
            response_text = "\n".join(json_lines)

        parsed_response = json.loads(response_text)
        return parsed_response

    except json.JSONDecodeError as e:
        # Return a structured error response
        return {
            "receptivity_score": 50,
            "initial_reaction": "Error parsing response",
            "emotional_response": f"JSON parsing error: {str(e)}",
            "moral_foundations_analysis": {
                "care_harm": "Unable to analyze",
                "fairness_cheating": "Unable to analyze",
                "loyalty_betrayal": "Unable to analyze",
                "authority_subversion": "Unable to analyze",
                "sanctity_degradation": "Unable to analyze",
                "liberty_oppression": "Unable to analyze"
            },
            "concerns": ["Response parsing failed"],
            "what_resonates": [],
            "barriers_to_persuasion": ["Technical error"],
            "trust_factors": "Unable to assess",
            "suggested_reframings": [],
            "identity_protective_reasoning": "Unable to analyze",
            "authentic_voice_response": f"Raw response: {response_text[:500]}..."
        }
    except Exception as e:
        return {
            "receptivity_score": 50,
            "initial_reaction": f"Error: {str(e)}",
            "emotional_response": "API error occurred",
            "moral_foundations_analysis": {
                "care_harm": "Unable to analyze",
                "fairness_cheating": "Unable to analyze",
                "loyalty_betrayal": "Unable to analyze",
                "authority_subversion": "Unable to analyze",
                "sanctity_degradation": "Unable to analyze",
                "liberty_oppression": "Unable to analyze"
            },
            "concerns": [f"API error: {str(e)}"],
            "what_resonates": [],
            "barriers_to_persuasion": ["Technical error"],
            "trust_factors": "Unable to assess",
            "suggested_reframings": [],
            "identity_protective_reasoning": "Unable to analyze",
            "authentic_voice_response": "An error occurred while generating the response."
        }


async def generate_all_persona_responses(
    personas: dict,
    selected_persona_names: list[str],
    message: str,
    context_type: str = "general"
) -> dict[str, dict]:
    """
    Generate responses from multiple personas in parallel.

    Args:
        personas: Dict of all available persona configs
        selected_persona_names: List of persona names to generate responses for
        message: The message to analyze
        context_type: The context type

    Returns:
        Dict mapping persona names to their responses
    """
    # Create tasks for parallel execution
    tasks = {}
    for name in selected_persona_names:
        if name in personas:
            tasks[name] = generate_persona_response(
                personas[name],
                message,
                context_type
            )

    # Execute all tasks concurrently
    results = {}
    if tasks:
        responses = await asyncio.gather(*tasks.values())
        for name, response in zip(tasks.keys(), responses):
            results[name] = response

    return results
