async def amazon_sg_search_within_department(
    page, department_name: str, query: str
) -> None:
    """Search Amazon.sg within a selected department and submit the search.

    What this skill does
    --------------------
    1) Opens the Amazon.sg homepage.
    2) If a regional interstitial appears ("Stay on Amazon.sg" vs "Go to Amazon.com"),
       it clicks "Stay on Amazon.sg" to proceed on Amazon.sg.
    3) In the header search bar (scoped to the "Primary" navigation):
       - selects a department from the department dropdown (<select>)
       - fills the search query
       - clicks the "Go" button to submit the search (this triggers navigation)

    Parameters
    ----------
    page:
        Playwright Page object.
    department_name:
        Visible label of the department option (e.g., "Electronics", "Books").
        This must match an existing option label in the dropdown.
    query:
        Search keywords to enter.

    Notes / unexpected behavior
    ---------------------------
    - Amazon.sg may sometimes show a region-selection interstitial on the homepage.
      Observed link text: "Stay on Amazon.sg". Clicking it dismisses the interstitial.
    - The department dropdown behaves like a native <select>, so `select_option(label=...)`
      is the most reliable interaction.
    - Clicking "Go" navigates to a results page. If you need to interact with results
      immediately after calling this skill, wait for navigation/load state in the caller.

    Usage log
    ---------
    - 2025-12-24: Selected department "Electronics", searched "headphones", clicked "Go".
      Results page displayed successfully. The "Stay on Amazon.sg" interstitial was present
      and had to be dismissed.
    """
    await page.goto("/")
    stay_link = page.get_by_role("link", name="Stay on Amazon.sg")
    if await stay_link.count() > 0:
        await stay_link.first.click()
        await page.wait_for_load_state("domcontentloaded")
    primary_nav = page.get_by_role("navigation", name="Primary")
    search_region = primary_nav.get_by_role("search")
    await search_region.get_by_role("combobox").select_option(label=department_name)
    await search_region.get_by_role("searchbox", name="Search Amazon.sg").fill(query)
    await search_region.get_by_role("button", name="Go").click()
