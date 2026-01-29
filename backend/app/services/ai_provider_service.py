# /backend/app/services/ai_provider_service.py

from app.services import openai_service, google_service
from app.config import get_settings
from typing import List, Dict, Any

settings = get_settings()

async def chat_completion(
    messages: List[Dict[str, str]],
    model_override: str = None,
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> str:
    # Check for valid keys
    has_gemini = settings.google_ai_api_key and "your-google" not in settings.google_ai_api_key
    has_openai = settings.openai_api_key and "your-openai" not in settings.openai_api_key
    
    # Determine which provider to use
    use_gemini = False
    
    if model_override:
        model_lower = model_override.lower()
        if "gemini" in model_lower or "google" in model_lower:
            if has_gemini:
                use_gemini = True
            elif has_openai:
                use_gemini = False  # Fallback to OpenAI if Gemini requested but key missing
            else:
                raise Exception("Gemini requested but no Google API key configured")
        elif "gpt" in model_lower or "openai" in model_lower:
            if has_openai:
                use_gemini = False
            elif has_gemini:
                use_gemini = True   # Fallback to Gemini if OpenAI requested but key missing
            else:
                raise Exception("OpenAI requested but no OpenAI API key configured")
    else:
        # No override: Default to Gemini if available, otherwise OpenAI
        use_gemini = has_gemini

    # Final decision based on availability with model name sanitization
    if use_gemini and has_gemini:
        # Sanitize gemini model name
        target_model = "gemini-2.0-flash"
        if model_override:
            if "gemini-2.0" in model_override: target_model = "gemini-2.0-flash"
            elif "gemini-1.5-pro" in model_override: target_model = "gemini-1.5-pro"
            elif "gemini-1.5-flash" in model_override: target_model = "gemini-1.5-flash"
            
        return await google_service.chat_completion(
            messages=messages,
            model=target_model,
            temperature=temperature,
            max_tokens=max_tokens
        )
    elif has_openai:
        # Sanitize openai model name (remove prefixes like 'openai-')
        target_model = "gpt-4o"
        if model_override:
            clean_model = model_override.lower().replace("openai-", "")
            if clean_model.startswith("gpt-"):
                target_model = clean_model
            elif "o1" in clean_model:
                target_model = "o1-preview"
                
        return await openai_service.chat_completion(
            messages=messages,
            model=target_model,
            temperature=temperature,
            max_tokens=max_tokens
        )
    else:
        raise Exception("No AI provider configured (missing API keys)")
