# -*- coding: utf-8 -*-
import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\spike_results\\task2_run2\\py_2_4.py']



async def act(page):
    # Find the search box and type 'AI'
    search_box = page.get_by_role("searchbox", name="Search stories by title, url or author")
    await search_box.first.click(timeout=15000)
    await search_box.first.fill("AI", timeout=15000)
    # Press Enter to search
    await search_box.first.press("Enter", timeout=15000)
    # Wait for search results to load
    await page.wait_for_timeout(2000)