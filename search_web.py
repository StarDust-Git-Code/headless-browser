"""
Web Search Tool (search_web.py)
===============================
Performs web searches via DuckDuckGo HTML engine without requiring API keys.
Outputs structured JSON or human-readable search results with URLs and snippets.
"""

import sys
import json
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0.0.0 Safari/537.36"
)

def search_web(query: str, max_results: int = 8) -> list:
    """
    Search the web for a given query string.
    Returns a list of dicts: [{'title': ..., 'url': ..., 'snippet': ...}]
    """
    query = query.strip()
    if not query:
        return []

    encoded_query = urllib.parse.urlencode({"q": query})
    url = f"https://html.duckduckgo.com/html/?{encoded_query}"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
    )

    results = []
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        soup = BeautifulSoup(html, "html.parser")
        result_blocks = soup.find_all("div", class_="result")

        for block in result_blocks[:max_results]:
            title_elem = block.find("a", class_="result__a")
            snippet_elem = block.find("a", class_="result__snippet")

            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)
            raw_href = title_elem.get("href", "")

            # Decode DuckDuckGo redirected URL if applicable
            parsed_url = raw_href
            if "uddg=" in raw_href:
                qs = urllib.parse.parse_qs(urllib.parse.urlparse(raw_href).query)
                if "uddg" in qs:
                    parsed_url = qs["uddg"][0]

            snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

            results.append({
                "title": title,
                "url": parsed_url,
                "snippet": snippet
            })

    except Exception as e:
        print(f"[!] Error during web search: {e}", file=sys.stderr)

    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_web.py <search query> [max_results]")
        sys.exit(1)

    search_query = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    res = search_web(search_query, max_results=count)
    print(json.dumps(res, indent=2))
