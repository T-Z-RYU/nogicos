# -*- coding: utf-8 -*-
import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\spike_results\\task2_run2\\py_0_2.py']



async def act(page):
    # Scroll down to find the search link at the bottom of the page
    await page.keyboard.press('End', timeout=15000)
    await page.wait_for_timeout(1000)