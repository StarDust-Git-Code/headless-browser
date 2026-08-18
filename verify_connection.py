"""
Obscura Remote Browser CDP Connection Verifier
==============================================
This script demonstrates how an AI agent or remote client connects to the
deployed Obscura instance on Render using Playwright over secure WebSocket (WSS).
"""

import asyncio
import os
import sys
from playwright.async_api import async_playwright, Error as PlaywrightError

# Target Render Service URL (e.g., 'https://obscura-browser-engine.onrender.com')
# In Render, public services terminate TLS automatically on port 443.
RENDER_SERVICE_URL = os.getenv(
    "OBSCURA_CDP_URL",
    "wss://obscura-browser-engine.onrender.com"
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

async def test_obscura_connection(cdp_endpoint: str):
    ws_endpoint = normalize_cdp_url(cdp_endpoint)
    print(f"[*] Connecting to Obscura CDP endpoint at: {ws_endpoint}")

    async with async_playwright() as p:
        try:
            # Connect over Chrome DevTools Protocol (CDP) via secure WebSocket
            browser = await p.chromium.connect_over_cdp(
                endpoint_url=ws_endpoint,
                timeout=30000  # 30 seconds connection timeout
            )
            print("[+] Successfully established CDP connection to remote browser!")

            # Retrieve browser context and open a new page
            contexts = browser.contexts
            if contexts:
                context = contexts[0]
            else:
                context = await browser.new_context()

            page = await context.new_page()

            # Test 1: Verify Stealth / Navigator Webdriver Flag
            print("[*] Navigating to navigator properties check...")
            await page.goto("https://httpbin.org/headers", wait_until="domcontentloaded")
            content = await page.text_content("body")
            print(f"[+] Response headers received:\n{content}\n")

            # Evaluate bot detection attributes
            webdriver_state = await page.evaluate("() => navigator.webdriver")
            user_agent = await page.evaluate("() => navigator.userAgent")
            print(f"[+] navigator.webdriver: {webdriver_state} (Expected: None / False)")
            print(f"[+] navigator.userAgent: {user_agent}")

            # Test 2: Take a verification screenshot (requires build with rendering enabled)
            try:
                screenshot_path = "verification_screenshot.png"
                await page.screenshot(path=screenshot_path)
                print(f"[+] Screenshot captured and saved to {screenshot_path}")
            except Exception as se:
                print(f"[!] Screenshot skipped ({se})")

            # Clean teardown
            await page.close()
            await browser.close()
            print("[+] Connection test completed successfully!")

        except PlaywrightError as pe:
            print(f"[!] Playwright error occurred: {pe}", file=sys.stderr)
            print("\nTroubleshooting Tips:")
            print("1. Ensure your Render web service is active (not spun down on free tier).")
            print("2. Verify that the URL matches your Render deployment domain.")
            print("3. Check Render deployment logs for container startup status.")
            sys.exit(1)
        except Exception as e:
            print(f"[!] Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else RENDER_SERVICE_URL
    asyncio.run(test_obscura_connection(target_url))
