import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\computer_use_comparison_results\\computer_use\\search_task\\py_0_0.py']



import asyncio

async def act(page):
    # Ensure the footer (where HN search lives) is reachable/visible.
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # HN footer search: label text "Search:" followed by a single textbox.
    # Use role-based selection; HN typically has only one textbox on the page.
    search_box = page.get_by_role("textbox").nth(0)

    await search_box.fill("rust programming")
    await search_box.press("Enter")
    await page.wait_for_load_state("domcontentloaded")