import os
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("prompt_distiller.models")

# 2026 Model Registry with cloud providers and universal local inference engines
MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "gemini": {
        "name": "Google Gemini",
        "free_tier": True,
        "requires_api_key": True,
        "key_url": "https://aistudio.google.com/app/apikey",
        "distillation_default": "gemini/gemini-3.6-flash",
        "execution_default": "gemini/gemini-3.6-flash",
        "models": [
            {"id": "gemini/gemini-3.6-flash", "label": "Gemini 3.6 Flash (Fast / Free)", "recommended_for": "distillation"},
            {"id": "gemini/gemini-3.1-pro", "label": "Gemini 3.1 Pro (Heavy Reasoning)", "recommended_for": "execution"},
            {"id": "gemini/gemini-3.5-flash", "label": "Gemini 3.5 Flash", "recommended_for": "distillation"}
        ]
    },
    "groq": {
        "name": "Groq Cloud",
        "free_tier": True,
        "requires_api_key": True,
        "key_url": "https://console.groq.com/keys",
        "distillation_default": "groq/llama-3.1-8b-instant",
        "execution_default": "groq/llama-3.3-70b-versatile",
        "models": [
            {"id": "groq/llama-3.1-8b-instant", "label": "Llama 3.1 8B Instant (Ultra-Fast)", "recommended_for": "distillation"},
            {"id": "groq/llama-3.3-70b-versatile", "label": "Llama 3.3 70B Versatile (Free Reasoning)", "recommended_for": "execution"},
            {"id": "groq/qwen-2.5-32b", "label": "Qwen 2.5 32B (Groq Free)", "recommended_for": "execution"}
        ]
    },
    "openai": {
        "name": "OpenAI",
        "free_tier": False,
        "requires_api_key": True,
        "key_url": "https://platform.openai.com/api-keys",
        "distillation_default": "gpt-4o-mini",
        "execution_default": "gpt-4o",
        "models": [
            {"id": "gpt-4o-mini", "label": "GPT-4o Mini (Fast)", "recommended_for": "distillation"},
            {"id": "gpt-5.6-luna", "label": "GPT-5.6 Luna (Fast 2026)", "recommended_for": "distillation"},
            {"id": "gpt-4o", "label": "GPT-4o (Reasoning)", "recommended_for": "execution"},
            {"id": "gpt-5.6-sol", "label": "GPT-5.6 Sol (Frontier Reasoning)", "recommended_for": "execution"},
            {"id": "o3-mini", "label": "o3-mini (Reasoning)", "recommended_for": "execution"}
        ]
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "free_tier": False,
        "requires_api_key": True,
        "key_url": "https://console.anthropic.com/",
        "distillation_default": "claude-3-5-haiku-20241022",
        "execution_default": "claude-3-5-sonnet-20241022",
        "models": [
            {"id": "claude-3-5-haiku-20241022", "label": "Claude 3.5 Haiku", "recommended_for": "distillation"},
            {"id": "claude-sonnet-5", "label": "Claude Sonnet 5 (2026)", "recommended_for": "distillation"},
            {"id": "claude-3-5-sonnet-20241022", "label": "Claude 3.5 Sonnet", "recommended_for": "execution"},
            {"id": "claude-opus-5", "label": "Claude Opus 5 (Frontier)", "recommended_for": "execution"}
        ]
    },
    "deepseek": {
        "name": "DeepSeek / OpenRouter",
        "free_tier": False,
        "requires_api_key": True,
        "key_url": "https://openrouter.ai/keys",
        "distillation_default": "openrouter/deepseek/deepseek-v4-flash",
        "execution_default": "openrouter/deepseek/deepseek-r1",
        "models": [
            {"id": "openrouter/deepseek/deepseek-v4-flash", "label": "DeepSeek V4 Flash", "recommended_for": "distillation"},
            {"id": "openrouter/deepseek/deepseek-v4-pro", "label": "DeepSeek V4 Pro", "recommended_for": "execution"},
            {"id": "openrouter/deepseek/deepseek-r1", "label": "DeepSeek R1 (Reasoning)", "recommended_for": "execution"}
        ]
    },
    "llamacpp": {
        "name": "llama.cpp Server",
        "free_tier": True,
        "requires_api_key": False,
        "default_api_base": "http://127.0.0.1:8080/v1",
        "distillation_default": "openai/local-model",
        "execution_default": "openai/local-model",
        "models": [
            {"id": "openai/local-model", "label": "llama-server Local Model", "recommended_for": "distillation & execution"}
        ]
    },
    "vllm": {
        "name": "vLLM GPU Server",
        "free_tier": True,
        "requires_api_key": False,
        "default_api_base": "http://127.0.0.1:8000/v1",
        "distillation_default": "openai/vllm-model",
        "execution_default": "openai/vllm-model",
        "models": [
            {"id": "openai/vllm-model", "label": "vLLM Serving Endpoint", "recommended_for": "distillation & execution"}
        ]
    },
    "lmstudio": {
        "name": "Mac / LM Studio / Jan.ai",
        "free_tier": True,
        "requires_api_key": False,
        "default_api_base": "http://127.0.0.1:1234/v1",
        "distillation_default": "openai/local-model",
        "execution_default": "openai/local-model",
        "models": [
            {"id": "openai/local-model", "label": "LM Studio Local Endpoint", "recommended_for": "distillation & execution"}
        ]
    },
    "ollama": {
        "name": "Local Ollama",
        "free_tier": True,
        "requires_api_key": False,
        "default_api_base": "http://127.0.0.1:11434",
        "distillation_default": "ollama/qwen2.5:1.5b",
        "execution_default": "ollama/qwen2.5:1.5b",
        "models": [
            {"id": "ollama/qwen2.5:1.5b", "label": "Qwen 2.5 1.5B (~1GB RAM)", "recommended_for": "distillation"},
            {"id": "ollama/llama3.2:1b", "label": "Llama 3.2 1B (~800MB RAM)", "recommended_for": "distillation"},
            {"id": "ollama/qwen2.5:32b", "label": "Qwen 2.5 32B (Heavy Local)", "recommended_for": "execution"}
        ]
    },
    "custom_local": {
        "name": "Custom OpenAI-Compatible Local Endpoint",
        "free_tier": True,
        "requires_api_key": False,
        "default_api_base": "http://127.0.0.1:8080/v1",
        "distillation_default": "openai/custom-model",
        "execution_default": "openai/custom-model",
        "models": [
            {"id": "openai/custom-model", "label": "Custom Local Model", "recommended_for": "distillation & execution"}
        ]
    }
}

def get_model_registry() -> Dict[str, Any]:
    return MODEL_REGISTRY

class LLMClient:
    """
    Provider-agnostic LLM Client wrapper with support for dynamic API keys,
    custom local API bases (llama.cpp, vLLM, LM Studio, Ollama), and heuristic fallback.
    """

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        provider: Optional[str] = None,
        api_base: Optional[str] = None
    ):
        self.model_name = model_name
        self.provider = provider
        self.api_base = api_base
        self.api_key = (
            api_key 
            or os.getenv("GEMINI_API_KEY") 
            or os.getenv("GROQ_API_KEY") 
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("ANTHROPIC_API_KEY")
        )

    async def generate(self, system_prompt: str, user_prompt: str, response_format: Optional[str] = None) -> str:
        """
        Executes an LLM generation call using LiteLLM or heuristic fallback.
        """
        try:
            import litellm
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            kwargs: Dict[str, Any] = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 1.0
            }
            
            if self.api_key:
                kwargs["api_key"] = self.api_key
            elif self.api_base or (self.provider and self.provider in ["llamacpp", "vllm", "lmstudio", "custom_local"]):
                kwargs["api_key"] = "sk-no-key-required"

            if self.api_base:
                kwargs["api_base"] = self.api_base

            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}

            response = await litellm.acompletion(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(
                f"LiteLLM call failed or unconfigured for model '{self.model_name}' "
                f"(api_base='{self.api_base}') ({e}). Falling back to heuristic engine."
            )
            return self._heuristic_fallback(system_prompt, user_prompt, response_format)

    def _heuristic_fallback(self, system_prompt: str, user_prompt: str, response_format: Optional[str]) -> str:
        """
        Built-in heuristic processor for standalone operation when external LLM APIs are not connected.
        """
        if "JSON" in system_prompt or response_format == "json":
            return json.dumps({
                "detected_language": "Russian (ru)",
                "raw_input_summary": f"User query: '{user_prompt[:80]}...'",
                "distilled_prompt": f"Address core request efficiently: {user_prompt[:120]}",
                "intent": "general_inquiry",
                "extracted_constraints": ["Concise output required"],
                "estimated_raw_tokens": len(user_prompt.split()) * 2,
                "estimated_distilled_tokens": int(len(user_prompt.split()) * 0.8),
                "token_savings_percent": 60.0
            }, indent=2)
        
        return (
            "**Ответ по вашему запросу (Автономный режим):**\n\n"
            f"Запрос обработан: {user_prompt}\n\n"
            "1. Основная задача проанализирована.\n"
            "2. Для подключения внешних языковых моделей или локальных серверов (llama.cpp / vLLM) введите настройки в окне Settings."
        )
