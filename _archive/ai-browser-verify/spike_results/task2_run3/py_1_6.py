# -*- coding: utf-8 -*-
import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\spike_results\\task2_run3\\py_1_6.py']



async def act(page):
    # Fill the search box with 'AI' and search
    search_box = page.get_by_role("searchbox", name="Search stories by title, url or author")
    await search_box.fill("AI", timeout=15000)
    # Press Enter to submit the search
    await search_box.press("Enter", timeout=15000)
    # Wait for search results to load
    import asyncio
    await asyncio.sleep(3)