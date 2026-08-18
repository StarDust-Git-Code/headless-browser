# Headless REST API - Access Structure & Reference Guide

**Base URL**: `https://headless-browser-xiuu.onrender.com`  
**Local Development Base URL**: `http://localhost:8000`  
**Interactive Swagger UI**: [`https://headless-browser-xiuu.onrender.com/docs`](https://headless-browser-xiuu.onrender.com/docs)  
**OpenAPI Specification**: [`https://headless-browser-xiuu.onrender.com/openapi.json`](https://headless-browser-xiuu.onrender.com/openapi.json)

---

## 📋 Endpoints Overview

| Method | Endpoint | Description | Query / Body Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Service health check | None |
| `GET` | `/api/search` | Web Search Engine | `q` *(required)*, `limit` *(optional, default: 5)* |
| `GET` | `/api/read` | Fast HTML Reader | `url` *(required)* |
| `GET` | `/api/fetch` | Remote Browser Rendering | `url` *(required)*, `format`, `screenshot` |
| `POST` | `/api/fetch` | Remote Browser Rendering | JSON Body *(see below)* |

---

## 🔌 1. Health Check Endpoint (`GET /health`)

### Request
```http
GET /health HTTP/1.1
Host: headless-browser-xiuu.onrender.com
```

### Response (`application/json`)
```json
{
  "status": "ok",
  "service": "Headless Web Tools API",
  "default_cdp_url": "ws://127.0.0.1:9222"
}
```

---

## 🔍 2. Web Search API (`GET /api/search`)

Searches the web via DuckDuckGo and returns structured JSON results with titles, links, and snippets.

### Query Parameters
- `q` *(string, required)*: The search term (e.g. `python playwright tutorial`).
- `limit` *(integer, optional, default: `5`, range: `1-20`)*: Maximum results to return.

### Example Request
```http
GET /api/search?q=obscura+headless+browser&limit=2 HTTP/1.1
Host: headless-browser-xiuu.onrender.com
```

### Response Schema (`application/json`)
```json
{
  "query": "obscura headless browser",
  "count": 2,
  "results": [
    {
      "title": "GitHub - h4ckf0r0day/obscura: The headless browser for AI agents",
      "url": "https://github.com/h4ckf0r0day/obscura",
      "snippet": "Obscura is a headless browser engine written in Rust..."
    },
    {
      "title": "Obscura · Give every agent its own browser",
      "url": "https://obscura.sh/",
      "snippet": "Obscura is an open source, headless browser engine..."
    }
  ]
}
```

---

## 📄 3. Static Content Reader API (`GET /api/read`)

Fetches static HTML content, strips non-content tags (scripts, CSS, navs), and converts DOM to Markdown.

### Query Parameters
- `url` *(string, required)*: Target page URL (e.g. `https://example.com`).

### Example Request
```http
GET /api/read?url=https://example.com HTTP/1.1
Host: headless-browser-xiuu.onrender.com
```

### Response Schema (`application/json`)
```json
{
  "status": 200,
  "title": "Example Domain",
  "url": "https://example.com",
  "markdown": "# Example Domain\n\nThis domain is for use in documentation examples..."
}
```

---

## 🖥️ 4. Remote Headless Browser API (`POST /api/fetch`)

Connects to the Obscura headless browser over CDP, renders JavaScript-heavy dynamic pages in stealth mode, extracts content, and optional base64 screenshot.

### Request Headers
`Content-Type: application/json`

### Request Body Schema
```json
{
  "url": "https://example.com",
  "format": "markdown",
  "screenshot": true,
  "cdp_url": "ws://127.0.0.1:9222"
}
```

- `url` *(string, required)*: Target URL to render.
- `format` *(string, optional, default: `"markdown"`)*: Options: `"markdown"`, `"text"`, `"html"`.
- `screenshot` *(boolean, optional, default: `false`)*: Capture base64 encoded screenshot.
- `cdp_url` *(string, optional)*: Override remote CDP endpoint.

### Response Schema (`application/json`)
```json
{
  "status": 200,
  "title": "Example Domain",
  "url": "https://example.com",
  "content": "# Example Domain\n\nThis domain is for use in documentation...",
  "screenshot_base64": "iVBORw0KGgoAAAANSUhEUgA..."
}
```

---

## 💻 Code Integration Examples

### 1. cURL
```bash
# Web Search
curl "https://headless-browser-xiuu.onrender.com/api/search?q=fastapi&limit=3"

# Content Reader
curl "https://headless-browser-xiuu.onrender.com/api/read?url=https://example.com"

# Dynamic Browser Fetcher with Screenshot
curl -X POST "https://headless-browser-xiuu.onrender.com/api/fetch" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com", "format": "markdown", "screenshot": true}'
```

### 2. Python (`requests`)
```python
import requests

BASE_URL = "https://headless-browser-xiuu.onrender.com"

# 1. Search
search_res = requests.get(f"{BASE_URL}/api/search", params={"q": "headless browser", "limit": 3}).json()
print("Search Results:", search_res["results"])

# 2. Render Page with Screenshot
payload = {
    "url": "https://example.com",
    "format": "markdown",
    "screenshot": True
}
fetch_res = requests.post(f"{BASE_URL}/api/fetch", json=payload).json()
print("Page Title:", fetch_res["title"])
print("Content:\n", fetch_res["content"])
```

### 3. JavaScript / Node.js (`fetch`)
```javascript
const BASE_URL = 'https://headless-browser-xiuu.onrender.com';

// Fetch dynamic page content
async function fetchPage(targetUrl) {
  const response = await fetch(`${BASE_URL}/api/fetch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      url: targetUrl,
      format: 'markdown',
      screenshot: false
    })
  });
  
  const data = await response.json();
  console.log(`Title: ${data.title}`);
  console.log(`Content: ${data.content}`);
}

fetchPage('https://example.com');
```
