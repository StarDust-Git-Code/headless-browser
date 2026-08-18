"""
Obscura Remote Browser CDP Connection Verifier
==============================================
This script connects to the deployed Obscura instance on Render over WSS
and navigates to a specified target URL (e.g. Google Search), capturing title,
stealth flags, and a screenshot.
"""

import asyncio
import os
import sys
from playwright.async_api import async_playwright, Error as PlaywrightError

DEFAULT_CDP_URL = os.getenv(
    "OBSCURA_CDP_URL",
    "wss://headless-browser-xiuu.onrender.com"
)

DEFAULT_TARGET_URL = os.getenv(
    "TARGET_URL",
    "https://www.google.com/search?q=workstation&rlz=1C1RXQR_enIN1217IN1217&oq=w&gs_lcrp=EgZjaHJvbWUqBggDEEUYOzIGCAAQRRg8MgYIARBFGDkyBggCEEUYOzIGCAMQRRg7MgYIBBBFGDwyBggFEEUYPDIGCAYQRRg8MgYIBxBFGDzSAQg2MDM4ajBqNKgCALACAQ&sourceid=chrome&source=chrome.ob&ie=UTF-8"
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

async def test_obscura_connection(cdp_endpoint: str, target_page_url: str):
    ws_endpoint = normalize_cdp_url(cdp_endpoint)
    print(f"[*] Connecting to Obscura CDP endpoint at: {ws_endpoint}")
    print(f"[*] Target page URL: {target_page_url}")

    async with async_playwright() as p:
        try:
            # Connect over Chrome DevTools Protocol (CDP) via secure WebSocket
            browser = await p.chromium.connect_over_cdp(
                endpoint_url=ws_endpoint,
                timeout=30000
            )
            print("[+] Successfully established CDP connection to remote Obscura browser!")

            contexts = browser.contexts
            context = contexts[0] if contexts else await browser.new_context()
            page = await context.new_page()

            # Navigate to target page
            print(f"[*] Navigating to {target_page_url}...")
            response = await page.goto(target_page_url, wait_until="domcontentloaded", timeout=60000)
            status_code = response.status if response else "Unknown"
            title = await page.title()
            print(f"[+] HTTP Status: {status_code}")
            print(f"[+] Page Title: '{title}'")

            # Evaluate bot detection attributes
            webdriver_state = await page.evaluate("() => navigator.webdriver")
            user_agent = await page.evaluate("() => navigator.userAgent")
            print(f"[+] navigator.webdriver: {webdriver_state} (Expected: False/None)")
            print(f"[+] navigator.userAgent: {user_agent}")

            # Capture verification screenshot
            screenshot_path = "google_search_screenshot.png"
            try:
                await page.screenshot(path=screenshot_path)
                print(f"[+] Screenshot captured and saved to {screenshot_path}")
            except Exception as se:
                print(f"[!] Screenshot skipped ({se})")

            await page.close()
            await browser.close()
            print("[+] Navigation task completed successfully!")

        except PlaywrightError as pe:
            print(f"[!] Playwright error occurred: {pe}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"[!] Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    cdp_url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CDP_URL
    page_url = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TARGET_URL
    asyncio.run(test_obscura_connection(cdp_url, page_url))
