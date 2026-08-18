"""
Obscura Remote Web Fetcher Tool (fetcher.py)
============================================
Connects to the deployed Obscura headless browser instance over WSS CDP,
renders JavaScript-heavy dynamic web pages, bypasses anti-bot checks in stealth mode,
extracts structured content, and saves screenshots.
"""

import asyncio
import argparse
import os
import sys
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Error as PlaywrightError

DEFAULT_CDP_URL = os.getenv(
    "OBSCURA_CDP_URL",
    "wss://headless-browser-xiuu.onrender.com"
)

def normalize_cdp_url(url: str) -> str:
    """Ensure the endpoint uses secure WebSocket (wss://) protocol."""
    url = url.strip()
    if url.startswith("https://"):
        return "wss://" + url[len("https://"):]
    elif url.startswith("http://"):
        return "ws://" + url[len("http://"):]
    elif not (url.startswith("wss://") or url.startswith("ws://")):
        return f"wss://{url}"
    return url

async def fetch_web_page(
    target_url: str,
    cdp_url: str = DEFAULT_CDP_URL,
    screenshot_path: str = None,
    output_format: str = "markdown"
) -> dict:
    """
    Fetch dynamic web content using the remote Obscura browser over CDP.
    """
    ws_endpoint = normalize_cdp_url(cdp_url)
    print(f"[*] Connecting to Obscura browser at: {ws_endpoint}")
    print(f"[*] Navigating to: {target_url}")

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(
                endpoint_url=ws_endpoint,
                timeout=30000
            )

            contexts = browser.contexts
            context = contexts[0] if contexts else await browser.new_context()
            page = await context.new_page()

            response = await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
            status_code = response.status if response else 200
            title = await page.title()
            rendered_html = await page.content()

            soup = BeautifulSoup(rendered_html, "html.parser")
            for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
                tag.decompose()

            if output_format == "html":
                content = str(soup)
            elif output_format == "text":
                content = soup.get_text(separator="\n", strip=True)
            else:  # markdown
                lines = []
                for tag in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "pre", "blockquote"]):
                    t = tag.get_text(strip=True)
                    if not t:
                        continue
                    if tag.name == "h1":
                        lines.append(f"\n# {t}\n")
                    elif tag.name == "h2":
                        lines.append(f"\n## {t}\n")
                    elif tag.name == "h3":
                        lines.append(f"\n### {t}\n")
                    elif tag.name == "li":
                        lines.append(f"- {t}")
                    elif tag.name == "blockquote":
                        lines.append(f"> {t}")
                    elif tag.name == "pre":
                        lines.append(f"\n```\n{t}\n```\n")
                    else:
                        lines.append(t)
                content = "\n\n".join(lines) if lines else soup.get_text(separator="\n", strip=True)

            # Screenshot if requested
            if screenshot_path:
                try:
                    await page.screenshot(path=screenshot_path)
                    print(f"[+] Screenshot captured and saved to: {screenshot_path}")
                except Exception as se:
                    print(f"[!] Screenshot skipped ({se})")

            await page.close()
            await browser.close()

            return {
                "status": status_code,
                "title": title,
                "url": target_url,
                "content": content
            }

        except PlaywrightError as pe:
            print(f"[!] Playwright error: {pe}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[!] Fetcher error: {e}", file=sys.stderr)
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Obscura Remote Web Fetcher Tool")
    parser.add_argument("url", help="Target URL to fetch")
    parser.add_argument("--format", choices=["markdown", "text", "html"], default="markdown", help="Output format")
    parser.add_argument("--screenshot", help="Optional path to save screenshot (e.g. output.png)")
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL, help="Remote Obscura CDP WebSocket URL")

    args = parser.parse_args()
    res = asyncio.run(fetch_web_page(
        target_url=args.url,
        cdp_url=args.cdp_url,
        screenshot_path=args.screenshot,
        output_format=args.format
    ))

    print(f"\n# {res['title']}\nURL: {res['url']}\nStatus: {res['status']}\n")
    print("--- CONTENT ---")
    print(res["content"])

if __name__ == "__main__":
    main()
