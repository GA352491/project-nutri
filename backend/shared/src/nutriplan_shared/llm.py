"""
NutriPlan Unified LLM Client Wrapper (Powered by LiteLLM)
=========================================================
Centralizes all LLM calls across NutriPlan microservices.
Supports:
- Local Ollama (default: ollama/llama3.2:latest at http://localhost:11434)
- Seamless switching to Cloud providers (OpenAI, Anthropic, Gemini, DeepSeek)
- Automatic fallback handling
- JSON schema structured output
"""
import os
import logging
from typing import List, Dict, Any, Optional
import litellm
from litellm import acompletion, completion

from nutriplan_shared.service_registry import OLLAMA_URL

# Silence verbose litellm telemetry and debug logs in microservices
litellm.telemetry = False
litellm.suppress_debug_info = True

logger = logging.getLogger("nutriplan_shared.llm")

DEFAULT_MODEL = os.getenv("DEFAULT_LLM_MODEL", "ollama/llama3.2:latest")


def normalize_model_name(model: Optional[str]) -> str:
    """Ensure Ollama models have the 'ollama/' prefix for LiteLLM routing."""
    target = (model or DEFAULT_MODEL).strip()
    # If caller specifies standard ollama names like 'llama3' or 'llama3.2:latest' without prefix
    if not (target.startswith("ollama/") or 
            target.startswith("openai/") or 
            target.startswith("anthropic/") or 
            target.startswith("gemini/") or 
            target.startswith("deepseek/") or
            target.startswith("groq/")):
        # Default local engine is ollama
        target = f"ollama/{target}"
    return target


async def llm_chat(
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: Optional[int] = None,
    response_format: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0,
    api_base: Optional[str] = None,
    **kwargs
) -> str:
    """
    Execute asynchronous chat completion using LiteLLM.
    Automatically injects local Ollama api_base when target model is Ollama-based.
    """
    target_model = normalize_model_name(model)
    extra_kwargs: Dict[str, Any] = {**kwargs}

    if target_model.startswith("ollama/"):
        extra_kwargs["api_base"] = api_base or OLLAMA_URL

    if response_format:
        extra_kwargs["response_format"] = response_format

    if max_tokens:
        extra_kwargs["max_tokens"] = max_tokens

    response = await acompletion(
        model=target_model,
        messages=messages,
        temperature=temperature,
        timeout=timeout,
        **extra_kwargs
    )
    return response.choices[0].message.content or ""


async def llm_generate(
    prompt: str,
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: Optional[int] = None,
    response_format: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0,
    api_base: Optional[str] = None,
    **kwargs
) -> str:
    """Convenience helper for single prompt generation."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    return await llm_chat(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format=response_format,
        timeout=timeout,
        api_base=api_base,
        **kwargs
    )
