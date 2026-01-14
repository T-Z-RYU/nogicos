import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\comparison_results\\with_kb\\task1_search\\py_0_6.py']

async def hn_search_from_footer(page, query: str, start_path: str = "https://news.ycombinator.com/news") -> None:
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
        start_path: Full URL to start from (example: "https://news.ycombinator.com/news").

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


async def open_hn_comments_thread_by_rank(page, rank: int) -> None:
    """Open the Hacker News comments thread (HN "item" page) for the front-page story at a given rank.

    This skill navigates to the Hacker News front page (`/news`) and clicks the
    comments/discuss link for the story currently displayed at 1-based rank `rank`.

    How it works (observed HN page structure)
    ----------------------------------------
    - The `/news` page is a table where each story is represented by a *title row*
      (rank number + "upvote" + title), followed shortly by a *subtext row*
      containing points/user/age and a link to the comments thread.
    - The link to the comment thread is typically either:
        - "<number> comments" (e.g., "192 comments"), or
        - "discuss" (often used when there are 0 comments).

    Selector strategy (Accessibility Tree-centric; no CSS/xpath locators)
    --------------------------------------------------------------------
    - Row accessible names include volatile content (points, username, age, comment count),
      so matching a row by its full accessible name is brittle.
    - Instead, this function:
        1) enumerates all rows via `page.get_by_role("row")`
        2) treats rows containing a link named "upvote" as *title rows*
        3) picks the (rank-1)th title row
        4) scans forward a handful of subsequent rows to find the first comments link
           (either a "<number> comments" link or a "discuss" link) and clicks it.

    Unexpected-but-useful observations
    ---------------------------------
    - Hacker News frequently inserts spacer rows between a title row and its subtext row.
      Because of that, assuming "the very next row is the subtext row" can be flaky.
      Scanning forward for the comments/discuss link is more robust.
    - The heuristic "row contains an 'upvote' link" should work for typical `/news` stories,
      but may fail in edge cases (e.g., unusual items or different logged-in behavior).
      If that occurs, the heuristic may need to be changed to detect title rows by the
      presence of the story title link instead.

    Parameters
    ----------
    page:
        Playwright page.
    rank:
        1-based rank on `/news` (e.g., 12 for the 12th story).

    Raises
    ------
    ValueError
        If `rank` < 1, if the rank is not present on the page, or if the comments/discuss
        link cannot be found after the selected title row.

    Usage log
    ---------
    - 2025-12-25: Opened the rank-12 story comments by clicking the "192 comments" link.
      Result: navigated to the HN item page (comments thread) successfully.

    """
    import re

    if rank < 1:
        raise ValueError("rank must be >= 1")
    await page.goto("https://news.ycombinator.com/news")
    all_rows = page.get_by_role("row")
    row_count = await all_rows.count()
    title_row_positions: list[int] = []
    for i in range(row_count):
        row = all_rows.nth(i)
        if await row.get_by_role("link", name="upvote").count() > 0:
            title_row_positions.append(i)
    if not title_row_positions:
        raise ValueError(
            "Could not find any story title rows (no rows containing an 'upvote' link)."
        )
    if rank > len(title_row_positions):
        raise ValueError(
            f"Requested rank {rank}, but only found {len(title_row_positions)} story rows on /news."
        )
    title_row_index = title_row_positions[rank - 1]
    max_scan_ahead = 12
    for j in range(
        title_row_index + 1, min(title_row_index + 1 + max_scan_ahead, row_count)
    ):
        candidate_row = all_rows.nth(j)
        numeric_comments = candidate_row.get_by_role(
            "link", name=re.compile(r"^\d+\s+comments$")
        )
        if await numeric_comments.count() > 0:
            await numeric_comments.first.click()
            return
        discuss = candidate_row.get_by_role("link", name="discuss")
        if await discuss.count() > 0:
            await discuss.first.click()
            return
    raise ValueError(
        "Could not find a comments link after the selected title row (neither '<number> comments' nor 'discuss')."
    )


async def act(page):
    # Use the provided knowledge_base skill to search via the footer search box.
    await hn_search_from_footer(page, query="rust programming", start_path="https://news.ycombinator.com/news")