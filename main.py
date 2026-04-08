import os
import json
import uuid
import logging
import uvicorn
import services
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("kayakflow")

app = FastAPI(
    title="KayakFlow AI",
    description="AI-powered marketing automation for Berlin Kayak Tours",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── History (JSON file) ───────────────────────────────────────────────────────
HISTORY_FILE = "history.json"

def _load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def _save_history(items: list):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(items[-50:], f, ensure_ascii=False, indent=2)

def _push_history(entry: dict):
    h = _load_history()
    h.append(entry)
    _save_history(h)

# ── Startup ───────────────────────────────────────────────────────────────────
logger.info("=== KayakFlow AI v3 Starting ===")
logger.info("✅ Groq ready" if os.getenv("GROQ_API_KEY") else "❌ GROQ_API_KEY missing!")

# ── Schemas ───────────────────────────────────────────────────────────────────
class ContentRequest(BaseModel):
    user_input: str
    context: Optional[str] = ""
    tone: Optional[str] = "adventurous"
    language: Optional[str] = "auto"
    platforms: Optional[List[str]] = ["instagram", "whatsapp"]

class BulkRequest(BaseModel):
    user_input: str
    tone: Optional[str] = "adventurous"
    language: Optional[str] = "auto"

# ── Static files ──────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def serve_ui():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    raise HTTPException(404, "index.html not found")

@app.get("/latest_promo.png", include_in_schema=False)
async def serve_image():
    if os.path.exists("latest_promo.png"):
        return FileResponse("latest_promo.png", media_type="image/png")
    raise HTTPException(404, "No image generated yet")

# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["ops"])
async def health():
    return {
        "status": "ok",
        "version": "3.0.0",
        "groq": bool(os.getenv("GROQ_API_KEY")),
        "ts": datetime.now(timezone.utc).isoformat(),
    }

# ── Legacy endpoint (keeps backward compat) ───────────────────────────────────
@app.post("/generate-content", include_in_schema=False)
async def generate_content_legacy(request: ContentRequest):
    return await generate_content(request)

# ── v1 API ────────────────────────────────────────────────────────────────────
@app.post("/api/v1/generate", tags=["content"])
async def generate_content(request: ContentRequest):
    logger.info(f"Generate | tone={request.tone} | platforms={request.platforms}")
    try:
        data = services.process_kayak_content(
            request.user_input, request.context,
            request.tone, request.language, request.platforms
        )
        if data.get("status") == "need_more_info":
            return JSONResponse(content=data)

        image_path = services.generate_marketing_image(
            data.get("image_prompt", "kayak tour Berlin")
        )
        entry = {
            "id": str(uuid.uuid4()),
            "ts": datetime.now(timezone.utc).isoformat(),
            "user_input": request.user_input,
            "tone": request.tone,
            "platforms": request.platforms,
            "content": data,
            "has_image": image_path not in ("image_error", "timeout", "connection_failed"),
        }
        _push_history(entry)
        return {"status": "complete", "id": entry["id"], "content": data, "image_url": "/latest_promo.png"}
    except json.JSONDecodeError:
        raise HTTPException(500, "AI returned malformed data — please retry.")
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, str(e))


@app.post("/api/v1/generate/bulk", tags=["content"])
async def generate_bulk(request: BulkRequest):
    logger.info(f"Bulk | tone={request.tone}")
    try:
        data = services.generate_bulk_content(request.user_input, request.tone, request.language)
        entry = {
            "id": str(uuid.uuid4()),
            "ts": datetime.now(timezone.utc).isoformat(),
            "type": "bulk",
            "user_input": request.user_input,
            "content": data,
        }
        _push_history(entry)
        return {"status": "complete", "id": entry["id"], **data}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(500, str(e))


@app.get("/api/v1/history", tags=["content"])
async def get_history():
    return {"items": list(reversed(_load_history()))}


@app.delete("/api/v1/history/{item_id}", tags=["content"])
async def delete_history(item_id: str):
    h = _load_history()
    filtered = [x for x in h if x.get("id") != item_id]
    if len(filtered) == len(h):
        raise HTTPException(404, "Not found")
    _save_history(filtered)
    return {"deleted": item_id}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)