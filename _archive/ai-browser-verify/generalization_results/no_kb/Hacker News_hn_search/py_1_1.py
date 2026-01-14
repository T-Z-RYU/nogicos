import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\generalization_results\\no_kb\\Hacker News_hn_search\\py_1_1.py']



import asyncio

async def act(page):
    # No knowledge base functions available for this task.

    # The Search box is in the footer; scroll to ensure it's attached/visible.
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # On HN the footer search input often has no accessible name
    # select the last textbox on the page (the footer search field).
    search_box = page.get_by_role("textbox").last
    await search_box.wait_for(state="visible", timeout=10000)
    await search_box.fill("machine learning")

    # Submit the search (navigation expected).
    await search_box.press("Enter")