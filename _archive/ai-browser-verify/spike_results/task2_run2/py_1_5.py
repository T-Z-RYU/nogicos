# -*- coding: utf-8 -*-
import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\spike_results\\task2_run2\\py_1_5.py']



async def act(page):
    # Scroll down to find the search form at the bottom of the page
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    # Wait for the search form to be visible
    await page.wait_for_selector("form[action*='hn.algolia.com']", state="visible", timeout=15000)
    # Find the search input and enter 'AI'
    search_input = page.get_by_role("textbox", name="Search").first
    await search_input.fill("AI", timeout=15000)
    # Submit the search (press Enter)
    await search_input.press("Enter", timeout=15000)