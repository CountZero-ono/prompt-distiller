import os
import yaml
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.core.distiller import PromptDistiller
from app.core.audio import AudioTranscriber

# Logging Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("prompt_distiller")

# Load Configuration
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)
else:
    config = {}

app = FastAPI(
    title="Prompt Distiller & Gateway API",
    description="Model-agnostic prompt distillation and noise reduction engine.",
    version="1.0.0"
)

distiller = PromptDistiller(config)
transcriber = AudioTranscriber()

# Mount Static Files
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class ProcessRequest(BaseModel):
    raw_prompt: str
    target_language: Optional[str] = "ru"
    model: Optional[str] = None

@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/v1/health")
async def health_check():
    return {"status": "ok", "engine": "PromptDistiller v1.0.0"}

@app.post("/v1/process")
async def process_prompt(req: ProcessRequest):
    if not req.raw_prompt.strip():
        raise HTTPException(status_code=400, detail="raw_prompt cannot be empty")
    
    logger.info(f"Processing prompt request (len: {len(req.raw_prompt)})")
    result = await distiller.process(req.raw_prompt, target_language=req.target_language)
    return result

@app.post("/v1/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as buffer:
        buffer.write(await file.read())
    
    transcript = transcriber.transcribe(temp_path)
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    return {"text": transcript}

if __name__ == "__main__":
    import uvicorn
    host = config.get("server", {}).get("host", "0.0.0.0")
    port = config.get("server", {}).get("port", 8000)
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
