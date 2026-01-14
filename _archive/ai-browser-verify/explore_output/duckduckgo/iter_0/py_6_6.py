import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\explore_output\\duckduckgo\\iter_0\\py_6_6.py']



async def act(page):
    import os
    import asyncio
    from playwright.async_api import Page
    async def act(page: Page):
        query = os.environ.get("QUERY", "example query")
        # Fill the search combobox (already expanded) and submit
        search_combo = (
            page.get_by_role("main")
            .get_by_role("article")
            .get_by_role("search", name="Searchbox")
            .get_by_role("combobox", name="Search with DuckDuckGo")
        )
        await search_combo.fill(query)
        await search_combo.press("Enter")
        # Wait for results to load
        await page.wait_for_load_state("domcontentloaded")
        # Click the first search result (last action; navigates away)
        first_result_link = (
            page.get_by_role("main")
            .get_by_role("article")
            .first
            .get_by_role("link")
            .first
        )
        await first_result_link.click()