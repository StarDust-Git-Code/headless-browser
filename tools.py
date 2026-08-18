"""
Unified Web Tools Runner (tools.py)
===================================
Provides a single unified command-line entrypoint for:
1. `search`: Search the web (DuckDuckGo engine)
2. `read`: Fetch static URL content and convert to Markdown
3. `fetch`: Render dynamic URL using Obscura CDP remote browser and capture screenshots
"""

import sys
import json
from search_web import search_web
from read_url import read_url_content
from fetcher import fetch_web_page
import asyncio

def print_help():
    print("""
Unified Web Tools CLI
=====================
Usage:
  python tools.py search <query> [max_results]
  python tools.py read <url>
  python tools.py fetch <url> [--screenshot path.png] [--format markdown|text|html]

Examples:
  python tools.py search "Render deployment guide"
  python tools.py read "https://news.ycombinator.com"
  python tools.py fetch "https://example.com" --screenshot page.png
""")

def main():
    if len(sys.argv) < 3:
        print_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "search":
        query = sys.argv[2]
        count = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        results = search_web(query, max_results=count)
        print(json.dumps(results, indent=2))

    elif command == "read":
        url = sys.argv[2]
        result = read_url_content(url)
        if "error" in result:
            print(f"[!] Read error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"# {result['title']}\nURL: {result['url']}\nStatus: {result['status']}\n")
        print(result["markdown"])

    elif command == "fetch":
        url = sys.argv[2]
        screenshot = None
        fmt = "markdown"

        for i, arg in enumerate(sys.argv):
            if arg == "--screenshot" and i + 1 < len(sys.argv):
                screenshot = sys.argv[i + 1]
            elif arg == "--format" and i + 1 < len(sys.argv):
                fmt = sys.argv[i + 1]

        res = asyncio.run(fetch_web_page(
            target_url=url,
            screenshot_path=screenshot,
            output_format=fmt
        ))
        print(f"\n# {res['title']}\nURL: {res['url']}\nStatus: {res['status']}\n")
        print(res["content"])

    else:
        print(f"[!] Unknown command '{command}'", file=sys.stderr)
        print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
