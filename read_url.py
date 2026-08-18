"""
URL Content Reader Tool (read_url.py)
=====================================
Fetches HTML content from a URL via HTTP GET request, strips scripts/CSS,
and converts the DOM structure into clean Markdown/plain text.
"""

import sys
import json
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup, Comment

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

def read_url_content(target_url: str) -> dict:
    """
    Fetch URL content and convert to clean Markdown/Text.
    Returns: {'title': ..., 'url': ..., 'markdown': ..., 'status': ...}
    """
    target_url = target_url.strip()
    if not (target_url.startswith("http://") or target_url.startswith("https://")):
        target_url = f"https://{target_url}"

    req = urllib.request.Request(
        target_url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9"
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            status_code = response.status
            content_type = response.headers.get("Content-Type", "")
            raw_data = response.read()

            # Handle charset encoding
            charset = "utf-8"
            if "charset=" in content_type:
                charset = content_type.split("charset=")[-1].split(";")[0].strip()

            html_text = raw_data.decode(charset, errors="ignore")

        soup = BeautifulSoup(html_text, "html.parser")

        # Extract title
        title = soup.title.get_text(strip=True) if soup.title else target_url

        # Remove non-content elements
        for element in soup(["script", "style", "noscript", "svg", "iframe", "footer", "header", "nav"]):
            element.decompose()

        for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Build clean markdown-like text structure
        lines = []
        for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "pre", "blockquote"]):
            text = tag.get_text(strip=True)
            if not text:
                continue

            name = tag.name
            if name == "h1":
                lines.append(f"\n# {text}\n")
            elif name == "h2":
                lines.append(f"\n## {text}\n")
            elif name == "h3":
                lines.append(f"\n### {text}\n")
            elif name in ["h4", "h5", "h6"]:
                lines.append(f"\n#### {text}\n")
            elif name == "li":
                lines.append(f"- {text}")
            elif name == "blockquote":
                lines.append(f"> {text}")
            elif name == "pre":
                lines.append(f"\n```\n{text}\n```\n")
            else:
                lines.append(text)

        markdown_content = "\n\n".join(lines) if lines else soup.get_text(separator="\n", strip=True)

        return {
            "status": status_code,
            "title": title,
            "url": target_url,
            "markdown": markdown_content[:20000]  # Cap length for readability
        }

    except Exception as e:
        return {
            "status": "error",
            "title": "Error",
            "url": target_url,
            "error": str(e)
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python read_url.py <URL>")
        sys.exit(1)

    url_to_read = sys.argv[1]
    result = read_url_content(url_to_read)
    
    if "error" in result:
        print(f"[!] Failed to read URL: {result['error']}", file=sys.stderr)
        sys.exit(1)

    print(f"# {result['title']}\nURL: {result['url']}\nStatus: {result['status']}\n")
    print("--- CONTENT ---")
    print(result["markdown"])
