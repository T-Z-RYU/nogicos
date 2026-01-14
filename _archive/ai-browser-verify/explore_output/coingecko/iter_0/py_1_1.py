import asyncio, re
from skillweaver.agent import vars

(print,) = vars['C:\\Users\\WIN\\Desktop\\Cursor Project\\ai-browser-verify\\explore_output\\coingecko\\iter_0\\py_1_1.py']



import asyncio

async def act(page):
    main = page.get_by_role("main")

    # Filter by a chosen (sub)category within Derivatives: Perpetuals
    await main.get_by_role("button", name="Perpetuals").click()
    await asyncio.sleep(2)

    # Sort by selected metric: 24h change (descending)
    # Click once, then click again to ensure descending order.
    table = main.get_by_role("table")
    header_24h = table.get_by_role("columnheader", name="24h")
    await header_24h.click()
    await asyncio.sleep(1)
    await header_24h.click()
    await asyncio.sleep(2)