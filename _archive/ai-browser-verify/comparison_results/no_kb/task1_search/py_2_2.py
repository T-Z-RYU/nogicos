import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\comparison_results\\no_kb\\task1_search\\py_2_2.py']



import asyncio

async def act(page):
    # Ensure footer area is visible
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

    # Anchor on a known footer link to ensure we're at/near the footer
    await page.get_by_role("link", name="Guidelines").scroll_into_view_if_needed()

    # The footer search input is typically the only textbox on the page and often unlabeled
    search_box = page.get_by_role("textbox").first

    await search_box.click()
    await search_box.fill("rust programming")

    # Submit search (navigates away)
    await search_box.press("Enter")
    await page.wait_for_load_state("domcontentloaded")