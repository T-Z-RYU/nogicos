import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\kb_comparison_output\\iter_2\\py_0_0.py']



async def act(page):
    # TODO: replace with the actual query string you want to search
    query = "<PUT_QUERY_HERE>"

    search_scope = page.get_by_role("main").get_by_role("article").get_by_role("search", name="Searchbox")
    search_input = search_scope.get_by_role("combobox", name="Search with DuckDuckGo")

    await search_input.click()
    await search_input.fill(query)
    await search_input.press("Enter")