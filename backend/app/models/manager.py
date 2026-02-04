from typing import Dict, List, Optional
from app.models.base import BaseOCRModel
from app.models.ollama_adapter import OllamaAdapter

class ModelManager:
    def __init__(self):
        self._models: Dict[str, BaseOCRModel] = {}
        self._active_model_name: Optional[str] = None
        
        # Register default models
        self.register_model(OllamaAdapter("deepseek-ocr:latest")) 
        self.register_model(OllamaAdapter("qwen3-vl:8b"))
        self._active_model_name = "deepseek-ocr:latest" # Set default active model
        # self.register_model(OllamaAdapter("llama3.2:3b")) # Text only, but good for testing

    def register_model(self, model: BaseOCRModel):
        self._models[model.model_name] = model

    def list_models(self) -> List[Dict[str, str]]:
        return [
            {"name": name, "provider": model.provider, "active": name == self._active_model_name}
            for name, model in self._models.items()
        ]

    async def get_model(self, model_name: str) -> BaseOCRModel:
        if model_name not in self._models:
            # Try to dynamic register if it's an ollama model that might exist
            # For now, just error out or default to ollama adapter if we want dynamic
            raise ValueError(f"Model {model_name} not found")
        
        return self._models[model_name]

    async def set_active_model(self, model_name: str):
        if model_name not in self._models:
             # Auto-register if it looks like a valid model name for our providers?
             # For now, strict registry
             raise ValueError(f"Model {model_name} not registered")
        
        self._active_model_name = model_name
        # Ideally, we load here or lazy load

manager = ModelManager()
