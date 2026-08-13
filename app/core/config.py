import os
from typing import Optional, Dict, Any
import yaml
from pydantic_settings import BaseSettings

class ModelsConfig(BaseSettings):
    provider: str = "local"
    api_base: Optional[str] = "http://127.0.0.1:1235/v1"
    distillation_model: str = "qwen3.6-35b-a3b-mtp@iq2_m"
    execution_model: str = "qwen3.6-35b-a3b-mtp@iq2_m"

class DistillationConfig(BaseSettings):
    translate_to_english_for_reasoning: bool = True
    auto_detect_language: bool = True
    default_output_language: str = "ru"
    strict_constraint_preservation: bool = True
    token_savings_tracking: bool = True

class AudioConfig(BaseSettings):
    whisper_model: str = "base"
    local_whisper: bool = True

class Settings(BaseSettings):
    models: ModelsConfig = ModelsConfig()
    distillation: DistillationConfig = DistillationConfig()
    audio: AudioConfig = AudioConfig()

def load_settings(config_path: str) -> Settings:
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            yaml_data = yaml.safe_load(f) or {}
            
            # Convert YAML dicts to Pydantic objects if present
            models_data = yaml_data.get('models', {})
            dist_data = yaml_data.get('distillation', {})
            audio_data = yaml_data.get('audio', {})
            
            return Settings(
                models=ModelsConfig(**models_data),
                distillation=DistillationConfig(**dist_data),
                audio=AudioConfig(**audio_data)
            )
    return Settings()
