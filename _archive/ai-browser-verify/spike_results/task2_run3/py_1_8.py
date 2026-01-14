# -*- coding: utf-8 -*-
import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\spike_results\\task2_run3\\py_1_8.py']



async def act(page):
    import re
    # I can see there's a search textbox at the bottom of the page
    # Let me click on it and search for 'AI'
    await page.wait_for_selector('textbox', state='visible', timeout=15000)
    search_box = page.get_by_role('textbox').first
    await search_box.click(timeout=15000)
    await search_box.fill('AI', timeout=15000)
    # Submit the search by pressing Enter
    await search_box.press('Enter', timeout=15000)
    # Wait for the search results page to load
    await page.wait_for_load_state('networkidle', timeout=15000)