from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP
from playwright.async_api import Browser, async_playwright


@dataclass
class AppContext:
    browser: Browser


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-setuid-sandbox"],
    )
    try:
        yield AppContext(browser=browser)
    finally:
        await browser.close()
        await pw.stop()


mcp = FastMCP("mcp-experiment-01", lifespan=app_lifespan)
