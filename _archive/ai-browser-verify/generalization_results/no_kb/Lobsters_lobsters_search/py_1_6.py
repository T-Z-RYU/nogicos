import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\generalization_results\\no_kb\\Lobsters_lobsters_search\\py_1_6.py']



async def act(page):
    search_form = page.get_by_role("form", name="Search")
    await search_form.get_by_role("searchbox", name="Search query").fill("rust programming")
    await search_form.get_by_role("button", name="Search").click()