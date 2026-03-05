import re
from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from mcp.server.fastmcp import Context

from mcp_server.config import load_config
from mcp_server.server import mcp

MAX_TEXT_LENGTH = 50_000
MAX_LINKS = 50


def _extract_clean_text(html: str) -> str:
    """Extract clean readable text from HTML, stripping boilerplate."""
    soup = BeautifulSoup(html, "lxml")

    # Remove non-content elements
    for tag in soup.find_all(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH] + "\n\n... (truncated)"

    return text


def _extract_search_results(html: str) -> str:
    """Extract structured search results from a Google search page."""
    soup = BeautifulSoup(html, "lxml")
    results: list[str] = []

    for div in soup.select("div.g"):
        # Title
        title_el = div.select_one("h3")
        title = title_el.get_text(strip=True) if title_el else ""

        # URL
        link_el = div.select_one("a[href]")
        url = link_el["href"] if link_el else ""

        # Snippet
        snippet_el = div.select_one("div[data-sncf], span.st, div.VwiC3b")
        snippet = snippet_el.get_text(strip=True) if snippet_el else ""

        if title and url:
            entry = f"**{title}**\n{url}"
            if snippet:
                entry += f"\n{snippet}"
            results.append(entry)

    if not results:
        # Fallback to generic text extraction
        return _extract_clean_text(str(soup))

    return "\n\n".join(results[:20])


async def _extract_links(page) -> str:
    """Extract links from the page."""
    links = await page.evaluate("""
        () => {
            const seen = new Set();
            return Array.from(document.querySelectorAll('a[href]'))
                .map(a => ({ text: a.textContent.trim(), href: a.href }))
                .filter(l => l.href.startsWith('http') && l.text.length > 0)
                .filter(l => {
                    if (seen.has(l.href)) return false;
                    seen.add(l.href);
                    return true;
                })
                .slice(0, """ + str(MAX_LINKS) + """)
                .map(l => `- [${l.text.substring(0, 80)}](${l.href})`)
                .join('\\n');
        }
    """)
    return links or "(No links found)"


@mcp.tool()
async def browse_web(
    url: str | None = None,
    search_query: str | None = None,
    extract_links: bool = False,
    wait_for_selector: str | None = None,
    ctx: Context | None = None,
) -> str:
    """Browse the web to retrieve information from a URL or search query.

    Provide either a direct URL to navigate to, or a search_query to
    search Google and return results. At least one must be provided.

    Args:
        url: Direct URL to navigate to and extract content from.
        search_query: Search query (uses Google search).
        extract_links: Whether to also return links found on the page.
        wait_for_selector: CSS selector to wait for before extracting content.
    """
    if not url and not search_query:
        return "Error: Provide either 'url' or 'search_query'."

    config = load_config()
    browser = ctx.request_context.lifespan_context.browser
    page = await browser.new_page(
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    )

    is_search = search_query is not None and url is None
    target_url = url if url else f"https://www.google.com/search?q={quote_plus(search_query)}"

    try:
        await page.goto(target_url, timeout=config.browser_timeout_ms, wait_until="domcontentloaded")

        if wait_for_selector:
            try:
                await page.wait_for_selector(wait_for_selector, timeout=10_000)
            except Exception:
                pass  # Continue even if selector not found

        html = await page.content()
        title = await page.title()

        # Extract text
        if is_search:
            text = _extract_search_results(html)
        else:
            text = _extract_clean_text(html)

        result = f"## {title}\n\n{text}"

        if extract_links:
            links = await _extract_links(page)
            result += f"\n\n## Links\n{links}"

        return result

    except Exception as e:
        return f"Error browsing '{target_url}': {e}"
    finally:
        await page.close()
