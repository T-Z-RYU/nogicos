import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\generalization_results\\no_kb\\Lobsters_lobsters_search\\py_0_5.py']



async def act(page):
    # No knowledge base functions are available for this action.
    await page.get_by_role("link", name="Search").click()