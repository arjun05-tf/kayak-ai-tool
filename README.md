# KayakFlow AI 🚣

> **AI-powered marketing automation** for Berlin Kayak Tours — generate multi-platform content, 7-day calendars, and promo images instantly.

[![CI](https://github.com/your-username/kayak-ai-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/kayak-ai-tool/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![Groq](https://img.shields.io/badge/LLM-Groq%20Llama%203.3-orange)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎯 **Multi-Platform Content** | Instagram, Facebook, TikTok, WhatsApp, Email — one click |
| 🎨 **Tone Control** | Adventurous / Romantic / Professional / Family |
| 🌍 **Language Toggle** | Auto-detect, English, Deutsch |
| 📅 **7-Day Calendar** | Full content calendar from a single concept |
| 🖼️ **AI Promo Images** | Flux model via Pollinations — cinematic quality |
| 📜 **Generation History** | Last 50 campaigns stored server-side (JSON) |
| ⚡ **Ultra-Fast** | Groq LPU inference — Llama 3.3 70B in < 1s |
| 🏥 **Health Check** | `/health` endpoint for CI/CD and load balancers |

---

## 🚀 Quick Start

### 1. Clone & install dependencies
```bash
git clone https://github.com/your-username/kayak-ai-tool.git
cd kayak-ai-tool
pip install -r requirements.txt
```

### 2. Set environment variables
```bash
# Create .env file
echo "GROQ_API_KEY=your_groq_key_here" > .env
```
Get a free Groq key at [console.groq.com](https://console.groq.com)

### 3. Run locally
```bash
python main.py
# Open http://localhost:8000
```

---

## 🐳 Docker

```bash
# Build & run
docker build -t kayakflow .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key kayakflow

# Or with docker-compose
docker-compose up
```

---

## 🧪 Tests

```bash
pytest tests/ -v
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check — CI/CD probe |
| `GET` | `/api/v1/history` | Last 50 generations |
| `DELETE` | `/api/v1/history/{id}` | Delete a history item |
| `POST` | `/api/v1/generate` | Generate single campaign |
| `POST` | `/api/v1/generate/bulk` | Generate 7-day calendar |

Interactive docs: `http://localhost:8000/docs`

### POST /api/v1/generate
```json
{
  "user_input": "Sunset kayak for couples in Kreuzberg",
  "tone": "romantic",
  "language": "auto",
  "platforms": ["instagram", "whatsapp", "email"]
}
```

---

## ☁️ Deploy to Render.com

1. Push to GitHub
2. Go to [render.com](https://render.com) → New Web Service → connect repo
3. Add `GROQ_API_KEY` in Environment settings
4. Deploy — `render.yaml` handles the rest

**Auto-deploy on tag:**
```bash
git tag v1.0.0 && git push --tags
```

---

## 🏗️ Architecture

```
Browser → FastAPI (main.py)
             ├── /api/v1/generate → services.process_kayak_content() → Groq LLM
             │                   → services.generate_marketing_image() → Pollinations
             ├── /api/v1/generate/bulk → services.generate_bulk_content() → Groq LLM
             └── /api/v1/history → history.json (file-backed store)
```

---

## 📁 Project Structure

```
kayak-ai-tool/
├── main.py               # FastAPI app, routes, history store
├── services.py           # LLM + image generation logic
├── index.html            # Premium single-page frontend
├── requirements.txt      # Pinned dependencies
├── Dockerfile            # Multi-stage production image
├── docker-compose.yml    # Local dev stack
├── render.yaml           # One-click Render.com deploy
├── .github/
│   └── workflows/
│       ├── ci.yml        # Lint → Test → Docker build
│       └── deploy.yml    # Auto-deploy on version tags
└── tests/
    └── test_api.py       # pytest suite
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Groq API key for LLM |
| `LOG_LEVEL` | No | Logging level (default: `INFO`) |

---

Built with ❤️ for Campus Eiswerder · Berlin
