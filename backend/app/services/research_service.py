# /backend/app/services/research_service.py

import json
from typing import Dict, Any, Optional
from app.services import perplexity_service, ai_provider_service
from app.config import get_settings

settings = get_settings()

async def research_company(company_name: str, website_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Research a company to get industry, products, LinkedIn, etc.
    Uses Perplexity if configured, otherwise falls back to OpenAI with general knowledge.
    """
    
    prompt = f"""
    Investiga la siguiente empresa y devuélveme un objeto JSON con su información clave:
    Nombre: {company_name}
    {f"URL: {website_url}" if website_url else ""}

    Necesito:
    1. industria (sector exacto, ej: "Transporte y Logística", "SaaS B2B", "E-commerce")
    2. productos_servicios (lista breve de lo que ofrecen)
    3. descripcion_corta (máximo 2 oraciones)
    4. publico_objetivo_estimado (quiénes son sus clientes principales)
    5. modelo_negocio (B2B, B2C, B2B2C, Marketplace, etc.)

    Devuelve ÚNICAMENTE el JSON sin texto adicional. Si no estás seguro de algo, haz tu mejor estimación basándote en el nombre y URL.
    """

    # Try Perplexity first (has real-time web search)
    has_perplexity = settings.perplexity_api_key and "your-perplexity" not in settings.perplexity_api_key
    
    if has_perplexity:
        try:
            response = await perplexity_service.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-sonar-large-128k-online"
            )
            result = _extract_json(response)
            if result:
                return result
        except Exception as e:
            print(f"Perplexity research failed: {str(e)}")

    # Fallback to OpenAI (uses training data, not real-time but knows major companies)
    try:
        response = await ai_provider_service.chat_completion(
            messages=[
                {"role": "system", "content": "Eres un experto en análisis de empresas. Responde SOLO con JSON válido."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        result = _extract_json(response)
        if result:
            return result
    except Exception as e:
        print(f"OpenAI research failed: {str(e)}")

    return {}


def _extract_json(text: str) -> Dict[str, Any]:
    """Extract JSON from potential AI response with extra text."""
    try:
        clean_text = text.strip()
        start_idx = clean_text.find('{')
        end_idx = clean_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            return json.loads(clean_text[start_idx:end_idx+1])
    except json.JSONDecodeError:
        pass
    return {}
