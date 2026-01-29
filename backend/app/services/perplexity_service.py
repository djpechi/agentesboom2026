# /backend/app/services/perplexity_service.py

import httpx
from app.config import get_settings

settings = get_settings()

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


async def chat_completion(
    messages: list[dict[str, str]],
    model: str = "llama-3.1-sonar-small-128k-online",
    temperature: float = 0.7
) -> str:
    """
    Send a chat completion request to Perplexity AI

    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model to use (default: llama-3.1-sonar-small-128k-online)
        temperature: Sampling temperature (0-2)

    Returns:
        The assistant's response content
    """
    if not settings.perplexity_api_key:
        raise Exception("Perplexity API key not configured")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                PERPLEXITY_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.perplexity_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature
                },
                timeout=60.0
            )

            response.raise_for_status()
            data = response.json()

            return data["choices"][0]["message"]["content"]

    except httpx.HTTPError as e:
        raise Exception(f"Perplexity API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error calling Perplexity: {str(e)}")
