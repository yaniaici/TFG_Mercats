import os
import httpx
from typing import Optional
import structlog

logger = structlog.get_logger()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:0.5b-instruct")


async def generate_text(prompt: str, system: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 256) -> str:
    """
    Llama/Ollama simple text generation.
    Falls back to default model if env not provided.
    """
    try:
        payload = {
            "model": LLM_MODEL,
            "prompt": f"<SYSTEM>\n{system}\n</SYSTEM>\n\n{prompt}" if system else prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{OLLAMA_HOST}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")
    except Exception as e:
        logger.warning("Ollama not available, using fallback response", error=str(e))
        # Fallback simple responses based on the prompt
        if "preferencias" in prompt.lower() or "preferences" in prompt.lower():
            return '{"diet": "omnivoro", "organic": false, "budget_level": "medium"}'
        elif "copy" in prompt.lower() or "mensaje" in prompt.lower():
            return "Descubre nuestras ofertas especiales esta semana en el mercat!"
        else:
            return "Respuesta generada automáticamente."


