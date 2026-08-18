# Obscura Headless Browser Engine & REST API

Production deployment configuration for hosting the [Obscura](https://github.com/h4ckf0r0day/obscura) headless browser engine on [Render.com](https://render.com) with Chrome DevTools Protocol (CDP) WebSocket support and a high-performance **FastAPI Headless Web REST API**.

---

## 📁 Repository Structure

```
├── .gitignore               # Git ignored patterns
├── Dockerfile               # Production multi-stage Docker container
├── render.yaml              # Render Blueprint Infrastructure-as-Code
├── api.py                   # FastAPI REST API server (/api/search, /api/read, /api/fetch)
├── search_web.py            # Web search engine tool (DuckDuckGo backend)
├── read_url.py              # Fast HTTP HTML-to-Markdown reader tool
├── fetcher.py               # Remote CDP Obscura browser fetcher & screenshot tool
├── tools.py                 # Unified CLI tool runner
├── verify_connection.py     # CDP connection & stealth test script
├── requirements.txt         # Python dependencies (FastAPI, Uvicorn, Playwright, BeautifulSoup)
└── README.md                # Documentation and guide
```

---

## 🚀 Running the REST API Server

Start the local REST API server:

```bash
python api.py
```
*App starts on `http://localhost:8000` (or `$PORT` when deployed to Render/Cloud).*

- **Interactive API Documentation (Swagger)**: [`http://localhost:8000/docs`](http://localhost:8000/docs)
- **Health Check**: `GET /health`

---

## 🔌 REST API Endpoints

### 1. Web Search API (`GET /api/search`)
Query DuckDuckGo search index and return structured JSON title, URL, and snippet results.
```bash
curl "http://localhost:8000/api/search?q=Obscura+browser&limit=5"
```

### 2. Static Content Reader API (`GET /api/read`)
Fetch static HTML web pages over HTTP and convert DOM to clean Markdown.
```bash
curl "http://localhost:8000/api/read?url=https://example.com"
```

### 3. Remote CDP Headless Browser Fetcher (`GET` or `POST /api/fetch`)
Render dynamic JavaScript pages using your live Obscura deployment on Render with optional base64 screenshot output.
```bash
# GET Request
curl "http://localhost:8000/api/fetch?url=https://example.com&format=markdown&screenshot=true"

# POST Request
curl -X POST "http://localhost:8000/api/fetch" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com", "format": "markdown", "screenshot": true}'
```

---

## 🛠️ CLI Usage

```bash
# Web Search CLI
python tools.py search "Render deployment guide" 5

# HTML Reader CLI
python tools.py read "https://news.ycombinator.com"

# CDP Browser Fetcher CLI
python tools.py fetch "https://example.com" --screenshot page.png
```
