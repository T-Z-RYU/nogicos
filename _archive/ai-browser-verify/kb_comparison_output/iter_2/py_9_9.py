import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\kb_comparison_output\\iter_2\\py_9_9.py']



async def act(page):
    # TODO: Replace with the exact query you want to search on DuckDuckGo
    query = "<PUT_QUERY_HERE>"

    search_input = (
        page.get_by_role("main")
        .get_by_role("search", name="Searchbox")
        .get_by_role("combobox", name="Search with DuckDuckGo")
    )

    await search_input.fill(query)
    await search_input.press("Enter")