# -*- coding: utf-8 -*-
import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\spike_results\\task1_run2\\py_0_1.py']



async def act(page):
    first_title_link = page.get_by_role("cell", name=
        "Maybe the default settings are too high").get_by_role("link").first
    title = await first_title_link.text_content()
    return title