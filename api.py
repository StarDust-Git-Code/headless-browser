"""
Headless Web Tools REST API Server (api.py)
===========================================
High-performance FastAPI server delivering RESTful endpoints for:
- Web Search (/api/search)
- Static HTML Reader (/api/read)
- Remote CDP Headless Browser Fetcher & Screenshots (/api/fetch)
"""

import os
import base64
from typing import Optional, Literal
from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, HttpUrl, Field
import uvicorn

from search_web import search_web
from read_url import read_url_content
from fetcher import fetch_web_page, DEFAULT_CDP_URL

app = FastAPI(
    title="Headless Web Tools REST API",
    description="REST API for web search, HTML content extraction, and remote CDP browser rendering via Obscura.",
    version="1.0.0"
)

# --- Pydantic Models ---
class FetchRequest(BaseModel):
    url: str = Field(..., example="https://example.com", description="Target URL to render")
    format: Literal["markdown", "text", "html"] = Field("markdown", description="Output content format")
    screenshot: bool = Field(False, description="Whether to capture a page screenshot")
    cdp_url: Optional[str] = Field(None, description="Optional remote Obscura CDP WebSocket URL")

class FetchResponse(BaseModel):
    status: int
    title: str
    url: str
    content: str
    screenshot_base64: Optional[str] = None

# --- Routes ---

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root_dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Headless Web Tools API</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.6; background: #0f172a; color: #f8fafc; }
            h1 { color: #38bdf8; border-bottom: 1px solid #334155; padding-bottom: 12px; }
            .endpoint { background: #1e293b; padding: 16px; border-radius: 8px; margin-bottom: 16px; border-left: 4px solid #38bdf8; }
            code { background: #0284c7; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
            a { color: #38bdf8; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>🌐 Headless Web Tools REST API</h1>
        <p>Production API delivering remote headless browser rendering, web search, and HTML-to-Markdown extraction.</p>
        
        <div class="endpoint">
            <h3>🔍 Web Search API</h3>
            <p><code>GET /api/search?q={query}&limit=5</code></p>
            <p>Searches the web via DuckDuckGo engine and returns structured JSON title, URL, and snippet results.</p>
        </div>

        <div class="endpoint">
            <h3>📄 Static Content Reader API</h3>
            <p><code>GET /api/read?url={url}</code></p>
            <p>Fetches static HTML content and converts DOM to clean Markdown text.</p>
        </div>

        <div class="endpoint">
            <h3>🖥️ Remote CDP Browser Fetcher API</h3>
            <p><code>POST /api/fetch</code> or <code>GET /api/fetch?url={url}&screenshot=true</code></p>
            <p>Renders JavaScript-heavy dynamic pages over WSS CDP via deployed Obscura server with optional base64 screenshot.</p>
        </div>

        <p>Interactive Swagger Documentation: <a href="/docs"><strong>/docs</strong></a> | OpenAPI Spec: <a href="/openapi.json"><strong>/openapi.json</strong></a></p>
    </body>
    </html>
    """

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Headless Web Tools API", "default_cdp_url": DEFAULT_CDP_URL}

@app.get("/api/search")
def api_search_web(
    q: str = Query(..., description="Search query string"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of search results")
):
    """
    Perform a web search and return structured JSON results.
    """
    results = search_web(query=q, max_results=limit)
    return {"query": q, "count": len(results), "results": results}

@app.get("/api/read")
def api_read_url(
    url: str = Query(..., description="Target web page URL to read")
):
    """
    Fetch static HTML content from a URL and convert it to clean Markdown.
    """
    res = read_url_content(target_url=url)
    if "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.get("/api/fetch", response_model=FetchResponse)
async def api_fetch_url_get(
    url: str = Query(..., description="Target web page URL to render"),
    format: Literal["markdown", "text", "html"] = Query("markdown", description="Output format"),
    screenshot: bool = Query(False, description="Capture screenshot"),
    cdp_url: Optional[str] = Query(None, description="Custom Obscura CDP WebSocket URL")
):
    """
    Render dynamic page via remote CDP Obscura browser (GET interface).
    """
    return await handle_fetch(url, format, screenshot, cdp_url)

@app.post("/api/fetch", response_model=FetchResponse)
async def api_fetch_url_post(req: FetchRequest):
    """
    Render dynamic page via remote CDP Obscura browser (POST interface).
    """
    return await handle_fetch(req.url, req.format, req.screenshot, req.cdp_url)

async def handle_fetch(url: str, format_str: str, take_screenshot: bool, custom_cdp_url: Optional[str]):
    cdp_endpoint = custom_cdp_url if custom_cdp_url else DEFAULT_CDP_URL
    screenshot_file = "temp_api_screenshot.png" if take_screenshot else None

    res = await fetch_web_page(
        target_url=url,
        cdp_url=cdp_endpoint,
        screenshot_path=screenshot_file,
        output_format=format_str
    )

    screenshot_b64 = None
    if take_screenshot and screenshot_file and os.path.exists(screenshot_file):
        try:
            with open(screenshot_file, "rb") as f:
                screenshot_b64 = base64.b64encode(f.read()).decode("utf-8")
            os.remove(screenshot_file)
        except Exception as e:
            print(f"[!] Failed to encode screenshot: {e}")

    return {
        "status": res["status"],
        "title": res["title"],
        "url": res["url"],
        "content": res["content"],
        "screenshot_base64": screenshot_b64
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=False)
