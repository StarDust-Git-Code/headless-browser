# Obscura Headless Browser Engine & Web Tools

Production deployment configuration for hosting the [Obscura](https://github.com/h4ckf0r0day/obscura) headless browser engine on [Render.com](https://render.com) with Chrome DevTools Protocol (CDP) WebSocket support and local Python web tools.

---

## 📁 Repository Structure

```
├── .gitignore               # Git ignored patterns
├── Dockerfile               # Production multi-stage Docker container
├── render.yaml              # Render Blueprint Infrastructure-as-Code
├── search_web.py            # Web search engine tool (DuckDuckGo backend)
├── read_url.py              # Fast HTTP HTML-to-Markdown reader tool
├── fetcher.py               # Remote CDP Obscura browser fetcher & screenshot tool
├── tools.py                 # Unified CLI tool runner for search, read, and fetch
├── verify_connection.py     # CDP connection & stealth test script
├── requirements.txt         # Python dependencies
└── README.md                # Documentation and guide
```

---

## 🛠️ Web Tools CLI Usage

You can use the unified `tools.py` runner to execute web search, content reading, or CDP browser fetching:

### 1. Web Search Tool (`search`)
Search the web and retrieve structured JSON titles, URLs, and snippets:
```bash
python tools.py search "Render.com Docker deployment" 5
```

### 2. Fast HTTP Content Reader (`read`)
Fetch static web content over HTTP and convert DOM to clean Markdown:
```bash
python tools.py read "https://news.ycombinator.com"
```

### 3. Remote Obscura CDP Browser Fetcher (`fetch`)
Render dynamic JavaScript pages using your live Obscura deployment on Render with stealth mode and screenshot capture:
```bash
python tools.py fetch "https://example.com" --screenshot page.png
```

---

## 🚀 Quick Deployment Guide

### Push Updates to GitHub

```bash
git add .
git commit -m "feat: add local web tools (search_web, read_url, fetcher, tools.py)"
git push origin main
```
