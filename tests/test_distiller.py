import pytest
from app.core.distiller import parse_llm_json, PromptDistiller
from app.core.config import Settings, ModelsConfig

def test_parse_llm_json():
    # Test valid JSON parsing
    raw = '```json\n{"key": "value"}\n```'
    assert parse_llm_json(raw) == {"key": "value"}
    
    # Test valid JSON without code block
    raw2 = '{"key2": "value2"}'
    assert parse_llm_json(raw2) == {"key2": "value2"}

def test_estimate_tokens():
    settings = Settings(models=ModelsConfig(distillation_model="test-model", execution_model="test-model"))
    distiller = PromptDistiller(settings)
    
    # Tiktoken is expected to be used
    tokens = distiller.estimate_tokens("Hello world this is a test.")
    assert tokens > 0

@pytest.mark.asyncio
async def test_distiller_config():
    settings = Settings(models=ModelsConfig(distillation_model="custom-distill-model", execution_model="custom-exec-model"))
    distiller = PromptDistiller(settings)
    assert distiller.default_distill_model == "custom-distill-model"
    assert distiller.default_exec_model == "custom-exec-model"
