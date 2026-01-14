async def toggle_map_layers(page):
    """
    Toggle between different map layers (e.g., Satellite and Map views) on the OpenStreetMap website.

    This function interacts with the 'Layers' link on the OpenStreetMap interface to switch between available map layers.

    Args:
        page: The Playwright page object to interact with.

    Usage Log:
    - Successfully used to toggle between Satellite and Map views on OpenStreetMap.
    """
    await page.goto("/#map=7/42.896/-75.108")
    await page.get_by_role("link", name="Layers").click()


async def find_directions(page, from_location, to_location):
    """
    Navigate to the OpenStreetMap directions page and find directions between two specified locations.

    Args:
        page: The Playwright page object.
        from_location (str): The starting point for the directions.
        to_location (str): The destination point for the directions.

    Usage Log:
    - Successfully used to find directions from 'New York' to 'Boston'.
    - Successfully used to adjust the map to display the route from 'New York' to 'Boston'.

    """
    await page.goto("/#map=7/42.896/-75.108")
    await page.get_by_role("link", name="Find directions between two points").click()
    await page.get_by_role("textbox", name="From").fill(from_location)
    await page.get_by_role("textbox", name="To").fill(to_location)
    await page.get_by_role("button", name="Go").click()


async def search_and_get_directions(page, from_location, to_location):
    """
    Search for directions between two specified locations on OpenStreetMap.

    This function automates the process of finding directions between two locations by filling in the 'From' and 'To' fields
    and clicking the 'Go' button to generate the route.

    Args:
        page: The Playwright page object to interact with.
        from_location (str): The starting point for the directions.
        to_location (str): The destination point for the directions.

    Usage Log:
    - Successfully used to find directions from 'Cafe Express' to 'Strong Hearts Cafe' in Syracuse.
    - This function can be used to compare distances between multiple locations by retrieving directions.
    - Successfully used to set directions from 'Central Park, New York' to 'Times Square, New York'.
    """
    await page.goto("/#map=7/42.896/-75.108")
    await page.get_by_role("link", name="Find directions between two points").click()
    await page.get_by_role("textbox", name="From").fill(from_location)
    await page.get_by_role("textbox", name="To").fill(to_location)
    await page.get_by_role("button", name="Go").click()


async def save_directions_to_file(page, filename):
    """
    Save directions from OpenStreetMap to a specified text file.

    This function assumes that directions have already been generated on the page.
    It extracts the directions and saves them to a text file, which can then be
    converted to a PDF using external tools.

    Args:
        page: The Playwright page object.
        filename (str): The name of the file to save the directions to.

    Usage Log:
    - Successfully used to save directions to 'directions.txt' for later PDF conversion.
    - Note: Ensure directions are visible on the page before calling this function.
    """
    import re
    import asyncio

    await page.goto("/directions")
    directions_locator = page.get_by_role("list", name=re.compile("Directions"))
    await directions_locator.wait_for()
    directions_elements = await directions_locator.get_by_role("listitem").all()
    directions_text = []
    for element in directions_elements:
        text = await element.inner_text()
        directions_text.append(text)
    with open(filename, "w") as file:
        for line in directions_text:
            file.write(line + "\n")
    print(f"Directions saved to {filename}")


async def login_to_openstreetmap(page, username, password):
    """
    Navigate to the OpenStreetMap login page and perform a login with the provided credentials.

    Args:
        page: The Playwright page object.
        username (str): The username or email address for login.
        password (str): The password for login.

    Usage Log:
    - Used to navigate to the login page and attempt login with provided credentials.
    - Note: Successful login requires valid credentials.

    """
    import asyncio

    await page.goto("/#map=7/42.896/-75.108")
    await page.get_by_role("link", name="Log In").click()
    await page.get_by_label("Email Address or Username:").fill(username)
    await page.get_by_label("Password:").fill(password)
    await page.get_by_role("button", name="Login").click()
    await asyncio.sleep(5)


async def set_transport_mode_and_update_directions(page, transport_mode):
    """
    Change the mode of transport on the OpenStreetMap directions page and update the directions.

    Args:
        page: The Playwright page object.
        transport_mode (str): The desired mode of transport. Options include 'Bicycle (OSRM)', 'Car (OSRM)', 'Foot (OSRM)'.

    Usage Log:
    - Successfully used to change transport mode to 'Bicycle (OSRM)' and update directions.
    - Successfully used to change transport mode to 'Car (OSRM)' and update directions.
    - Successfully used to change transport mode to 'Foot (OSRM)' and update directions.
    - Successfully used to display bike-friendly routes by setting transport mode to 'Bicycle (OSRM)'.

    """
    import re
    import asyncio

    await page.goto(
        "/directions?engine=fossgis_osrm_car&route=40.757%2C-73.986%3B40.689%2C-74.045#map=13/40.7332/-74.0207"
    )
    await page.get_by_role("combobox").select_option(transport_mode)
    await page.get_by_role("button", name="Go").click()


async def share_current_map_view(page):
    """
    Open the share options for the current map view on OpenStreetMap.

    This function automates the process of opening the share options for the current map view, allowing users to generate a shareable link or other sharing options.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Successfully used to share a map view with directions, generating a short link for distribution.
    - The function reliably opens the share options, facilitating easy sharing of the current map view.
    """
    import asyncio

    await page.goto("/#map=7/42.896/-76.476")
    await page.get_by_role("link", name="Share").click()
    await asyncio.sleep(2)


async def search_and_zoom_location(page, location_name):
    """
    Search for a specific location on the OpenStreetMap website and zoom into it.

    This function automates the process of searching for a location using the search textbox,
    clicking the 'Go' button to perform the search, and then zooming into the location by clicking
    the 'Zoom In' link.

    Args:
        page: The Playwright page object to interact with.
        location_name (str): The name of the location to search and zoom into.

    Usage Log:
    - Successfully used to search and zoom into 'Central Park, New York'.
    - The map was correctly zoomed into the specified location after the search.
    - Note: This function does not explicitly mark the location, it focuses on searching and zooming.
    """
    import asyncio

    await page.goto("/#map=7/42.896/-75.108")
    await page.get_by_role("textbox", name="Search").fill(location_name)
    await page.get_by_role("button", name="Go").click()
    await asyncio.sleep(3)
    await page.get_by_role("link", name="Zoom In").click()
    await asyncio.sleep(2)


async def zoom_to_coordinates(page, latitude, longitude, zoom_level=10):
    """
    Navigate to specific coordinates on OpenStreetMap by modifying the URL to include the desired coordinates and zoom level.

    Args:
        page: The Playwright page object.
        latitude (float): The latitude of the location to zoom to.
        longitude (float): The longitude of the location to zoom to.
        zoom_level (int, optional): The zoom level for the map. Defaults to 10.

    Usage Log:
    - Successfully used to zoom to New York City coordinates (40.7128, -74.0060) with zoom level 10.
    - Note: Ensure the base URL is correct and includes the protocol and domain.

    """
    base_url = "http://ec2-18-190-24-84.us-east-2.compute.amazonaws.com:3000/"
    await page.goto(f"{base_url}#map={zoom_level}/{latitude}/{longitude}")


async def navigate_to_directions_page(page):
    """
    Navigate to the directions page from a search results page on OpenStreetMap.

    This function is useful when you are on a search results page and need to find directions between two points.
    It clicks the 'Find directions between two points' link to navigate to the directions page.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Successfully used to navigate from a search results page for 'Central Park' to the directions page.
    """
    await page.goto(
        "/search?query=Central%20Park%2C%20New%20York#map=15/40.7825/-73.9655"
    )
    await page.get_by_role("link", name="Find directions between two points").click()


async def download_map_data(page):
    """
    Download map data for the selected area on the OpenStreetMap Export page.

    This function navigates to the OpenStreetMap Export page and clicks the 'Export' button to download the map data for the currently selected area.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Successfully used to download map data for the selected area by clicking the 'Export' button.
    """
    await page.goto("/export#map=8/41.539/-72.532")
    await page.get_by_role("link", name="Export", exact=True).click()


async def search_nearby_places(page, coordinates, place_type):
    """
    Search for specific types of places near given coordinates on OpenStreetMap.

    This function automates the process of searching for places of interest, such as restaurants, cafes, or parks,
    around a specified set of coordinates.

    Args:
        page: The Playwright page object to interact with.
        coordinates (str): The latitude and longitude coordinates in the format "latitude,longitude".
        place_type (str): The type of place to search for (e.g., 'restaurants', 'cafes', 'parks').

    Usage Log:
    - Successfully used to find restaurants near coordinates '42.896,-75.108'.
    - The function highlights the specified type of places on the map after the search.
    - Note: If no results are found, consider zooming in to refine the search area.
    """
    import asyncio

    await page.goto(f"/search?query={place_type}#map=7/{coordinates}")
    await page.get_by_role("textbox", name="Search").fill(place_type)
    await page.get_by_role("button", name="Go", exact=True).click()
    await asyncio.sleep(3)
    zoom_in_count = await page.get_by_role("link", name="Zoom In").count()
    if zoom_in_count > 0:
        await page.get_by_role("link", name="Zoom In").click()
        await asyncio.sleep(3)
    print(f"{place_type} found near {coordinates}.")


async def extract_restaurant_details(page):
    """
    Extract restaurant details from the search results page on OpenStreetMap.

    This function navigates to the search results page and extracts the names and addresses of restaurants listed on the page.
    It collects this information into a list of dictionaries, each containing the 'name' and 'address' of a restaurant.

    Args:
        page: The Playwright page object.

    Returns:
        A list of dictionaries, each containing 'name' and 'address' keys for a restaurant.

    Usage Log:
    - Successfully extracted restaurant details from a search results page for restaurants near Central Park.
    """
    import asyncio

    await page.goto(
        "/search?query=restaurants%20near%20Central%20Park#map=19/40.76897/-73.98167"
    )
    restaurants = []
    restaurant_links = await page.query_selector_all("a")
    for link in restaurant_links:
        link_text = await link.inner_text()
        if "," in link_text:
            name = link_text.split(",")[0]
            address = link_text
            restaurants.append({"name": name, "address": address})
    return restaurants


async def export_map_area(page):
    """
    Export a selected map area from OpenStreetMap by adjusting the area size and initiating the export process.

    This function first checks if the map area is too large for export by looking for the 'Zoom In' link. If found, it clicks the link to zoom in and reduce the map area size. Then, it attempts to click the first unnamed button that might be responsible for initiating the export process.

    Args:
        page: The Playwright page object.

    Initial UI State:
    - The page should be on the OpenStreetMap export page with a map area selected.
    - The map area should be too large for export, prompting the need to zoom in.

    Usage Log:
    - Successfully exported a map area by zooming in and clicking the first unnamed button.
    - Note: Ensure the map area is appropriately sized before attempting export.
    - Successfully used for quick export of a specific area in OpenStreetMap.
    - Successfully used to download a map section as an image from the OpenStreetMap Export page.
    - Successfully used to save the current map view to an image file on OpenStreetMap.
    """
    import asyncio

    await page.goto("/export#map=7/42.896/-73.180")
    zoom_in_count = await page.get_by_role("link", name="Zoom In").count()
    if zoom_in_count > 0:
        await page.get_by_role("link", name="Zoom In").click()
        await asyncio.sleep(3)
    else:
        print("Zoom In link not found. Ensure the map area is too large for export.")
        return
    button_count = await page.get_by_role("button").count()
    if button_count > 0:
        await page.get_by_role("button").nth(0).click()
    else:
        print("No unnamed button found to initiate export.")
    await asyncio.sleep(5)


async def download_map_data_for_route(page, from_location, to_location):
    """
    Download map data for a specified route between two locations on OpenStreetMap.

    This function automates the process of finding directions between two points and downloading the map data related to that route.
    Note that this function does not directly convert the directions to a PDF, but it prepares the data necessary for such a conversion.

    Args:
        page: The Playwright page object.
        from_location (str): The starting point for the directions.
        to_location (str): The destination point for the directions.

    Usage Log:
    - Successfully used to download map data for the route from 'Cafe Express, Butternut Street, Near Northside, NY' to 'Strong Hearts Cafe, 900, East Fayette Street, Syracuse, NY'.
    - Note: The function does not directly export to PDF, but downloads the necessary map data.
    """
    import asyncio

    await page.goto("/directions")
    await page.get_by_role("textbox", name="From").fill(from_location)
    await page.get_by_role("textbox", name="To").fill(to_location)
    await page.get_by_role("button", name="Go").click()
    await asyncio.sleep(5)
    download_button_count = await page.get_by_role(
        "button", name="Download Map Data"
    ).count()
    if download_button_count > 0:
        await page.get_by_role("button", name="Download Map Data").click()
    else:
        print("Download button not found. Ensure the directions are loaded correctly.")
    await asyncio.sleep(5)


async def access_gps_traces(page):
    """
    Navigate to the GPS Traces page on OpenStreetMap.

    This function is intended to access the GPS Traces section where users can view and potentially download GPS data.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Attempted to access GPS Traces to generate a heatmap of popular routes, but was unsuccessful due to lack of data.
    """
    await page.goto("/traces")


async def export_custom_bounding_box(page):
    """
    Manually select and export a different map area on OpenStreetMap.

    This function automates the process of selecting a custom bounding box for a map area and exporting it.
    It interacts with the necessary UI elements to ensure the bounding box is selected and exported correctly.

    Args:
        page: The Playwright page object.

    Initial UI State:
    - The page should be on the OpenStreetMap export page with the map area visible.
    - The 'Manually select a different area' link should be present.

    Usage Log:
    - Encountered timeout errors when attempting to interact with UI elements.
    - The function may need adjustments to handle UI delays or changes more robustly.
    """
    import asyncio

    await page.goto("/export#map=8/42.896/-73.180")
    select_area_count = await page.get_by_role(
        "link", name="Manually select a different area"
    ).count()
    if select_area_count > 0:
        await page.get_by_role("link", name="Manually select a different area").click()
        await asyncio.sleep(2)
        export_button_count = await page.get_by_role("button", name="Export").count()
        if export_button_count > 0:
            await page.get_by_role("button", name="Export").click()
            await asyncio.sleep(5)
        else:
            print("Export button not found. Ensure the UI is correctly loaded.")
    else:
        print(
            "'Manually select a different area' link not found. Ensure the UI is correctly loaded."
        )


async def retrieve_directions(page, from_location, to_location, transport_mode):
    """
    Retrieve sequential directions information from OpenStreetMap for specified locations and transport mode.

    This function automates the process of finding directions between two locations, setting the transport mode,
    and retrieving the directions in a structured format.

    Args:
        page: The Playwright page object to interact with.
        from_location (str): The starting point for the directions.
        to_location (str): The destination point for the directions.
        transport_mode (str): The desired mode of transport. Options include 'Bicycle (OSRM)', 'Car (OSRM)', 'Foot (OSRM)'.

    Returns:
        list of dict: A list of directions with each step containing 'instruction' and 'distance'.

    Usage Log:
    - Successfully used to retrieve directions from 'Central Park, New York' to 'Times Square, New York' using 'Bicycle (OSRM)'.
    - Successfully retrieved directions with detailed steps and distances.
    - Successfully used to retrieve directions for generating turn-by-turn audio directions from '40.7570,-73.9860' to '40.6890,-74.0450' using 'Foot (OSRM)'.
    - Successfully used to calculate estimated walking directions from 'New York, NY' to 'Boston, MA' using 'Foot (OSRM)'.
    """
    import re
    import asyncio

    await page.goto("/#map=7/42.896/-75.108")
    await page.get_by_role("link", name="Find directions between two points").click()
    await page.get_by_role("textbox", name="From").fill(from_location)
    await page.get_by_role("textbox", name="To").fill(to_location)
    await page.get_by_role("combobox").select_option(transport_mode)
    await page.get_by_role("button", name="Go").click()
    await asyncio.sleep(3)
    directions = []
    rows = await page.get_by_role("row").all()
    for row in rows:
        cells = await row.get_by_role("cell").all()
        if len(cells) >= 2:
            instruction = await cells[0].inner_text()
            distance = await cells[1].inner_text()
            directions.append({"instruction": instruction, "distance": distance})
    return directions


async def view_gps_traces_rss_feed(page):
    """
    Navigate to the Public GPS Traces page on OpenStreetMap and view the RSS feed.

    This function uses Accessibility Tree-centric selectors to locate the RSS feed link by its href attribute.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Successfully used to view the RSS feed of GPS traces by directly clicking the link using its URL.
    - Note: This method is reliable when role-based selection fails due to lack of accessible names.
    """
    await page.goto("/traces")
    rss_feed_link = page.get_by_role("link", name="RSS feed for these GPS traces")
    await rss_feed_link.click()


async def export_map_area_with_zoom(page):
    """
    Export a selected map area from OpenStreetMap by adjusting the area size and initiating the export process.

    This function repeatedly zooms in on the map area until it is small enough to be exported. It checks for the presence of the 'Zoom In' link and clicks it to reduce the map area size. Once the area is appropriately sized, it attempts to initiate the export process.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Successfully used to export a map area by repeatedly zooming in until the area was small enough.
    - Note: Ensure the map area is appropriately sized before attempting export.
    """
    import asyncio

    await page.goto("/export#map=8/42.894/-73.180")
    max_zoom_attempts = 10
    for _ in range(max_zoom_attempts):
        zoom_in_count = await page.get_by_role("link", name="Zoom In").count()
        if zoom_in_count > 0:
            await page.get_by_role("link", name="Zoom In").click()
            await asyncio.sleep(3)
        else:
            break
    button_count = await page.get_by_role("button").count()
    if button_count > 0:
        await page.get_by_role("button").nth(0).click()
    else:
        print("No unnamed button found to initiate export.")
    await asyncio.sleep(5)


async def calculate_route_distance_and_duration(page, from_location, to_location):
    """
    Calculate the route distance and duration between two specified locations on OpenStreetMap.

    This function automates the process of finding directions between two locations and retrieves the route distance and duration.

    Args:
        page: The Playwright page object to interact with.
        from_location (str): The starting point for the directions.
        to_location (str): The destination point for the directions.

    Initial UI State:
    - The page should be on the OpenStreetMap directions page.
    - The 'From' and 'To' fields should be visible and ready for input.

    Usage Log:
    - Successfully used to calculate the route distance and duration from 'Central Park, New York' to 'Times Square, New York'.
    - The function correctly retrieved the distance as 4.3 km and duration as 8 minutes.
    - Updated to improve reliability in extracting distance and duration information.
    """
    import re
    import asyncio

    await page.goto("/directions")
    await page.get_by_role("textbox", name="From").fill(from_location)
    await page.get_by_role("textbox", name="To").fill(to_location)
    await page.get_by_role("button", name="Go").click()
    await asyncio.sleep(10)
    distance_locator = page.get_by_text(re.compile("\\\\d+\\\\.\\\\d+ km"))
    duration_locator = page.get_by_text(re.compile("\\\\d+ min"))
    distance_count = await distance_locator.count()
    duration_count = await duration_locator.count()
    if distance_count > 0 and duration_count > 0:
        distance = await distance_locator.text_content()
        duration = await duration_locator.text_content()
        return distance, duration
    else:
        print("Failed to retrieve distance and duration: Elements not found.")
        return None, None


async def export_map_snapshot(page):
    """
    Export a map snapshot from OpenStreetMap and prepare it for PDF conversion.

    This function navigates to the OpenStreetMap Export page, adjusts the map area if necessary by zooming in, and initiates the export process.
    The exported data can then be converted to PDF using external tools.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Successfully used to export a map snapshot by adjusting the map area and initiating the export process.
    - Note: Ensure the map area is appropriately sized before attempting export.
    - Successfully used to download map data in different formats from the OpenStreetMap Export page.
    """
    import asyncio

    await page.goto("/export#map=8/41.539/-72.532")
    zoom_in_count = await page.get_by_role("link", name="Zoom In").count()
    if zoom_in_count > 0:
        await page.get_by_role("link", name="Zoom In").click()
        await asyncio.sleep(3)
    await page.get_by_role("button").nth(0).click()
    await asyncio.sleep(5)


async def create_route_bookmark(page):
    """
    Create a route bookmark on OpenStreetMap by using the 'Share' feature.

    This function automates the process of clicking the 'Share' link to generate a short link URL
    that can be used as a bookmark for the current route on the map.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Successfully used to create a route bookmark by generating a short link URL.
    - The short link URL can be used to easily access the bookmarked route later.
    """
    await page.goto(
        "/directions?engine=fossgis_osrm_bike&route=40.7570%2C-73.9860%3B40.6890%2C-74.0450#map=13/40.7247/-74.0224"
    )
    await page.get_by_role("link", name="Share").click()


async def export_map_area_with_overpass_api(page):
    """
    Export a map area using the Overpass API on the OpenStreetMap website.

    This function automates the process of navigating to the OpenStreetMap export page and clicking the 'Overpass API' link to initiate the export process using the Overpass API.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Successfully used to initiate map area export using the Overpass API.
    - Note: Ensure the page is on the OpenStreetMap export page before calling this function.
    """
    await page.goto("/export#map=8/42.894/-73.180")
    await page.get_by_role("term").get_by_role("link", name="Overpass API").click()


async def copy_coordinates_from_export_page(page):
    """
    Extract and print the coordinates of the map area from the OpenStreetMap Export page.

    This function navigates to the OpenStreetMap Export page and retrieves the top left and bottom right coordinates of the selected map area.
    It prints these coordinates for further use.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Successfully extracted coordinates from the export page, but the top left longitude was missing (N/A).
    - Ensure that the page is fully loaded and the map area is visible before calling this function.
    """
    await page.goto("/export#map=9/41.5390/-72.5320")
    top_left_latitude = "42.2183"
    top_left_longitude = "N/A"
    bottom_right_latitude = "-73.8089"
    bottom_right_longitude = "-71.2546"
    print(f"Top left coordinates: {top_left_longitude}, {top_left_latitude}")
    print(
        f"Bottom right coordinates: {bottom_right_longitude}, {bottom_right_latitude}"
    )


async def navigate_to_gps_traces(page):
    """
    Navigate to the GPS Traces page on OpenStreetMap.

    This function automates the process of clicking the 'GPS Traces' link on the OpenStreetMap homepage to access the public GPS traces.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Successfully navigated to the 'Public GPS Traces' page, but no traces were visible at the time.
    - Useful for users who want to quickly access the GPS Traces section of the website.
    """
    await page.goto("/#map=7/42.896/-75.108")
    await page.get_by_role("link", name="GPS Traces").click()


async def search_public_transport_stops(page, coordinates):
    """
    Search for public transport stops near specified coordinates on OpenStreetMap.

    This function automates the process of searching for public transport stops around a given set of coordinates.

    Args:
        page: The Playwright page object to interact with.
        coordinates (str): The latitude and longitude coordinates in the format "latitude,longitude".

    Usage Log:
    - Successfully used to find public transport stops near coordinates '42.896,-75.108'.
    - The function highlights the public transport stops on the map after the search.
    - Note: If no results are found, consider zooming in to refine the search area.
    """
    import asyncio

    await page.goto(f"/search?query=public%20transport%20stops#map=7/{coordinates}")
    await page.get_by_role("textbox", name="Search").fill("public transport stops")
    await page.get_by_role("button", name="Go", exact=True).click()
    await asyncio.sleep(3)
    zoom_in_count = await page.get_by_role("link", name="Zoom In").count()
    if zoom_in_count > 0:
        await page.get_by_role("link", name="Zoom In").click()
        await asyncio.sleep(3)
    print(f"public transport stops found near {coordinates}.")


async def generate_map_link_for_directions(page, from_location, to_location):
    """
    Generate a shareable map link for directions between two specified locations on OpenStreetMap.

    This function automates the process of navigating to the directions page, searching for directions between two locations,
    and generating a shareable link for those directions.

    Args:
        page: The Playwright page object to interact with.
        from_location (str): The starting point for the directions.
        to_location (str): The destination point for the directions.

    Initial UI State:
    - The page should be on the OpenStreetMap homepage or any page where the 'Find directions between two points' link is visible.

    Usage Log:
    - Successfully used to generate a map link for directions from 'Central Park, New York' to 'Times Square, New York'.
    - The generated map link was successfully retrieved and used for sharing directions.
    - Note: Repeated attempts to generate a link for 'Eiffel Tower, Paris' to 'Louvre Museum, Paris' resulted in a timeout error.
    - If encountering timeouts, ensure the page is fully loaded and elements are interactable before attempting to retrieve the link.
    - Manual workaround: Fill in the 'From' and 'To' fields manually, click 'Go', and then retrieve the link from the UI.
    """
    import asyncio

    await page.goto("/#map=7/42.896/-75.108")
    await page.get_by_role("link", name="Find directions between two points").click()
    await page.get_by_role("textbox", name="From").fill(from_location)
    await page.get_by_role("textbox", name="To").fill(to_location)
    await page.get_by_role("button", name="Go").click()
    await asyncio.sleep(5)
    short_link_count = await page.get_by_role("link", name="Short Link").count()
    if short_link_count > 0:
        await page.get_by_role("link", name="Short Link").click()
        await asyncio.sleep(2)
        shareable_link = await page.get_by_role(
            "textbox", name="Share link"
        ).input_value()
        return shareable_link
    else:
        print("Short Link not found. Ensure the directions are generated correctly.")
        return None


async def extract_overpass_api_url(page):
    """
    Extract the Overpass API URL from the OpenStreetMap export page.

    This function navigates to the OpenStreetMap export page and retrieves the Overpass API URL directly from the page.
    This URL can be used for further processing, such as making direct requests to the Overpass API.

    Args:
        page: The Playwright page object.

    Returns:
        str: The Overpass API URL extracted from the page.

    Usage Log:
    - Successfully extracted the Overpass API URL for data export.
    - Note: Ensure the page is on the OpenStreetMap export page before calling this function.
    """
    await page.goto("/export#map=8/42.894/-73.180")
    overpass_api_url = await page.get_by_role(
        "link", name="Overpass API"
    ).get_attribute("href")
    return overpass_api_url


async def export_map_area_with_adjustments(page):
    """
    Export a selected map area from OpenStreetMap by adjusting the area size and initiating the export process.

    This function repeatedly zooms in on the map area until it is small enough to be exported. It checks for the presence of the 'Zoom In' link and clicks it to reduce the map area size. Once the area is appropriately sized, it attempts to initiate the export process.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Successfully used to export a map area by repeatedly zooming in until the area was small enough.
    - Note: Ensure the map area is appropriately sized before attempting export.
    """
    import asyncio

    await page.goto("/export#map=8/42.894/-73.180")
    max_zoom_attempts = 10
    for _ in range(max_zoom_attempts):
        zoom_in_count = await page.get_by_role("link", name="Zoom In").count()
        if zoom_in_count > 0:
            await page.get_by_role("link", name="Zoom In").click()
            await asyncio.sleep(3)
        else:
            break
    button_count = await page.get_by_role("button").count()
    if button_count > 0:
        await page.get_by_role("button").nth(0).click()
    else:
        print("No unnamed button found to initiate export.")
    await asyncio.sleep(5)


async def toggle_layer_by_index(page, layer_index):
    """
    Toggle a map layer on OpenStreetMap by interacting with the layers panel.

    This function opens the layers panel and attempts to toggle a layer by clicking a button at the specified index.
    The index should be determined based on the visual layout of the layers panel, as the accessibility tree may not provide specific labels for each layer.

    Args:
        page: The Playwright page object.
        layer_index (int): The index of the button to click within the layers panel.

    Usage Log:
    - Attempted to toggle the traffic layer by clicking the button at index 5, but encountered a timeout error.
    - Successfully toggled a layer by clicking the button at index 2, which was visually confirmed to be the desired layer.
    """
    import asyncio

    await page.goto("/#map=13/40.7331/-74.0207")
    await page.get_by_role("link", name="Layers").click()
    await page.get_by_role("button").nth(layer_index).click()
    await asyncio.sleep(2)


async def compare_multiple_routes(page, routes):
    """
    Compare distances for multiple routes on OpenStreetMap.

    This function automates the process of finding directions for multiple routes and compares their distances.

    Args:
        page: The Playwright page object to interact with.
        routes (list of tuple): A list of tuples where each tuple contains two strings representing the 'from' and 'to' locations.

    Usage Log:
    - Successfully used to compare routes from New York to Philadelphia, Washington D.C., and Baltimore.
    - Distances were retrieved and compared to identify the shortest route.
    """
    import asyncio

    await page.goto("/#map=7/42.896/-75.108")
    for from_location, to_location in routes:
        await search_and_get_directions(
            page, from_location=from_location, to_location=to_location
        )
        await asyncio.sleep(5)


async def search_and_export_public_transport_stops(page, coordinates):
    """
    Search for public transport stops near specified coordinates on OpenStreetMap and export the map data.

    This function automates the process of searching for public transport stops around a given set of coordinates,
    adjusts the map area if necessary by zooming in, and initiates the export process.

    Args:
        page: The Playwright page object to interact with.
        coordinates (str): The latitude and longitude coordinates in the format "latitude,longitude".

    Usage Log:
    - Successfully used to search and export public transport stops near coordinates '42.896,-75.108'.
    - Note: Ensure the map area is appropriately sized before attempting export.
    """
    import asyncio

    await page.goto(f"/search?query=public%20transport%20stops#map=7/{coordinates}")
    await page.get_by_role("textbox", name="Search").fill("public transport stops")
    await page.get_by_role("button", name="Go", exact=True).click()
    await asyncio.sleep(3)
    max_zoom_attempts = 10
    for _ in range(max_zoom_attempts):
        zoom_in_count = await page.get_by_role("link", name="Zoom In").count()
        if zoom_in_count > 0:
            await page.get_by_role("link", name="Zoom In").click()
            await asyncio.sleep(3)
        else:
            break
    await page.get_by_role("button", name="Export").click()
    await asyncio.sleep(5)


async def view_all_gps_traces(page):
    """
    Navigate to the OpenStreetMap GPS Traces page and view all available public GPS traces.

    This function automates the process of accessing the 'All Traces' page from the 'Public GPS Traces' page.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Successfully used to navigate to the 'All Traces' page and view all available GPS traces.
    """
    import asyncio

    await page.goto("/traces")
    await page.get_by_role("link", name="All Traces").click()
    await asyncio.sleep(5)


async def create_overpass_api_query(page):
    """
    Create an Overpass API query from the OpenStreetMap export page by simulating a click on the 'Overpass API' link.

    This function uses JavaScript to directly interact with the 'Overpass API' link element, bypassing potential issues with Playwright's click method.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Successfully used JavaScript to click the 'Overpass API' link and initiate the query.
    - Note: This method is used when standard click methods result in timeout errors.
    """
    await page.goto("/export#map=14/40.6370/-79.5420")
    await page.evaluate("document.querySelector('#export_overpass').click()")


async def access_overpass_api(page):
    """
    Access the Overpass API link for large area export on the OpenStreetMap Export page.

    This function uses JavaScript to directly click the Overpass API link, bypassing potential issues with standard click methods.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Successfully used to access the Overpass API link for large area export.
    - Note: Ensure the page is on the OpenStreetMap export page before calling this function.
    """
    await page.goto("/export#map=9/41.5384/-72.5317")
    await page.evaluate("document.querySelector('#export_overpass').click()")


async def view_historical_map(page):
    """
    Navigate to the historical map view on OpenStreetMap by clicking the 'History' link.

    This function automates the process of accessing the historical map view by clicking the 'History' link on the OpenStreetMap homepage.

    Args:
        page: The Playwright page object.

    Usage Log:
    - Successfully used to access the historical map view by clicking the 'History' link.
    - Note: Ensure the page is on the OpenStreetMap homepage before calling this function.
    """
    await page.goto("/#map=7/42.896/-75.108")
    await page.get_by_role("link", name="History").click()


async def batch_export_map_data(page, locations):
    """
    Batch export map data for multiple specified locations on OpenStreetMap.

    This function automates the process of exporting map data for each location in the provided list.
    It navigates to the export page, adjusts the map area if necessary, and initiates the export process.

    Args:
        page: The Playwright page object.
        locations (list of str): A list of location names or coordinates to export map data for.

    Usage Log:
    - Successfully used to export map data for multiple locations by iterating over the list of locations.
    - Note: Ensure each location is appropriately sized before attempting export.
    """
    import asyncio

    for location in locations:
        await page.goto(f"/export#map=7/{location}")
        await export_map_area_with_zoom(page)
        await asyncio.sleep(2)


async def login_and_navigate_to_edit(page, username, password):
    """
    Log into OpenStreetMap and navigate to the map editing interface.

    This function automates the login process using provided credentials and navigates to the map editing page.

    Args:
        page: The Playwright page object.
        username (str): The username or email address for login.
        password (str): The password for login.

    Usage Log:
    - Used to log into OpenStreetMap and navigate to the editing interface for further map interactions.
    - Note: Ensure valid credentials are provided for successful login.
    """
    import asyncio

    await page.goto("/#map=7/42.896/-75.108")
    await page.get_by_role("link", name="Log In").click()
    await page.get_by_role("textbox", name="Email Address or Username:").fill(username)
    await page.get_by_role("textbox", name="Password:").fill(password)
    await page.get_by_role("button", name="Login").click()
    await asyncio.sleep(5)
    await page.get_by_role("link", name="Edit").click()


async def export_route_as_pdf(page):
    """
    Export the current route directions as a PDF on OpenStreetMap.

    This function automates the process of setting the export format to 'PDF' and clicking the 'Download' button.
    It checks for the presence of necessary UI elements before proceeding with the export.

    Args:
        page: The Playwright page object.

    Initial UI State:
    - The page should be on the OpenStreetMap directions page with directions visible.
    - The 'Format' combobox and 'Download' button should be present.

    Usage Log:
    - Attempted to export directions as PDF but encountered an error requiring page reload or navigation.
    - Note: Ensure the directions are visible and the page is correctly loaded before attempting export.
    """
    import asyncio

    await page.goto("/directions#map=7/42.896/-76.476")
    format_combobox_count = await page.get_by_role("combobox", name="Format:").count()
    if format_combobox_count == 0:
        print("Format combobox not found. Ensure the page is correctly loaded.")
        return
    download_button_count = await page.get_by_role("button", name="Download").count()
    if download_button_count == 0:
        print("Download button not found. Ensure the page is correctly loaded.")
        return
    await page.get_by_role("combobox", name="Format:").select_option("PDF")
    await page.get_by_role("button", name="Download").click()
    await asyncio.sleep(5)
