# -*- coding: utf-8 -*-
import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\spike_results\\task1_run1\\py_0_0.py']



async def act(page):
    # Get the first news item title by finding the link in the first news item row
    first_title_link = page.get_by_role("link", name="Maybe the default settings are too high").first
    title_text = await first_title_link.text_content(timeout=15000)
    print(title_text)
    return title_text