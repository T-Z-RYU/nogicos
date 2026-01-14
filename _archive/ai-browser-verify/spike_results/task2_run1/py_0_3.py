# -*- coding: utf-8 -*-
import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\spike_results\\task2_run1\\py_0_3.py']



async def act(page):
    # Click on the 'submit' link to access the search page
    await page.get_by_role("link", name="submit").first.click(timeout=15000)

    # Wait for the search input to become visible
    await page.wait_for_selector('input[name="q"]', state='visible', timeout=15000)

    # Fill the search input with 'AI'
    search_input = page.get_by_role("textbox", name="Search")
    await search_input.first.fill('AI', timeout=15000)

    # Press enter to submit the search
    await search_input.first.press('Enter', timeout=15000)

    # Wait for the search results to load
    await page.wait_for_selector('tr.athing', state='visible', timeout=15000)

    # Get the title of the first search result
    first_result_title = await page.get_by_role("row", name="1.").get_by_role("link").first.text_content()

    print(first_result_title)
    return first_result_title