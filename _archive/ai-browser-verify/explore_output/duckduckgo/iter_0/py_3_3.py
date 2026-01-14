import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\explore_output\\duckduckgo\\iter_0\\py_3_3.py']



async def act(page):
    import os
    from playwright.async_api import Page
    async def act(page: Page):
        query = os.environ.get("QUERY", "example query")
        # Fill the already-expanded search combobox and submit
        search_combo = (
            page.get_by_role("main")
            .get_by_role("article")
            .get_by_role("search", name="Searchbox")
            .get_by_role("combobox", name="Search with DuckDuckGo")
        )
        await search_combo.fill(query)
        await search_combo.press("Enter")
        # Wait for navigation to results
        await page.wait_for_load_state("domcontentloaded")
        # Open the first result (scoped path to avoid ambiguous link matches)
        results_main = page.get_by_role("main")
        first_result_link = (
            results_main.get_by_role("list")
            .get_by_role("listitem")
            .first
            .get_by_role("link")
            .first
        )
        await first_result_link.click()