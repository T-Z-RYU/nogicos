# -*- coding: utf-8 -*-
import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\spike_results\\task3_run1\\py_0_2.py']



async def act(page):
    await page.get_by_role("link", name="new").first.click(timeout=15000)