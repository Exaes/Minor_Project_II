"""
LLM-based recommendation generator.

Uses the Hugging Face Inference API to generate recommendations
from structured prompts. Falls back to the rule-based generator
if no API token is available or the API call fails.
"""

import os
import sys
import json
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config import HF_API_TOKEN, LLM_MODEL

from .prompt_templates import build_recommendation_prompt
from .fallback_generator import generate_fallback_recommendations


HF_API_URL = f"https://api-inference.huggingface.co/models/{LLM_MODEL}"


def generate_recommendations(
    startup_data: dict,
    scoring_result: dict,
    num_recommendations: int = 5,
    use_llm: bool = True,
) -> list[dict]:
    """
    Generate prioritized recommendations for a target startup.

    Tries LLM first (if API token available), falls back to rule-based.

    Args:
        startup_data: Original startup data dict.
        scoring_result: Output from scorer.score_startup().
        num_recommendations: Number of recommendations.
        use_llm: Whether to attempt LLM generation.

    Returns:
        List of recommendation dicts, each with:
        {rank, title, category, impact_level, explanation, supporting_data}
    """
    # Try LLM if token is available
    if use_llm and HF_API_TOKEN:
        try:
            recommendations = _call_llm(startup_data, scoring_result, num_recommendations)
            if recommendations and len(recommendations) > 0:
                return recommendations
        except Exception as e:
            print(f"LLM generation failed: {e}. Falling back to rule-based.")

    # Fallback to rule-based generator
    return generate_fallback_recommendations(
        startup_data, scoring_result, num_recommendations
    )


def _call_llm(
    startup_data: dict,
    scoring_result: dict,
    num_recommendations: int,
) -> list[dict]:
    """
    Call the Hugging Face Inference API to generate recommendations.
    """
    system_prompt, user_prompt = build_recommendation_prompt(
        startup_data, scoring_result, num_recommendations
    )

    # Format for instruct models
    full_prompt = f"<s>[INST] {system_prompt}\n\n{user_prompt} [/INST]"

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "inputs": full_prompt,
        "parameters": {
            "max_new_tokens": 2000,
            "temperature": 0.3,
            "top_p": 0.9,
            "return_full_text": False,
        },
    }

    response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        raise RuntimeError(f"HF API returned {response.status_code}: {response.text}")

    result = response.json()

    # Parse generated text
    if isinstance(result, list) and len(result) > 0:
        generated_text = result[0].get("generated_text", "")
    else:
        raise RuntimeError(f"Unexpected API response format: {result}")

    # Extract JSON from response
    recommendations = _parse_json_response(generated_text)

    return recommendations


def _parse_json_response(text: str) -> list[dict]:
    """
    Extract and parse JSON array from LLM response text.
    Handles cases where the model wraps JSON in markdown code blocks.
    """
    # Try direct parse
    text = text.strip()

    # Remove markdown code blocks if present
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    # Find JSON array
    start_idx = text.find("[")
    end_idx = text.rfind("]")

    if start_idx == -1 or end_idx == -1:
        raise ValueError(f"No JSON array found in response: {text[:200]}")

    json_text = text[start_idx:end_idx + 1]
    recommendations = json.loads(json_text)

    # Validate structure
    validated = []
    for rec in recommendations:
        validated.append({
            "rank": rec.get("rank", len(validated) + 1),
            "title": rec.get("title", "Recommendation"),
            "category": rec.get("category", "General"),
            "impact_level": rec.get("impact_level", "Medium"),
            "explanation": rec.get("explanation", ""),
            "supporting_data": rec.get("supporting_data", {}),
        })

    return validated
