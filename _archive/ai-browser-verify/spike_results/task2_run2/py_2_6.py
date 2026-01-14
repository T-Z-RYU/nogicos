# -*- coding: utf-8 -*-
import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\spike_results\\task2_run2\\py_2_6.py']



async def act(page):
    # Find and interact with the search textbox at the bottom of the page
    search_input = page.get_by_role("textbox").first
    await search_input.fill("AI", timeout=15000)
    # Submit the search (press Enter)
    await search_input.press("Enter", timeout=15000)
    # Wait for the search results page to load
    await page.wait_for_load_state("networkidle", timeout=15000)