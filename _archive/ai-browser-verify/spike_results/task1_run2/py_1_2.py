# -*- coding: utf-8 -*-
import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\spike_results\\task1_run2\\py_1_2.py']



async def act(page):
    first_news_title = page.get_by_role("row", name="1. upvote Maybe the default settings are too high (raptitude.com)").get_by_role("link", name="Maybe the default settings are too high").first
    title_text = await first_news_title.text_content()
    return title_text