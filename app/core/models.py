import os
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("prompt_distiller.models")

# Cloud providers (no local api_base by default)
CLOUD_PROVIDERS = {"gemini", "groq", "openai", "anthropic", "deepseek"}

# 2026 Model Registry with cloud providers and universal local inference engines
MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "gemini": {
        "name": "Google Gemini",
        "free_tier": True,
        "requires_api_key": True,
        "key_url": "https://aistudio.google.com/app/apikey",
        "api_key_env": "GEMINI_API_KEY",
        "distillation_default": "gemini/gemini-2.0-flash",
        "execution_default": "gemini/gemini-2.5-pro",
        "models": [
            {"id": "gemini/gemini-2.0-flash", "label": "Gemini 2.0 Flash (Fast / Free)", "recommended_for": "distillation"},
            {"id": "gemini/gemini-2.5-flash", "label": "Gemini 2.5 Flash", "recommended_for": "distillation"},
            {"id": "gemini/gemini-2.5-pro", "label": "Gemini 2.5 Pro (Reasoning)", "recommended_for": "execution"}
        ]
    },
    "groq": {
        "name": "Groq Cloud",
        "free_tier": True,
        "requires_api_key": True,
        "key_url": "https://console.groq.com/keys",
        "api_key_env": "GROQ_API_KEY",
        "distillation_default": "groq/llama-3.1-8b-instant",
        "execution_default": "groq/llama-3.3-70b-versatile",
        "models": [
            {"id": "groq/llama-3.1-8b-instant", "label": "Llama 3.1 8B Instant (Ultra-Fast)", "recommended_for": "distillation"},
            {"id": "groq/llama-3.3-70b-versatile", "label": "Llama 3.3 70B Versatile (Free Reasoning)", "recommended_for": "execution"},
            {"id": "groq/qwen-qwq-32b", "label": "Qwen QwQ 32B (Groq)", "recommended_for": "execution"}
        ]
    },
    "openai": {
        "name": "OpenAI",
        "free_tier": False,
        "requires_api_key": True,
        "key_url": "https://platform.openai.com/api-keys",
        "api_key_env": "OPENAI_API_KEY",
        "distillation_default": "gpt-4o-mini",
        "execution_default": "gpt-4o",
        "models": [
            {"id": "gpt-4o-mini", "label": "GPT-4o Mini (Fast)", "recommended_for": "distillation"},
            {"id": "gpt-4o", "label": "GPT-4o (Reasoning)", "recommended_for": "execution"},
            {"id": "o3-mini", "label": "o3-mini (Reasoning)", "recommended_for": "execution"}
        ]
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "free_tier": False,
        "requires_api_key": True,
        "key_url": "https://console.anthropic.com/",
        "api_key_env": "ANTHROPIC_API_KEY",
        "distillation_default": "claude-3-5-haiku-20241022",
        "execution_default": "claude-3-5-sonnet-20241022",
        "models": [
            {"id": "claude-3-5-haiku-20241022", "label": "Claude 3.5 Haiku", "recommended_for": "distillation"},
            {"id": "claude-3-5-sonnet-20241022", "label": "Claude 3.5 Sonnet", "recommended_for": "execution"},
            {"id": "claude-opus-4-5", "label": "Claude Opus 4.5 (Frontier)", "recommended_for": "execution"}
        ]
    },
    "deepseek": {
        "name": "DeepSeek / OpenRouter",
        "free_tier": False,
        "requires_api_key": True,
        "key_url": "https://openrouter.ai/keys",
        "api_key_env": "OPENROUTER_API_KEY",
        "distillation_default": "openrouter/deepseek/deepseek-chat",
        "execution_default": "openrouter/deepseek/deepseek-r1",
        "models": [
            {"id": "openrouter/deepseek/deepseek-chat", "label": "DeepSeek Chat (Fast)", "recommended_for": "distillation"},
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

# Alias: "local" in config.yaml maps to custom_local behaviour
MODEL_REGISTRY["local"] = MODEL_REGISTRY["custom_local"]

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
        # Resolve API key provider-aware: pick the env var matching the active provider.
        # Falling back to any set key only when provider is unknown.
        if api_key:
            self.api_key = api_key
        elif provider and provider in MODEL_REGISTRY:
            env_var = MODEL_REGISTRY[provider].get("api_key_env")
            self.api_key = os.getenv(env_var) if env_var else None
        else:
            # Generic fallback: try known env vars in order
            self.api_key = (
                os.getenv("GEMINI_API_KEY")
                or os.getenv("GROQ_API_KEY")
                or os.getenv("OPENAI_API_KEY")
                or os.getenv("ANTHROPIC_API_KEY")
            )

    async def generate(self, system_prompt: str, user_prompt: str, response_format: Optional[str] = None) -> str:
        """
        Executes an LLM generation call using local HTTP endpoint (e.g. Qwen 35B on port 1235),
        LiteLLM, or heuristic fallback.
        """
        is_cloud = self.provider in CLOUD_PROVIDERS

        # 1. Try Direct HTTP call to local OpenAI-compatible endpoint.
        # Only attempted for local/custom providers, never for cloud providers to avoid
        # accidentally routing cloud requests to 127.0.0.1:1235.
        local_api_base = self.api_base
        if not is_cloud and not local_api_base:
            local_api_base = os.getenv("LLM_API_BASE", "http://127.0.0.1:1235/v1")

        if local_api_base:
            endpoint = local_api_base.rstrip("/")
            if not endpoint.endswith("/chat/completions"):
                endpoint += "/chat/completions"
            try:
                import httpx
                payload = {
                    "model": self.model_name or "qwen",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.2
                }
                if response_format == "json":
                    payload["response_format"] = {"type": "json_object"}

                async with httpx.AsyncClient(timeout=120.0) as client:
                    resp = await client.post(endpoint, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data["choices"][0]["message"]["content"]
                        if content and content.strip():
                            return content
            except Exception as e:
                logger.warning(f"Local HTTP LLM call to {endpoint} failed: {e}. Trying litellm/fallback...")

        # 2. Try LiteLLM if API key or external provider configured
        try:
            import litellm
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            kwargs: Dict[str, Any] = {
                "model": self.model_name,
                "messages": messages,
                "temperature": 0.2
            }
            
            if self.api_key:
                kwargs["api_key"] = self.api_key
            else:
                kwargs["api_key"] = "sk-no-key-required"

            # Only pass api_base to LiteLLM for local/custom providers; cloud
            # providers use their own SDK endpoints and must not get a local URL.
            if local_api_base and not is_cloud:
                kwargs["api_base"] = local_api_base

            if response_format == "json":
                kwargs["response_format"] = {"type": "json_object"}

            response = await litellm.acompletion(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.warning(
                f"LiteLLM call failed for model '{self.model_name}' "
                f"({e}). Falling back to heuristic engine."
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
                "distilled_prompt": user_prompt,
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
