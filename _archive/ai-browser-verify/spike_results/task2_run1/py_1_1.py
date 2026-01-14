# -*- coding: utf-8 -*-
import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\spike_results\\task2_run1\\py_1_1.py']



async def act(page):
    await page.get_by_role("searchbox", name="Search stories by title, url or author").first.fill("AI", timeout=15000)
    await page.keyboard.press("Enter", timeout=15000)
    await page.wait_for_timeout(2000)