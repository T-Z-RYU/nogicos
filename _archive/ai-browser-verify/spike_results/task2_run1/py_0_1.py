# -*- coding: utf-8 -*-
import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\spike_results\\task2_run1\\py_0_1.py']



async def act(page):
    # Navigate to the search page
    await page.goto("/search", timeout=15000)
    await page.wait_for_load_state("networkidle", timeout=15000)