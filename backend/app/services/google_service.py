# /backend/app/services/google_service.py

import google.generativeai as genai
from app.config import get_settings
from typing import List, Dict, Any

settings = get_settings()

if settings.google_ai_api_key:
    genai.configure(api_key=settings.google_ai_api_key)

async def chat_completion(
    messages: List[Dict[str, str]],
    model: str = "gemini-2.0-flash",
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> str:
    """
    Send a chat completion request to Google Gemini
    """
    try:
        # Convert OpenAI format messages to Gemini format
        # Gemini uses 'user' and 'model' instead of 'user' and 'assistant'
        # Also handles 'system' as a separate parameter in GenerativeModel
        
        system_instruction = ""
        gemini_history = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                gemini_history.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                gemini_history.append({"role": "model", "parts": [msg["content"]]})
        
        # Last message is always the current user prompt
        last_message = gemini_history.pop() if gemini_history and gemini_history[-1]["role"] == "user" else None
        
        model_instance = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_instruction
        )
        
        chat = model_instance.start_chat(history=gemini_history)
        
        # If there's no history or the last message was assistant, this shouldn't happen in a normal chat
        # but for robustness:
        prompt = last_message["parts"][0] if last_message else "Continue"
        
        response = chat.send_message(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
        
        return response.text

    except Exception as e:
        raise Exception(f"Google Gemini API error: {str(e)}")
