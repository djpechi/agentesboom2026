# /backend/app/services/openai_service.py

from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.openai_api_key)


async def chat_completion(
    messages: list[dict[str, str]],
    model: str = "gpt-4o",
    temperature: float = 0.7,
    max_tokens: int | None = None
) -> str:
    """
    Send a chat completion request to OpenAI

    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model to use (default: gpt-4o)
        temperature: Sampling temperature (0-2)
        max_tokens: Maximum tokens in response

    Returns:
        The assistant's response content
    """
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")
