import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\explore_output\\duckduckgo\\iter_0\\py_1_1.py']



async def act(page):
    import os
    import asyncio
    from playwright.async_api import Page
    async def act(page: Page):
        query = os.environ.get("QUERY", "example query")
        # Use the search region -> combobox path from the accessibility tree
        search_region = page.get_by_role("search", name="Searchbox")
        search_box = search_region.get_by_role("combobox", name="Search with DuckDuckGo")
        await search_box.click()
        await search_box.fill(query)
        await search_box.press("Enter")
        # Wait for results to appear
        await page.wait_for_load_state("domcontentloaded")
        # Click the first search result link (scoped through main -> list -> listitem -> link)
        results_main = page.get_by_role("main")
        first_result = results_main.get_by_role("list").get_by_role("listitem").first
        first_result_link = first_result.get_by_role("link").first
        await first_result_link.click()