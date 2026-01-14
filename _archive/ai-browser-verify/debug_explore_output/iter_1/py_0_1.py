import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\debug_explore_output\\iter_1\\py_0_1.py']

async def hn_search_from_footer(page, query: str, start_path: str = "/news") -> None:
    """Search Hacker News using the footer "Search" textbox.

    What this skill does:
        1) Navigates to a Hacker News listing page (default: /news).
        2) Scrolls to the bottom to reveal the footer area.
        3) Finds the footer search textbox.
        4) Fills it with ``query``.
        5) Presses Enter to submit and waits for the results to load.

    Args:
        page: Playwright Page.
        query: Search terms to submit (example: "zig x server").
        start_path: Relative path to start from (example: "/news", "/newest", "/ask").

    Waiting / navigation behavior:
        - After pressing Enter, this function waits for ``domcontentloaded``.
        - Depending on current HN configuration, submitting the footer search may:
            * Navigate to an on-site results page, or
            * Redirect to an external provider (commonly Algolia).
          This skill does not assume a specific destination; it only waits for the next page
          to reach DOMContentLoaded.

    Selector strategy and robustness notes:
        - Hacker News pages are very minimal; the footer search input is typically the last
          textbox on the page.
        - This skill selects the last textbox (``page.get_by_role('textbox').last``) after
          scrolling to the bottom. If a browser extension injects extra inputs at the end of the
          page, this heuristic could select the wrong textbox.

    Unexpected/useful observed behavior:
        - Scrolling to ``document.body.scrollHeight`` reliably reveals the footer search area.
        - The search box can be used without clicking first; ``fill()`` + ``press('Enter')`` works.

    Usage log:
        - 2025-12-25: From the HN front page listing, scrolled to footer, filled "zig x server",
          pressed Enter; results page loaded successfully.

    """
    await page.goto(start_path)
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    textboxes = page.get_by_role("textbox")
    await textboxes.first.wait_for(state="visible")
    search_box = textboxes.last
    await search_box.scroll_into_view_if_needed()
    await search_box.wait_for(state="visible")
    await search_box.fill(query)
    await search_box.press("Enter")
    await page.wait_for_load_state("domcontentloaded")


async def act(page):
    # Open the comments thread for the post ranked 12
    await page.get_by_role(
        "row",
        name="296 points by nickrubin 3 hours ago | hide | 192 comments",
    ).get_by_role("link", name="192 comments").click()