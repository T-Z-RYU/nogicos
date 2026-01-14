import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\debug_explore_output\\iter_0\\py_0_0.py']



import asyncio

async def act(page):
    # Ensure we're at the footer where the search input is located
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # Hacker News footer search: label text is typically "Search:" next to a textbox
    search_box = page.get_by_role("textbox")
    await search_box.wait_for(state="visible")
    await search_box.fill("zig x server")

    # Submit the search (HN search box submits on Enter)
    await search_box.press("Enter")
    await page.wait_for_load_state("domcontentloaded")