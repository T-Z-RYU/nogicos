# -*- coding: utf-8 -*-
import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\spike_results\\task2_run1\\py_2_3.py']



async def act(page):
    # Find and click on the search box
    search_box = page.get_by_role("searchbox", name="Search stories by title, url or author").first
    await search_box.click(timeout=15000)

    # Clear any existing text and type 'AI'
    await search_box.fill("AI", timeout=15000)

    # Press Enter to submit the search
    await search_box.press("Enter", timeout=15000)

    # Wait for search results to load
    await page.wait_for_load_state("networkidle", timeout=15000)