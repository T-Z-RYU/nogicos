async def go_to_product_catalog(page):
    """
    Navigates to the Product Catalog section from the Magento Admin Dashboard.

    This function first clicks on the 'Catalog' link available in the menubar,
    and then clicks on the 'Products' link in the Catalog submenu to reach the
    Product Catalog page.

    Usage Log:
    - Initially attempted to directly click 'Catalog' which was not sufficient
      to reach the Product Catalog. Adjusted path to include 'Products' submenu link.
    - Encountered a timeout error when trying to click 'Products', revised approach
      ensured successful navigation.

    """
    await page.goto("/admin/admin/dashboard/")
    await page.get_by_role("menubar").get_by_role("link", name="Catalog").click()
    await page.get_by_role("menubar").get_by_role("menu").get_by_role(
        "link", name="Products"
    ).click()


async def extract_product_data(page):
    """
    [Function description]
    Extracts all product information present in the table on the current page.

    This function automates the retrieval of product details from a table, including:
    - IDs
    - Names
    - Types
    - Attribute Sets
    - SKUs
    - Prices
    - Quantities
    - Visibility
    - Status
    - Websites
    - Last Updated Dates

    [Usage preconditions]
    - This API retrieves product data which is visible in the current table structure on the page.
    - **You must already be on a Magento Admin product page where the product table is available**.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the product details.
    """
    await page.goto("/admin/catalog/product/")
    products = []
    rows = await page.query_selector_all("table tr")
    for row in rows[1:]:
        cells = await row.query_selector_all("td")
        if cells:
            product = {
                "id": await cells[1].inner_text(),
                "name": await cells[2].inner_text(),
                "type": await cells[3].inner_text(),
                "attribute_set": await cells[4].inner_text(),
                "sku": await cells[5].inner_text(),
                "price": await cells[6].inner_text(),
                "quantity": await cells[7].inner_text(),
                "visibility": await cells[9].inner_text(),
                "status": await cells[10].inner_text(),
                "websites": await cells[11].inner_text(),
                "last_updated": await cells[12].inner_text(),
            }
            products.append(product)
    return products


async def get_out_of_stock_products(page):
    """
    Retrieves a list of products with zero stock from the current page of a product inventory table.

    This function automates the extraction of product details that are listed as out of stock (quantity of 0.0000) from a table on the current web page.

    [Usage preconditions]
    - Ensure you are on the correct page displaying a table of product inventory within the Magento Admin Panel before invoking this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "name" (str): The product name.
        - "type" (str): The product type.
        - "edit_link" (str): The URL link to edit the product.
    """
    await page.goto("/admin/catalog/product/")
    products = []
    rows = await page.query_selector_all("table tr")
    for row in rows:
        quantity_cell = await row.query_selector("td:nth-child(9)")
        if quantity_cell:
            quantity_text = await quantity_cell.inner_text()
            if quantity_text.strip() == "0.0000":
                name_cell = await row.query_selector("td:nth-child(3)")
                type_cell = await row.query_selector("td:nth-child(5)")
                edit_link = await (
                    await row.query_selector("td a[href]")
                ).get_attribute("href")
                product_info = {
                    "name": await name_cell.inner_text() if name_cell else "",
                    "type": await type_cell.inner_text() if type_cell else "",
                    "edit_link": edit_link,
                }
                products.append(product_info)
    return products


async def filter_products_by_type(page, product_type):
    """
    [Function description]
    Filters products based on their type (e.g., Configurable Product, Simple Product) on the current Magento Admin page.

    [Usage preconditions]
    - This API function retrieves and filters products by type for the inventory catalog page you are currently on.
    - **You must already be on the Magento Admin products catalog page before calling this function.**

    Args:
    page: A Playwright `Page` instance that controls browser automation.
    product_type: A string specifying the type of product to filter by (e.g., 'Configurable Product', 'Simple Product').

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains product details for all products of a specific type. Each dictionary includes:
        - "name" (str): The name of the product.
        - "type" (str): The type of product.
        - "sku" (str): The SKU of the product.
        - "price" (str): The price of the product.
    """
    await page.goto("/admin/catalog/product/")
    rows = await page.query_selector_all("table tr")
    products = []
    for row in rows:
        type_cell = await row.query_selector("td:nth-child(5)")
        product_type_text = await (
            await type_cell.get_property("innerText")
        ).json_value()
        if product_type_text.strip() == product_type:
            name_cell = await row.query_selector("td:nth-child(4)")
            sku_cell = await row.query_selector("td:nth-child(7)")
            price_cell = await row.query_selector("td:nth-child(8)")
            name = await (await name_cell.get_property("innerText")).json_value()
            sku = await (await sku_cell.get_property("innerText")).json_value()
            price = await (await price_cell.get_property("innerText")).json_value()
            products.append(
                {
                    "name": name.strip(),
                    "type": product_type_text.strip(),
                    "sku": sku.strip(),
                    "price": price.strip(),
                }
            )
    return products


async def navigate_to_orders_section(page):
    """
    Navigates to the Orders section from the Magento Admin Dashboard.

    This function automates the process of accessing the Orders section by first clicking on the 'Sales' link in the menubar and then selecting 'Orders' from the submenu.

    [Usage preconditions]
    - You must be authenticated and on the Magento Admin Dashboard page before invoking this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Usage log:
    - Successfully navigated to the Orders section by clicking through the Sales menu.
    """
    await page.goto("/admin/admin/dashboard/")
    sales_menu = page.get_by_role("menubar").get_by_role("link", name="\ue60b Sales")
    await sales_menu.click()
    orders_link = page.get_by_role("menu").get_by_role("link", name="Orders")
    await orders_link.click()


async def get_order_details(page):
    """
    Retrieve all orders from the current page including order details.

    This function extracts details of each order from the orders table on the page.
    For each order, it gathers information such as:
    - Order ID
    - Purchase Point
    - Purchase Date
    - Bill-to Name
    - Ship-to Name
    - Grand Total
    - Status
    - View action link

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "order_id" (str): The order ID.
        - "purchase_point" (str): The purchase point.
        - "purchase_date" (str): The date of purchase.
        - "bill_to_name" (str): The name of the person to bill.
        - "ship_to_name" (str): The name of the person to ship to.
        - "grand_total" (str): The grand total amount.
        - "status" (str): The status of the order.
        - "view_link" (str): The URL to view the order details.
    """
    await page.goto("/admin/sales/order/")
    orders = []
    row_selector = "table tr"
    rows = await page.query_selector_all(row_selector)
    for row in rows[1:]:
        order_id = await (await row.query_selector("td:nth-child(2)")).inner_text()
        purchase_point = await (
            await row.query_selector("td:nth-child(3)")
        ).inner_text()
        purchase_date = await (await row.query_selector("td:nth-child(4)")).inner_text()
        bill_to_name = await (await row.query_selector("td:nth-child(5)")).inner_text()
        ship_to_name = await (await row.query_selector("td:nth-child(6)")).inner_text()
        grand_total = await (await row.query_selector("td:nth-child(7)")).inner_text()
        status = await (await row.query_selector("td:nth-child(9)")).inner_text()
        view_url_node = await row.query_selector("td .action-menu a")
        view_link = await view_url_node.get_attribute("href") if view_url_node else None
        orders.append(
            {
                "order_id": order_id,
                "purchase_point": purchase_point,
                "purchase_date": purchase_date,
                "bill_to_name": bill_to_name,
                "ship_to_name": ship_to_name,
                "grand_total": grand_total,
                "status": status,
                "view_link": view_link,
            }
        )
    return orders


async def retrieve_pending_orders(page):
    """
    Retrieves a list of orders with 'Pending' status.

    This function automates the process of extracting order details with 'Pending'
    status from the current page of a sales dashboard. The extracted information includes:

    - Order ID
    - Customer Name
    - Order Total
    - Date

    [Usage preconditions]
    - This API retrieves order information from the sales order page **you are currently at**.
    - **You must already be on the sales orders page before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "order_id" (str): The order ID.
        - "customer_name" (str): The name of the customer.
        - "order_total" (str): The total amount of the order.
        - "date" (str): The date of the order.
    """
    await page.goto("/admin/sales/order/")
    orders = []
    rows = await page.query_selector_all("table tbody tr")
    for row in rows:
        status = await (await row.query_selector("td:nth-child(8)")).inner_text()
        if status.strip() == "Pending":
            order_id = await (await row.query_selector("td:nth-child(2)")).inner_text()
            customer_name = await (
                await row.query_selector("td:nth-child(5)")
            ).inner_text()
            order_total = await (
                await row.query_selector("td:nth-child(7)")
            ).inner_text()
            date = await (await row.query_selector("td:nth-child(4)")).inner_text()
            orders.append(
                {
                    "order_id": order_id.strip(),
                    "customer_name": customer_name.strip(),
                    "order_total": order_total.strip(),
                    "date": date.strip(),
                }
            )
    return orders


async def get_complete_orders_details(page):
    """
    Retrieves details of all orders marked as 'Complete' on the current page.

    This function automates the process of extracting order details from a page
    which lists several orders, filtering only those that are marked as 'Complete'.

    For each order, the details retrieved include:
    - Order ID
    - Purchase Date
    - Bill-to Name
    - Ship-to Name
    - Grand Total (Base)
    - Grand Total (Purchased)

    Usage preconditions:
    - This API assumes you are on a web page listing orders in the format as given on a
      Magento Admin sales order list page.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list with each dictionary containing the following keys:
        - "order_id" (str): The order ID.
        - "purchase_date" (str): The purchase date of the order.
        - "bill_to_name" (str): The bill-to name.
        - "ship_to_name" (str): The ship-to name.
        - "grand_total_base" (str): The grand total in base currency.
        - "grand_total_purchased" (str): The grand total in purchased currency.
    """
    await page.goto("/admin/sales/order/")
    orders_details = []
    order_rows = await page.query_selector_all("table tbody tr")
    for row in order_rows:
        status = await (await row.query_selector("td:nth-child(8)")).inner_text()
        if status.strip().lower() == "complete":
            order_id = await (await row.query_selector("td:nth-child(2)")).inner_text()
            purchase_date = await (
                await row.query_selector("td:nth-child(4)")
            ).inner_text()
            bill_to_name = await (
                await row.query_selector("td:nth-child(5)")
            ).inner_text()
            ship_to_name = await (
                await row.query_selector("td:nth-child(6)")
            ).inner_text()
            grand_total_base = await (
                await row.query_selector("td:nth-child(7)")
            ).inner_text()
            grand_total_purchased = await (
                await row.query_selector("td:nth-child(8)")
            ).inner_text()
            order_details = {
                "order_id": order_id.strip(),
                "purchase_date": purchase_date.strip(),
                "bill_to_name": bill_to_name.strip(),
                "ship_to_name": ship_to_name.strip(),
                "grand_total_base": grand_total_base.strip(),
                "grand_total_purchased": grand_total_purchased.strip(),
            }
            orders_details.append(order_details)
    return orders_details


async def navigate_to_categories_section(page):
    """
    Navigates to the 'Categories' section within the 'Catalog' menu of the Magento Admin interface.

    This function interacts with the Magento Admin dashboard UI to reach the Categories section.
    It first clicks the 'Catalog' option in the menubar, and then selects 'Categories' from the resulting dropdown menu.
    Ensure you are on the Magento Admin Dashboard page before using this function.

    Usage log:
    - Successfully navigated to the 'Categories' section from the Dashboard.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    None
    """
    await page.goto("/admin/admin/dashboard/")
    await page.get_by_role("menubar").get_by_role("link", name="Catalog").click()
    await page.get_by_role("menu").get_by_role("link", name="Categories").click()


async def retrieve_categories_and_subcategories(page):
    """
    [Function description]
    Extracts a complete list of categories and subcategories with their names and IDs from the Magento Admin category page.

    This function automates the extraction of category and subcategory information
    from the Magento Admin category section. It ensures that all categories and
    subcategories are visible and gathers their names and IDs.

    [Usage preconditions]
    - This API retrieves category information for the Magento Admin **you are currently at**.
    - **You must already be on the Magento Admin category page before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the category or subcategory.
        - "id" (str): The unique ID of the category or subcategory.
    """
    await page.goto("/admin/catalog/category/")
    await page.click('text="Expand All"')
    category_links = await page.query_selector_all(
        'main a[href^="#/admin/catalog/category"]'
    )
    categories = []
    for link in category_links:
        text_content = await link.inner_text()
        parts = text_content.split(" (ID: ", 1)
        if len(parts) == 2:
            name = parts[0].strip()
            id = parts[1].split(")")[0].strip()
            categories.append({"name": name, "id": id})
    return categories


async def get_top_level_categories(page):
    """
    [Function description]
    Extract the names and IDs of top-level categories from a given webpage.

    This function scans the webpage to find and compile a list of root category names and their associated IDs.

    [Usage preconditions]
    - Assume the user is on a page featuring a list of categories intended for extraction.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "id" (str): The identifier for the category.
        - "name" (str): The name of the category.
    """
    await page.goto("/admin/catalog/category/")
    category_elements = await page.query_selector_all("main link")
    categories = []
    for element in category_elements:
        category_text = await element.text_content()
        if "(ID: " in category_text:
            id_start = category_text.find("(ID: ") + len("(ID: ")
            id_end = category_text.find(")", id_start)
            category_id = category_text[id_start:id_end]
            name_end = category_text.find(" (ID:")
            category_name = category_text[:name_end]
            categories.append({"id": category_id, "name": category_name})
    return categories


async def get_subcategories(page):
    """
    [Function description]
    Retrieves all subcategory names and their IDs under a specific parent category on the Magento Admin page.

    This function automates the extraction of subcategory information for a given category by traversing the categories list and extracting relevant details for each subcategory.

    [Usage preconditions]
    - You must be already logged into the Magento Admin and positioned at the page where category information is displayed.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the subcategory.
        - "id" (str): The unique ID of the subcategory.
    """
    await page.goto("/admin/catalog/category/")
    subcategories_locator = '//main//a[contains(@href, "category")]'
    subcategory_elements = await page.query_selector_all(subcategories_locator)
    subcategories = []
    for element in subcategory_elements:
        element_text = await element.inner_text()
        if "(ID: " in element_text:
            name_part, id_part = element_text.split("(ID: ")
            category_name = name_part.strip()
            category_id = id_part.split(")")[0].strip()
            subcategories.append({"name": category_name, "id": category_id})
    return subcategories


async def navigate_to_customer_dashboard(page):
    """
    [Function description]
    Navigate to the 'All Customers' section in the Magento Admin panel, which serves as the customer dashboard.

    This function automates the navigation from the dashboard to the 'All Customers' section by interacting with the relevant menu links.

    [Usage preconditions]
    - You should be logged into the Magento Admin panel and positioned at the dashboard before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Usage log:
    - On first use, this function successfully navigated to the 'All Customers' page using menu links.
    - No unexpected behavior was observed during navigation.

    Example:
    >>> await navigate_to_customer_dashboard(page)
    """
    await page.goto("/admin/admin/dashboard/")
    await page.get_by_role("menubar").get_by_role("link", name="Customers").click()
    await page.get_by_role("menubar").get_by_role("menu").get_by_role(
        "link", name="All Customers"
    ).click()


async def get_all_reviews(page):
    '''
    [Function description]
    The API is used to retrieve all reviews from the review list page. 
    The page is about Manage and review customer feedback on products in a Magento store.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    '''
    await page.goto("/admin/review/product/index/")
    reviews = []
    extracted_ids = set()

    while True:
        current_page = await page.input_value('#reviewGrid_page-current')
        review_rows = await page.query_selector_all(
            "table#reviewGrid_table > tbody > tr"
        )
        for row in review_rows:
            columns = await row.query_selector_all("td")
            review_id_elem = columns[1]
            review_id = (await review_id_elem.inner_text()).strip()
            if review_id not in extracted_ids:
                extracted_ids.add(review_id)
                created = (await columns[2].inner_text()).strip()
                status = (await columns[3].inner_text()).strip()
                title = (await columns[4].inner_text()).strip()
                nickname = (await columns[5].inner_text()).strip()
                detail = (await columns[6].inner_text()).strip()
                product_name = (await columns[9].inner_text()).strip()
                sku = (await columns[10].inner_text()).strip()
                review_data = {
                    "review_id": review_id,
                    "created": created,
                    "status": status,
                    "title": title,
                    "nickname": nickname,
                    "detail": detail,
                    "product_name": product_name,
                    "sku": sku,
                }
                reviews.append(review_data)
        next_button = await page.query_selector(
            "div#reviewGrid .admin__data-grid-pager button.action-next:not(.disabled)"
        )
        if next_button:
            await next_button.click()
            await page.wait_for_load_state("networkidle")            
            new_page = await page.input_value('#reviewGrid_page-current')
            if new_page == current_page:
                break
        else:
            break
    return reviews


async def retrieve_all_customers(page):
    '''
    The API is used to retrieve all customers from the customer list page.
    The page is about the admin to manage customer information, conduct searches, apply filters, view and edit details, add new customers, and export data for external use. It also provides system messages to alert the admin about integration issues."
    '''
    await page.goto("/admin/customer/index/")
    customers = []
    total_records = 70  
    rows_per_page = 20  
    pages = (total_records // rows_per_page) + (1 if total_records % rows_per_page > 0 else 0)

    for _ in range(pages):
        await page.wait_for_timeout(1000) 
        data_rows = await page.query_selector_all("tbody tr")
        for row in data_rows:
            name_element = await row.query_selector("td:nth-child(2) .data-grid-cell-content")
            email_element = await row.query_selector("td:nth-child(3) .data-grid-cell-content")
            group_element = await row.query_selector("td:nth-child(4) .data-grid-cell-content")
            phone_element = await row.query_selector("td:nth-child(5) .data-grid-cell-content")
            zip_element = await row.query_selector("td:nth-child(6) .data-grid-cell-content")
            country_element = await row.query_selector("td:nth-child(7) .data-grid-cell-content")
            state_province_element = await row.query_selector("td:nth-child(8) .data-grid-cell-content")
            customer_since_element = await row.query_selector("td:nth-child(9) .data-grid-cell-content")

            customer_info = {}

            if name_element:
                customer_info["name"] = (await name_element.text_content()).strip()
            if email_element:
                customer_info["email"] = (await email_element.text_content()).strip()
            if group_element:
                customer_info["group"] = (await group_element.text_content()).strip()
            if phone_element:
                customer_info["phone"] = (await phone_element.text_content()).strip()
            if zip_element:
                customer_info["zip"] = (await zip_element.text_content()).strip()
            if country_element:
                customer_info["country"] = (await country_element.text_content()).strip()
            if state_province_element:
                customer_info["state_province"] = (await state_province_element.text_content()).strip()
            if customer_since_element:
                customer_info["customer_since"] = (await customer_since_element.text_content()).strip()

            customers.append(customer_info)

        try:
            next_button = page.locator('button.action-next')
            await next_button.click()
        except Exception:
            return customers

    customers.sort(key=lambda x: x.get('name', ''))

    return customers


async def navigate_to_media_gallery(page):
    """
    Navigates to the Media Gallery in the Magento Admin panel from the dashboard.

    This function simulates user interaction starting at the dashboard level, leveraging the menubar to
    locate and go to the Media Gallery section. The Media Gallery is typically housed under the 'Content' menu.

    [Usage Preconditions]
    - You must be logged into the Magento Admin dashboard.
    - Ensure the menubar is visible on the page.
    - This function expects the page to be fully loaded, rendering all necessary interactive elements.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Usage Log:
    - Initially faced TimeoutError due to timing constraints with menu link accessibility.
    - After corrections, successfully navigated to the Media Gallery from Dashboard.
    """
    await page.goto("/admin/admin/dashboard/")
    content_link = page.get_by_role("menubar").get_by_role(
        "link", name="Content", exact=True
    )
    if await content_link.count() == 0:
        raise Exception("Content menu link is not found on the menubar.")
    await content_link.click()
    media_gallery_link = page.get_by_role("menu").get_by_role(
        "link", name="Media Gallery"
    )
    if await media_gallery_link.count() == 0:
        raise Exception("Media Gallery link is not found under Content menu.")
    await media_gallery_link.click()


async def extract_directory_structure(page):
    """
    Extracts a hierarchical directory structure from the current page of "Manage Gallery / Media / Content / Magento Admin".

    This function interacts with the tree structure found in the main section of the Magento Admin page
    to recursively gather directory levels and their respective names under the "wysiwyg" tree group.

    Usage preconditions:
    - You must be on the Manage Gallery / Media / Content page of the Magento Admin Panel.

    Args:
    page: A Playwright Page instance that controls browser automation.

    Returns:
    dict
        A dictionary representation of the directory structure where keys are directory names
        and values are lists of subdirectory names.
    """
    await page.goto("/admin/media_gallery/media/index/")
    directory_structure = {}
    treeitems = await page.query_selector_all('[role="treeitem"]:not([aria-level="1"])')
    main_treeitems = await page.query_selector_all('[role="treeitem"][aria-level="1"]')
    for main_treeitem in main_treeitems:
        main_treeitem_name = await main_treeitem.get_attribute("innerText")
        if not main_treeitem_name:
            continue
        directory_structure[main_treeitem_name] = []
        for subitem in treeitems:
            subitem_name = await subitem.get_attribute("innerText")
            if subitem_name:
                directory_structure[main_treeitem_name].append(subitem_name)
    return directory_structure


async def retrieve_images_in_directory(page):
    """
    [Function description]
    Retrieves details for all images present in the specified directory on a media management page.

    This function automates the extraction of image details, including image names,
    upload dates, and associated tags from the selected directory (e.g., 'mens').

    [Usage preconditions]
    - You need to be on a page where directories and image content within them are visible,
      and the specified directory (e.g., 'mens') is already expanded or selected.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains image properties:
        - "name" (str): The file name of the image.
        - "upload_date" (str): The upload date of the image.
        - "tags" (list of str): A list of associated tags for the image.
    """
    await page.goto("/admin/media_gallery/media/index/")
    image_elements = await page.query_selector_all(".image-item-selector")
    image_details = []
    for image in image_elements:
        name_element = await image.query_selector(".image-name")
        upload_date_element = await image.query_selector(".upload-date")
        tags_element = await image.query_selector(".tags")
        name = await name_element.text_content() if name_element else ""
        upload_date = (
            await upload_date_element.text_content() if upload_date_element else ""
        )
        tags = await tags_element.text_content() if tags_element else ""
        tags = tags.split(",") if tags else []
        image_details.append(
            {
                "name": name.strip(),
                "upload_date": upload_date.strip(),
                "tags": [tag.strip() for tag in tags],
            }
        )
    return image_details


async def search_images_by_keyword(page, keyword):
    """
    [Function description]
    Searches and lists images by entering a keyword into the search box and retrieves image results based on their names or metadata.

    [Usage preconditions]
    - This API searches images using a keyword for the current page you're on.
    - **You must already be on the media or gallery page where this functionality is available.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    keyword: The keyword string to input for searching images.

    Returns:
    list of str
        A list of strings representing the names or metadata of the found images.
    """
    await page.goto("/admin/media_gallery/media/index/")
    await page.goto("/admin/media_gallery/media/index/")
    search_box = await page.query_selector(
        'input[type="text"][placeholder="Search by keyword"]'
    )
    if search_box:
        await search_box.fill(keyword)
    else:
        raise Exception("Search box not found")
    search_button = await page.query_selector('button:text("Search")')
    if search_button:
        await search_button.click()
    else:
        raise Exception("Search button not found")
    image_elements = await page.query_selector_all(".image-item")
    image_data = []
    for image_element in image_elements:
        image_name = await image_element.text_content()
        if image_name:
            image_data.append(image_name.strip())
    return image_data


async def extract_last_order_details(page):
    """
    Extracts the most recent orders details from the current page,
    including customer names, item counts, and total amounts.

    [Usage preconditions]
    - This API retrieves the most recent order details.
    - **You must already be on the correct page that lists order information**.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "customer" (str): The name of the customer.
        - "items" (str): The number of items ordered.
        - "total" (str): The total order amount.
    """
    await page.goto("/admin/admin/dashboard/")
    order_details = []
    order_rows = await page.query_selector_all("table > tbody > tr:not(:first-child)")
    for row in order_rows:
        cells = await row.query_selector_all("td")
        if len(cells) == 3:
            customer_name = await (
                await cells[0].get_property("textContent")
            ).json_value()
            item_count = await (await cells[1].get_property("textContent")).json_value()
            total_amount = await (
                await cells[2].get_property("textContent")
            ).json_value()
            order_details.append(
                {
                    "customer": customer_name.strip(),
                    "items": item_count.strip(),
                    "total": total_amount.strip(),
                }
            )
    return order_details


async def get_bestsellers_data(page):
    """
    [Function description]
    Retrieves information about bestselling products, including their names, prices, and quantities sold, from the Magento Admin dashboard.

    [Usage preconditions]
    - This function assumes you are currently on the Magento Admin dashboard page where bestselling product data is presented.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries containing the bestselling product details:
        - 'product_name' (str): The name of the product.
        - 'price' (str): The price of the product.
        - 'quantity_sold' (str): The quantity of the product sold.
    """
    await page.goto("/admin/admin/dashboard/")
    best_sellers = []
    rows = await page.query_selector_all("#grid_tab_ordered_products_content table tr")
    for row in rows[1:]:
        product_name = await (await row.query_selector("td:nth-child(1)")).inner_text()
        price = await (await row.query_selector("td:nth-child(2)")).inner_text()
        quantity_sold = await (await row.query_selector("td:nth-child(3)")).inner_text()
        best_sellers.append(
            {
                "product_name": product_name,
                "price": price,
                "quantity_sold": quantity_sold,
            }
        )
    return best_sellers


async def get_recent_search_terms(page):
    """
    [Function description]
    Extracts details of the most recent search terms including their result counts and usage frequency.

    This function automates the extraction of recent search term details from the page.
    It collects information about each search term, result count, and usage frequency from the specific table.

    [Usage preconditions]
    - Ensure you are on the page containing the search term table before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "search_term" (str): The search term.
        - "results" (int): The number of results returned for the search term.
        - "uses" (int): The number of times the search term has been used.
    """
    await page.goto("/admin/admin/dashboard/")
    search_terms_data = []
    search_term_rows = await page.query_selector_all("table:nth-of-type(3) tr + tr")
    for row in search_term_rows:
        cells = await row.query_selector_all("td")
        search_term = await cells[0].text_content()
        results = int(await cells[1].text_content())
        uses = int(await cells[2].text_content())
        search_terms_data.append(
            {"search_term": search_term, "results": results, "uses": uses}
        )
    return search_terms_data




async def navigate_to_marketing_section(page):
    """
    Navigate to the Marketing section from the Magento Admin Dashboard.

    This function automates the navigation from the dashboard to the Marketing section by
    clicking on relevant menu links.

    [Usage preconditions]
    - Ensure you are authenticated and on the Magento Admin Dashboard page.

    Args:
    page : A Playwright `Page` instance that controls the browser automation.

    Usage log:
    - Successfully navigated to the Marketing section via the menu link.
    - No errors were encountered in navigation.

    Example:
    >>> await navigate_to_marketing_section(page)
    """
    await page.goto("/admin/admin/dashboard/")
    await page.get_by_role("menubar").get_by_role("link", name="Marketing").click()


async def extract_bestselling_product_details(page):
    """
    [Function description]
    Extracts detailed information on bestselling products from the dashboard page, including product names, prices, and quantities, for analyzing sales trends and performance.

    [Usage preconditions]
    - You must be on a page that contains a table of bestselling products.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "product_name" (str): The name of the product.
        - "price" (str): The price of the product as displayed.
        - "quantity" (str): The quantity sold of the product.
    """
    await page.goto("/admin/admin/dashboard/")
    bestselling_products = []
    table = await page.query_selector("#grid_tab_ordered_products_content table")
    rows = await table.query_selector_all("tbody tr")
    for row in rows:
        cells = await row.query_selector_all("td")
        product_name = await cells[0].text_content()
        price = await cells[1].text_content()
        quantity = await cells[2].text_content()
        bestselling_products.append(
            {
                "product_name": product_name.strip(),
                "price": price.strip(),
                "quantity": quantity.strip(),
            }
        )
    return bestselling_products


async def retrieve_latest_search_terms(page):
    """
    [Function description]
    Retrieves the most recent search terms from the Latest Search Terms section.

    This function automates the process of extracting details of the most recent
    search terms. It focuses on gathering search term details including:

    - Search term
    - Number of results returned for each term
    - Count of times each term has been used

    [Usage preconditions]
    - You must be on the correct page which displays the latest search terms in a table format.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "search_term" (str): The search term.
        - "results" (int): The number of results returned for that term.
        - "uses" (int): The number of times this search term has been used.
    """
    await page.goto("/admin/admin/dashboard/")
    table_rows_selector = "table:has-text('Search Term Results Uses') tbody tr"
    table_rows = await page.query_selector_all(table_rows_selector)
    latest_search_terms = []
    for row in table_rows:
        cells = await row.query_selector_all("td")
        search_term = (await cells[0].text_content()).strip()
        results = int((await cells[1].text_content()).strip())
        uses = int((await cells[2].text_content()).strip())
        latest_search_terms.append(
            {"search_term": search_term, "results": results, "uses": uses}
        )
    return latest_search_terms


async def extract_top_search_terms(page):
    """
    [Function description]
    Compiles a list of top search terms used by customers, detailing the frequency of use and the results found for each term.

    This function automates the extraction of search term data from a specific section of the dashboard page.
    It gathers information about each search term, including:

    - The search term itself.
    - Number of results found for the search term.
    - Frequency of usage by customers.

    [Usage preconditions]
    - You must already be on the correct dashboard page where search terms are displayed.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "search_term" (str): The specific search term used.
        - "results" (int): The number of results found for the search term.
        - "uses" (int): The number of times the search term was used.
    """
    await page.goto("/admin/admin/dashboard/")
    rows = await page.query_selector_all("table:nth-of-type(3) tr")
    search_data = []
    for row in rows[1:]:
        cells = await row.query_selector_all("td")
        search_term = await cells[0].inner_text()
        results = int(await cells[1].inner_text())
        uses = int(await cells[2].inner_text())
        search_data.append(
            {"search_term": search_term, "results": results, "uses": uses}
        )
    return search_data


async def extract_order_information(page):
    """
    [Function description]
    Extracts all order information from the current page, retrieving comprehensive details
    for each order listed, including:

    - Order ID
    - Purchase Point
    - Purchase Date
    - Bill-to Name
    - Ship-to Name
    - Grand Total (Base)
    - Grand Total (Purchased)
    - Status
    - Action URL

    [Usage preconditions]
    - The current page should be the Magento Admin orders page containing the orders table.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "order_id" (str): The order ID.
        - "purchase_point" (str): The purchase point information.
        - "purchase_date" (str): The order purchase date.
        - "bill_to_name" (str): The name details for bill-to.
        - "ship_to_name" (str): The name details for ship-to.
        - "grand_total_base" (str): The base grand total amount.
        - "grand_total_purchased" (str): The purchased grand total amount.
        - "status" (str): The current status of the order.
        - "action_url" (str): The URL for order-related actions.
    """
    await page.goto("/admin/sales/order/")
    order_details = []
    rows = await page.query_selector_all("tbody > tr")
    for row in rows:
        order_id = await (await row.query_selector("td:nth-child(2)")).inner_text()
        purchase_point = await (
            await row.query_selector("td:nth-child(3)")
        ).inner_text()
        purchase_date = await (await row.query_selector("td:nth-child(4)")).inner_text()
        bill_to_name = await (await row.query_selector("td:nth-child(5)")).inner_text()
        ship_to_name = await (await row.query_selector("td:nth-child(6)")).inner_text()
        grand_total_base = await (
            await row.query_selector("td:nth-child(7)")
        ).inner_text()
        grand_total_purchased = await (
            await row.query_selector("td:nth-child(8)")
        ).inner_text()
        status = await (await row.query_selector("td:nth-child(9)")).inner_text()
        action_node = await row.query_selector("td:nth-child(10) > a")
        action_url = await page.evaluate("el => el.href", action_node)
        order_data = {
            "order_id": order_id,
            "purchase_point": purchase_point,
            "purchase_date": purchase_date,
            "bill_to_name": bill_to_name,
            "ship_to_name": ship_to_name,
            "grand_total_base": grand_total_base,
            "grand_total_purchased": grand_total_purchased,
            "status": status,
            "action_url": action_url,
        }
        order_details.append(order_data)
    return order_details



async def calculate_total_sales_value(page):
    """
    [Function description]
    Calculate the total sales value of all 'Complete' orders to assess overall revenue.

    This function identifies orders marked as 'Complete' from the order table on the current page
    and aggregates their sales values to determine the total revenue of completed transactions.

    [Usage preconditions]
    - Ensure that you are already on the page containing a list of orders.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    float
        The total sales value of all orders with 'Complete' status.
    """
    await page.goto("/admin/sales/order/")
    total_sales_value = 0.0
    rows = await page.query_selector_all("table rowgroup row")
    for row in rows:
        status_cell = await row.query_selector("cell:nth-child(8)")
        status_text = await (await status_cell.text_content()).strip()
        if status_text == "Complete":
            total_cell = await row.query_selector("cell:nth-child(7)")
            total_text = await (await total_cell.text_content()).strip()
            total_value = float(total_text.replace("$", ""))
            total_sales_value += total_value
    return total_sales_value


async def manage_directories(page):
    """
    Manage directories by creating, renaming, or deleting them.

    This function provides capability to create a new directory, rename an existing
    directory, or delete a directory using the page's directory management UI tools.

    [Usage preconditions]
    - User should be on the directory management page where actions can be performed.
    - Ensure appropriate permissions to perform operations on directories.

    Args:
    page : A Playwright `Page` instance that controls browser automation.


    Returns:
    None
    """
    await page.goto("/admin/media_gallery/media/index/")
    create_button = await page.query_selector('button:text("Create Folder")')
    if create_button:
        await create_button.click()
    delete_button = await page.query_selector('button:text("Delete Folder")')
    if delete_button:
        await delete_button.click()
    mens_treeitem = await page.query_selector('treeitem:text("mens")')
    if mens_treeitem:
        await mens_treeitem.click()
    return None


async def upload_and_delete_images(page):
    """
    [Function description]
    Automates the process of uploading and deleting images within the Magento Admin interface.

    This function interacts with the Magento Admin interface to automate the actions of uploading and then deleting images.
    It uses button selectors to locate and perform these tasks.

    [Usage preconditions]
    - You must already be on the Magento Admin media management page.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    None
    """
    await page.goto("/admin/media_gallery/media/index/")
    upload_button = await page.query_selector('button:text("Upload Image")')
    if upload_button:
        await upload_button.click()
    delete_button = await page.query_selector('button:text("Delete Images...")')
    if delete_button:
        await delete_button.click()


async def navigate_to_invoices_section(page):
    """
    Navigates to the Invoices section from the Magento Admin Dashboard.

    This function automates the process of accessing the Invoices section by first
    clicking on the 'Sales' link in the menubar and then selecting 'Invoices' from the submenu.

    [Usage preconditions]
    - You must be authenticated and on the Magento Admin Dashboard page before invoking this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Usage log:
    - Successfully navigated to the Invoices section by clicking through the Sales menu.
    - No errors encountered during navigation.

    Example:
    >>> await navigate_to_invoices_section(page)
    """
    await page.goto("/admin/admin/dashboard/")
    sales_menu = page.get_by_role("menubar").get_by_role("link", name="Sales")
    await sales_menu.click()
    invoices_link = page.get_by_role("menu").get_by_role("link", name="Invoices")
    await invoices_link.click()


async def extract_invoice_details(page):
    """
    [Function description]
    Extracts all details of invoices present in a table on the current page, including invoice numbers, dates, order numbers, status, and totals.

    This function automates the extraction of invoice details from a table on a webpage.
    It gathers information about each invoice, such as:
    - Invoice number
    - Invoice date
    - Order number
    - Order date
    - Bill-to name
    - Status
    - Grand total (base)
    - Grand total (purchased)

    [Usage preconditions]
    - This API extracts invoice information from the page **you are currently at**.
    - **You must already be on a page containing an invoice table before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "invoice_number" (str): The invoice number.
        - "invoice_date" (str): The date of the invoice.
        - "order_number" (str): The order number.
        - "order_date" (str): The date of the order.
        - "bill_to_name" (str): The name of the billing recipient.
        - "status" (str): The status of the invoice.
        - "total_base" (str): The grand total in base currency.
        - "total_purchased" (str): The grand total in purchased currency.
    """
    await page.goto("/admin/sales/invoice/")
    invoices = []
    rows = await page.query_selector_all("table > tbody > tr")
    for row in rows:
        invoice_number = await (
            await row.query_selector("td:nth-child(2)")
        ).inner_text()
        invoice_date = await (await row.query_selector("td:nth-child(3)")).inner_text()
        order_number = await (await row.query_selector("td:nth-child(4)")).inner_text()
        order_date = await (await row.query_selector("td:nth-child(5)")).inner_text()
        bill_to_name = await (await row.query_selector("td:nth-child(6)")).inner_text()
        status = await (await row.query_selector("td:nth-child(7)")).inner_text()
        total_base = await (await row.query_selector("td:nth-child(8)")).inner_text()
        total_purchased = await (
            await row.query_selector("td:nth-child(9)")
        ).inner_text()
        invoices.append(
            {
                "invoice_number": invoice_number,
                "invoice_date": invoice_date,
                "order_number": order_number,
                "order_date": order_date,
                "bill_to_name": bill_to_name,
                "status": status,
                "total_base": total_base,
                "total_purchased": total_purchased,
            }
        )
    return invoices


async def retrieve_invoices_by_status(page, status):
    """
    [Function description]
    Retrieves invoice information from the Magento Admin page filtered by specific invoice status.

    This function automates the extraction of invoice details from the current page
    of Magento's admin interface, specifically filtering invoices by their status.
    It gathers information about each invoice including:

    - Invoice number
    - Invoice date
    - Order number
    - Order date
    - Bill-to name
    - Status
    - Grand total in base currency
    - Grand total in purchased currency

    [Usage preconditions]
    - This API filters invoices by status in the Magento Admin page **you are currently at**.
    - **You must already be on the Magento Admin invoices page before calling this function.**

    Args:
    page : Playwright 'Page' instance that controls browser automation.
    status : str, the status to filter invoices by.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "invoice_number" (str): The invoice number.
        - "invoice_date" (str): The date of the invoice.
        - "order_number" (str): The order number linked to the invoice.
        - "order_date" (str): The date of the linked order.
        - "bill_to_name" (str): The name of the billing client.
        - "status" (str): The invoice status.
        - "grand_total_base" (str): The grand total based on the base currency.
        - "grand_total_purchased" (str): The grand total based on the currency purchased.
    """
    await page.goto("/admin/sales/invoice/")
    invoices = []
    rows_selector = "table tr:nth-child(n+2)"
    rows = await page.query_selector_all(rows_selector)
    for row in rows:
        invoice_status = await (
            await row.query_selector("td:nth-child(7)")
        ).inner_text()
        if invoice_status.strip() == status:
            invoice_number = await (
                await row.query_selector("td:nth-child(2)")
            ).inner_text()
            invoice_date = await (
                await row.query_selector("td:nth-child(3)")
            ).inner_text()
            order_number = await (
                await row.query_selector("td:nth-child(4)")
            ).inner_text()
            order_date = await (
                await row.query_selector("td:nth-child(5)")
            ).inner_text()
            bill_to_name = await (
                await row.query_selector("td:nth-child(6)")
            ).inner_text()
            grand_total_base = await (
                await row.query_selector("td:nth-child(8)")
            ).inner_text()
            grand_total_purchased = await (
                await row.query_selector("td:nth-child(9)")
            ).inner_text()
            invoices.append(
                {
                    "invoice_number": invoice_number.strip(),
                    "invoice_date": invoice_date.strip(),
                    "order_number": order_number.strip(),
                    "order_date": order_date.strip(),
                    "bill_to_name": bill_to_name.strip(),
                    "status": invoice_status.strip(),
                    "grand_total_base": grand_total_base.strip(),
                    "grand_total_purchased": grand_total_purchased.strip(),
                }
            )
    return invoices


async def accumulate_total_invoiced_amount(page):
    """
    [Function description]
    Calculate the sum of all grand totals in the 'Purchased' column to understand overall revenue from invoices.

    This function automates the computation of total revenue from invoices listed on the current Magento Admin page,
    specifically deriving values from the 'Grand Total (Purchased)' column.

    [Usage preconditions]
    - This API should be called while you are on the Magento Admin invoices page where invoice data is listed.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    float
        The sum total of all grand total values in the 'Purchased' column from the invoices table.
    """
    await page.goto("/admin/sales/invoice/")
    total_sum = 0.0
    purchased_totals = await page.query_selector_all("tr td:nth-child(9)")
    for total in purchased_totals:
        text_content = await total.inner_text()
        value = float(text_content.replace("$", "").replace(",", ""))
        total_sum += value
    return total_sum


async def navigate_to_reports_section(page):
    """
    Navigates to the Reports section from the Magento Admin Dashboard.

    This function automates the process of accessing the Reports section by clicking on
    the 'Reports' link in the menubar.

    [Usage preconditions]
    - You must be authenticated and on the Magento Admin Dashboard page before invoking this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Usage log:
    - Successfully navigated to the Reports section by clicking the link in the menubar.
    """
    await page.goto("/admin/admin/dashboard/")
    await page.get_by_role("menubar").get_by_role("link", name="Reports").click()


async def extract_bestseller_details(page):
    """
    [Function description]
    Retrieves names, prices, and quantities of products listed under the 'Bestsellers' tab on the dashboard.

    This function automates the extraction of bestseller product details from the Magento dashboard,
    focusing on products under the 'Bestsellers' tab. It gathers information about each bestseller
    product, including:

    - Product name
    - Product price
    - Product quantity

    [Usage preconditions]
    - **You must already be on the Magento dashboard page with the 'Bestsellers' tab visible before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The product name.
        - "price" (str): The product price.
        - "quantity" (str): The product quantity sold.
    """
    await page.goto("/admin/admin/dashboard/")
    bestseller_details = []
    rows = await page.query_selector_all("#grid_tab_ordered_products_content table tr")
    for row in rows[1:]:
        name_element = await row.query_selector("td:nth-child(1)")
        name = await name_element.inner_text()
        price_element = await row.query_selector("td:nth-child(2)")
        price = await price_element.inner_text()
        quantity_element = await row.query_selector("td:nth-child(3)")
        quantity = await quantity_element.inner_text()
        bestseller_details.append({"name": name, "price": price, "quantity": quantity})
    return bestseller_details


async def summarize_last_search_terms_usage(page):
    """
    [Function description]
    Compiles a summary list of search terms recently searched by customers, including the number of uses and results produced.

    This function scans through tables on a Magento Admin dashboard page to extract and summarize details about
    search terms, their usage count, and the number of results each produced.

    [Usage preconditions]
    - You must already be on the Magento Admin dashboard page containing the recent search terms data before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "search_term" (str): The search query term.
        - "results" (int): The number of results the search produced.
        - "uses" (int): The number of times the search term was used.
    """
    await page.goto("/admin/admin/dashboard/")
    search_terms_summary = []
    tables = await page.query_selector_all("table")
    for table in tables:
        rows = await table.query_selector_all("tr")
        for row in rows:
            cells = await row.query_selector_all("td")
            if len(cells) == 3:
                search_term = await cells[0].inner_text()
                results = await cells[1].inner_text()
                uses = await cells[2].inner_text()
                try:
                    search_terms_summary.append(
                        {
                            "search_term": search_term.strip(),
                            "results": int(results.strip()),
                            "uses": int(uses.strip()),
                        }
                    )
                except ValueError:
                    continue
    return search_terms_summary


async def accumulate_latest_orders_total_value(page):
    """
    [Function description]
    Calculate the total order amount listed in the 'Latest Orders' section for financial overview.

    This function automates the extraction and summation of order totals from
    the latest orders section on the current page. It gathers and sums up the
    total value of the orders, thereby enabling a financial overview.

    [Usage preconditions]
    - This API accumulates total order amounts from the 'Latest Orders' table section on the page **you are currently at**.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    float
        The sum of the total order amounts listed in the 'Latest Orders' section.
    """
    await page.goto("/admin/admin/dashboard/")
    total_value = 0
    latest_orders_table = (await page.query_selector_all("table"))[1]
    rows = await latest_orders_table.query_selector_all("tbody > tr")
    for row in rows:
        total_cell = await row.query_selector("td:nth-child(3)")
        total_text = await total_cell.inner_text()
        total_amount = float(total_text.replace("$", "").strip())
        total_value += total_amount
    return total_value


async def filter_invoices_by_status(page, target_status):
    """
    [Function description]
    Filters and retrieves invoice information from a list of invoices based on a specific status such as 'Paid', 'Pending', etc.

    The function extracts detailed information for each invoice with the specified status in the current invoice listing page.

    [Usage preconditions]
    - The Playwright `Page` instance must be on the invoice listing page.

    Args:
    page : A Playwright `Page` instance controlling the browser automation.
    target_status (str): The status to filter invoices by (e.g., 'Paid', 'Pending').

    Returns:
    list of dict
        A list of dictionaries, each containing details of invoices matching the specified status.
        - "invoice_id" (str): The invoice identifier.
        - "invoice_date" (str): The date of the invoice.
        - "order_id" (str): The associated order identifier.
        - "order_date" (str): The date of the associated order.
        - "bill_to_name" (str): The name of the billing recipient.
        - "status" (str): The status of the invoice.
        - "total_base" (str): The grand total of the invoice (base currency).
        - "total_purchased" (str): The grand total of the invoice (purchased currency).
    """
    await page.goto("/admin/sales/invoice/")
    await page.goto("/admin/sales/invoice/")
    await page.click('button:has-text("\ue610Filters")')
    await page.fill('input[placeholder="Search by keyword"]', target_status)
    await page.press('input[placeholder="Search by keyword"]', "Enter")
    invoice_rows = await page.query_selector_all("table tbody tr")
    invoices = []
    for row in invoice_rows:
        cells = await row.query_selector_all("td")
        status = await cells[5].text_content()
        status = status.strip() if status else ""
        if status == target_status:
            invoice_details = {
                "invoice_id": (await cells[0].text_content()).strip(),
                "invoice_date": (await cells[1].text_content()).strip(),
                "order_id": (await cells[2].text_content()).strip(),
                "order_date": (await cells[3].text_content()).strip(),
                "bill_to_name": (await cells[4].text_content()).strip(),
                "status": status,
                "total_base": (await cells[6].text_content()).strip(),
                "total_purchased": (await cells[7].text_content()).strip(),
            }
            invoices.append(invoice_details)
    return invoices


async def navigate_to_sales_section(page):
    """
    Navigates to the Sales section from the Magento Admin Dashboard.

    This function automates the process of accessing the Sales section by clicking the 'Sales' link in the menubar.

    [Usage preconditions]
    - You must be authenticated and on the Magento Admin Dashboard page before invoking this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Usage log:
    - Successfully navigated to the Sales section from the dashboard by using the menu link.
    - No errors were encountered during navigation.

    Example:
    >>> await navigate_to_sales_section(page)
    """
    await page.goto("/admin/admin/dashboard/")
    sales_menu = page.get_by_role("menubar").get_by_role("link", name="\ue60b Sales")
    await sales_menu.click()


async def extract_bestsellers_info(page):
    """
    Extract bestsellers' information from the current page.

    This function automates the extraction of product details from the Bestsellers
    section of the dashboard. It gathers information about each product, including:

    - Product name
    - Price
    - Quantity sold

    [Usage preconditions]
    - This API retrieves bestseller information from the dashboard you are currently viewing.
    - **You must already be on the dashboard page in the admin section of the site** where
      the Bestsellers tab is present.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "product" (str): The product name.
        - "price" (str): The price of the product.
        - "quantity" (str): The quantity sold.
    """
    await page.goto("/admin/admin/dashboard/")
    bestsellers_info = []
    table_rows = await page.query_selector_all(
        'div[role="tabpanel"]:has-text("Bestsellers") table tbody tr'
    )
    for row in table_rows:
        cells = await row.query_selector_all("td")
        product_name = await cells[0].text_content()
        product_price = await cells[1].text_content()
        product_quantity = await cells[2].text_content()
        bestsellers_info.append(
            {
                "product": product_name.strip(),
                "price": product_price.strip(),
                "quantity": product_quantity.strip(),
            }
        )
    return bestsellers_info


async def compile_recent_search_terms(page):
    """
    [Function description]
    Compiles a list of recent search terms from a page along with their usage frequency and number of results.

    This function extracts the search terms, their usage counts, and the number of results found from a table displayed on the page.
    The function targets tables that are structured to display search term statistics.

    [Usage preconditions]
    - You should be on a page that contains a table of recent search terms with their result counts and usage frequency.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "search_term" (str): The search term.
        - "results" (int): The number of results found for the search term.
        - "uses" (int): The frequency of the search term's usage.
    """
    await page.goto("/admin/admin/dashboard/")
    search_terms_data = []
    rows = await page.query_selector_all(
        'table:has-text("Search Term Results Uses") tr'
    )
    for row in rows[1:]:
        columns = await row.query_selector_all("td")
        if columns:
            search_term = await columns[0].inner_text()
            results = int(await columns[1].inner_text())
            uses = int(await columns[2].inner_text())
            search_terms_data.append(
                {"search_term": search_term, "results": results, "uses": uses}
            )
    return search_terms_data


async def extract_bestsellers_products(page):
    """
    [Function description]
    Extracts all products, with their quantities and prices, from the Bestsellers tab in the Magento Admin Dashboard.

    [Usage preconditions]
    - This function assumes that you are already on the Magento Admin Dashboard page where the Bestsellers tab is loaded.

    Args:
    page : A Playwright `Page` instance that is currently pointing to the correct tab of the Magento Admin Dashboard.

    Returns:
    list of dict
        A list of dictionaries, each containing:
        - "product" (str): The name of the product.
        - "price" (str): The price of the product.
        - "quantity" (str): The available quantity of the product.
    """
    await page.goto("/admin/admin/dashboard/")
    product_rows = await page.query_selector_all(
        "#grid_tab_ordered_products_content table tr"
    )
    bestsellers = []
    for row in product_rows[1:]:
        cells = await row.query_selector_all("td")
        if cells:
            product_name = await cells[0].text_content()
            product_price = await cells[1].text_content()
            product_quantity = await cells[2].text_content()
            bestsellers.append(
                {
                    "product": product_name.strip(),
                    "price": product_price.strip(),
                    "quantity": product_quantity.strip(),
                }
            )
    return bestsellers


async def summarize_search_terms(page):
    """
    [Function Description]
    Extracts recent search terms along with their result counts and usage frequencies from
    the Magento admin dashboard. This information helps in monitoring customer interests
    and search behavior.

    [Usage Preconditions]
    - The page should be on the Magento admin dashboard where search term information is available.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries, each containing:
        - "term" (str): The search term.
        - "results" (int): The number of results returned for the search term.
        - "uses" (int): The frequency the term was used.
    """
    await page.goto("/admin/admin/dashboard/")
    search_terms_data = []
    tables = await page.query_selector_all("table:has-text('Search Term Results Uses')")
    for table in tables:
        rows = await table.query_selector_all("tr:nth-child(n+2)")
        for row in rows:
            cells = await row.query_selector_all("td")
            term = await cells[0].text_content()
            results = await cells[1].text_content()
            uses = await cells[2].text_content()
            search_terms_data.append(
                {
                    "term": term.strip(),
                    "results": int(results.strip()),
                    "uses": int(uses.strip()),
                }
            )
    return search_terms_data


async def extract_last_search_terms(page):
    """
    [Function description]
    Extracts details of the last search terms used from an admin panel dashboard.

    This function automates the extraction of the last search term details from the dashboard page.
    It gathers information about each search term in the last available table, including:

    - Search Term
    - Results
    - Uses

    [Usage preconditions]
    - This API extracts search term information from the **current** admin dashboard page you are on.
    - **You must already be on the relevant admin dashboard page before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "search_term" (str): The search term.
        - "results" (str): The number of results returned by the search.
        - "uses" (str): The number of times the search term was used.
    """
    await page.goto("/admin/admin/dashboard/")
    tables = await page.query_selector_all("table")
    last_table = tables[-1]
    search_term_data = []
    rows = await last_table.query_selector_all("tr")
    for row in rows[1:]:
        cells = await row.query_selector_all("td")
        if len(cells) == 3:
            search_term = await cells[0].text_content()
            results = await cells[1].text_content()
            uses = await cells[2].text_content()
            search_term_data.append(
                {
                    "search_term": search_term.strip(),
                    "results": results.strip(),
                    "uses": uses.strip(),
                }
            )
    return search_term_data


async def extract_bestseller_product_details(page):
    """
    [Function description]
    Extracts details of all bestseller products from the current admin dashboard page in the Magento Admin Panel.

    This function targets the bestseller products table and retrieves information including:
    - Product name
    - Product price
    - Quantity sold

    [Usage preconditions]
    - The admin must be logged into the Magento Admin Panel and be on the dashboard page where the bestseller's tab is selected.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the details of a bestseller product with the following keys:
        - "name" (str): The name of the product.
        - "price" (str): The product price.
        - "quantity" (str): The quantity sold.
    """
    await page.goto("/admin/admin/dashboard/")
    product_rows = await page.query_selector_all(
        "css=table >> text=Product >> .. >> .. >> tr:not(:first-child)"
    )
    bestsellers = []
    for row in product_rows:
        cells = await row.query_selector_all("td")
        name = await (await cells[0].text_content()).strip()
        price = await (await cells[1].text_content()).strip()
        quantity = await (await cells[2].text_content()).strip()
        bestsellers.append({"name": name, "price": price, "quantity": quantity})
    return bestsellers


async def extract_latest_customer_orders(page):
    """
    [Function description]
    Extracts details of the latest customer orders from the 'Latest Orders' table on the current dashboard.

    This function automates the extraction of order details displayed in the 'Latest Orders' section of the dashboard,
    gathering information about each order, including:

    - Customer name
    - Number of items purchased
    - Total amount spent

    [Usage preconditions]
    - This API should be called when you are already on the dashboard page containing the 'Latest Orders' section.
    - Ensure the session has access to necessary permissions to view order details.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "customer" (str): The name of the customer.
        - "items" (int): The number of items purchased.
        - "total" (str): The total amount spent in dollars.
    """
    await page.goto("/admin/admin/dashboard/")
    tables = await page.query_selector_all("table")
    target_table = None
    for table in tables:
        headers = await table.query_selector_all("tr th")
        header_texts = [
            (await (await header.get_property("innerText")).json_value())
            for header in headers
        ]
        if (
            "Customer" in header_texts
            and "Items" in header_texts
            and "Total" in header_texts
        ):
            target_table = table
            break
    if not target_table:
        return []
    rows = await target_table.query_selector_all("tbody tr")
    orders = []
    for row in rows:
        cells = await row.query_selector_all("td")
        customer_name = await (await cells[0].get_property("innerText")).json_value()
        items_purchased = int(
            await (await cells[1].get_property("innerText")).json_value()
        )
        total_spent = await (await cells[2].get_property("innerText")).json_value()
        orders.append(
            {"customer": customer_name, "items": items_purchased, "total": total_spent}
        )
    return orders


async def retrieve_search_terms(page):
    """
    [Function description]
    Retrieves search term data from the Last Search Terms and Top Search Terms tables on a webpage.
    This information includes search terms, result counts, and usage frequencies.

    [Usage preconditions]
    - **You must already be on the relevant webpage** that contains Search Terms tables before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "search_term" (str): The search term itself.
        - "results" (int): The count of results for the search term.
        - "uses" (int): The frequency of use for the search term.
    """
    await page.goto("/admin/admin/dashboard/")
    search_terms_data = []
    search_tables = await page.query_selector_all("table")
    for table in search_tables:
        headers = await table.query_selector_all("thead tr th")
        header_text = [(await header.inner_text()) for header in headers]
        if (
            "Search Term" in header_text
            and "Results" in header_text
            and "Uses" in header_text
        ):
            rows = await table.query_selector_all("tbody tr")
            for row in rows:
                cells = await row.query_selector_all("td")
                search_term = await cells[0].inner_text()
                results = int(await cells[1].inner_text())
                uses = int(await cells[2].inner_text())
                search_terms_data.append(
                    {"search_term": search_term, "results": results, "uses": uses}
                )
    return search_terms_data


async def navigate_to_customers_section(page):
    """
    Navigate to the 'Customers' section in the Magento Admin panel from the dashboard.

    This function automates the navigation to the 'Customers' section by interacting with
    the menu link available in the dashboard menubar.

    [Usage preconditions]
    - You should be logged into the Magento Admin panel on the dashboard before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Usage log:
    - Successfully navigated to the 'Customers' section upon utilizing the function.
    - The navigation employed the existing browser elements to determine the correct path
      and resulted in reaching the intended destination without errors.

    Example:
    >>> await navigate_to_customers_section(page)
    """
    await page.goto("/admin/admin/dashboard/")
    customers_menu = page.get_by_role("menubar").get_by_role("link", name="Customers")
    await customers_menu.click()


async def extract_customer_information(page):
    """
    Extracts complete customer details from a table on the current page.

    This function automates the extraction of customer information from a table.
    The collected details include:
    - Name
    - Email
    - Group
    - Phone
    - ZIP code
    - Country
    - State/Province
    - Customer Since date

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list where each entry corresponds to a customer and contains the following keys:
        - "name": Customer's name (str)
        - "email": Customer's email (str)
        - "group": Customer's group (str)
        - "phone": Customer's phone number (str)
        - "zip": Customer's ZIP code (str)
        - "country": Customer's country (str)
        - "state_province": Customer's state or province (str)
        - "customer_since": Date since customer is registered (str)
    """
    await page.goto("/admin/customer/index/")
    rows = await page.query_selector_all("table > tbody > tr")
    customers = []
    for row in rows:
        name = await (await row.query_selector("td:nth-child(2)")).inner_text()
        email = await (await row.query_selector("td:nth-child(3)")).inner_text()
        group = await (await row.query_selector("td:nth-child(4)")).inner_text()
        phone = await (await row.query_selector("td:nth-child(5)")).inner_text()
        zip_code = await (await row.query_selector("td:nth-child(6)")).inner_text()
        country = await (await row.query_selector("td:nth-child(7)")).inner_text()
        state_province = await (
            await row.query_selector("td:nth-child(8)")
        ).inner_text()
        customer_since = await (
            await row.query_selector("td:nth-child(9)")
        ).inner_text()
        customers.append(
            {
                "name": name.strip(),
                "email": email.strip(),
                "group": group.strip(),
                "phone": phone.strip(),
                "zip": zip_code.strip(),
                "country": country.strip(),
                "state_province": state_province.strip(),
                "customer_since": customer_since.strip(),
            }
        )
    return customers


async def navigate_to_shipments_section(page):
    """
    Navigate to the Shipments section from the Magento Admin Dashboard.

    This function automates the process of accessing the Shipments section by first
    clicking on the 'Sales' link in the menubar and then selecting 'Shipments' from the submenu.

    [Usage preconditions]
    - You must be authenticated and on the Magento Admin Dashboard page before invoking this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Usage log:
    - Successfully navigated to the Shipments section by clicking through the Sales menu.
    - No errors encountered during navigation.

    Example:
    >>> await navigate_to_shipments_section(page)
    """
    await page.goto("/admin/admin/dashboard/")
    sales_menu = page.get_by_role("menubar").get_by_role("link", name="Sales")
    await sales_menu.click()
    shipments_link = page.get_by_role("menuitem", name="Shipments")
    await shipments_link.click()


async def extract_all_shipments_details(page):
    """
    [Function description]
    Retrieves comprehensive shipment details from the current page of the shipping list.

    This function automates the extraction of shipment details from the shipment table
    on the current page. It gathers information about each shipment including:
    - Shipment number
    - Ship date
    - Order number
    - Order date
    - Ship-to name
    - Total quantity
    - View URL for further details

    [Usage preconditions]
    - This API function retrieves shipment details from the current shipments list page.
    - **You must already be on the page listing shipments before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "shipment_number" (str): The shipment number.
        - "ship_date" (str): The date and time the shipment was made.
        - "order_number" (str): The associated order number.
        - "order_date" (str): The date and time the order was placed.
        - "ship_to_name" (str): The name of the recipient.
        - "total_quantity" (str): The total quantity of items shipped.
        - "view_url" (str): The URL to view detailed shipment information.
    """
    await page.goto("/admin/sales/shipment/")
    rows_selector = "table > tbody > tr"
    rows = await page.query_selector_all(rows_selector)
    shipments = []
    for row in rows:
        cells = await row.query_selector_all("td")
        shipment_number = (await cells[1].text_content()).strip()
        ship_date = (await cells[2].text_content()).strip()
        order_number = (await cells[3].text_content()).strip()
        order_date = (await cells[4].text_content()).strip()
        ship_to_name = (await cells[5].text_content()).strip()
        total_quantity = (await cells[6].text_content()).strip()
        view_url = await cells[7].query_selector("a").get_attribute("href")
        shipment_details = {
            "shipment_number": shipment_number,
            "ship_date": ship_date,
            "order_number": order_number,
            "order_date": order_date,
            "ship_to_name": ship_to_name,
            "total_quantity": total_quantity,
            "view_url": view_url,
        }
        shipments.append(shipment_details)
    return shipments


async def extract_bestselling_products(page):
    """
    [Function description]
    Retrieves product information from the 'Bestsellers' tab on the current page.

    This function automates the extraction of bestseller product details from the current page.
    It gathers information about each product listed as a bestseller, including:

    - Product name
    - Product price
    - Product quantity

    [Usage preconditions]
    - This API retrieves product information from the 'Bestsellers' tab **you are currently at**.
    - **You must already be on a page with the 'Bestsellers' table visible before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "name" (str): The product name.
        - "price" (str): The product price.
        - "quantity" (str): The available quantity of the product.
    """
    await page.goto("/admin/admin/dashboard/")
    product_rows = await page.query_selector_all("table tr.rowgroup:nth-of-type(2) tr")
    bestsellers = []
    for row in product_rows:
        product_name = await (await row.query_selector("td:nth-child(1)")).inner_text()
        product_price = await (await row.query_selector("td:nth-child(2)")).inner_text()
        product_quantity = await (
            await row.query_selector("td:nth-child(3)")
        ).inner_text()
        bestsellers.append(
            {"name": product_name, "price": product_price, "quantity": product_quantity}
        )
    return bestsellers


async def gather_latest_customer_order_details(page):
    """
    Gather the latest customer order details from the dashboard 'Latest Orders' section.

    [Function description]
    This function automates the extraction of customer order details from a dashboard's
    'Latest Orders' section. It captures key information, including:
    - Customer Name
    - Number of Items
    - Total Expenses

    [Usage preconditions]
    - You must be on the dashboard page in a section where 'Latest Orders' is visible.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "customer" (str): The name of the customer.
        - "items" (str): The number of items.
        - "total" (str): The total expense in currency format.
    """
    await page.goto("/admin/admin/dashboard/")
    order_details = []
    rows = await page.query_selector_all(".orders-table tbody tr")
    for row in rows:
        cells = await row.query_selector_all("td")
        customer = await (await cells[0].text_content()).strip()
        items = await (await cells[1].text_content()).strip()
        total = await (await cells[2].text_content()).strip()
        order_details.append({"customer": customer, "items": items, "total": total})
    return order_details


async def extract_shipment_details(page):
    """
    [Function description]
    Retrieves comprehensive shipment details from the shipment listing page.

    This function automates the extraction of shipment details such as shipment number, ship date, order number,
    order date, and total quantity from the table on the shipment page.

    [Usage preconditions]
    - You must already be on the page that lists shipment details in a tabular format before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "shipment_number" (str): The shipment number.
        - "ship_date" (str): The date and time when the shipment was created.
        - "order_number" (str): The order number associated with the shipment.
        - "order_date" (str): The date and time when the order was placed.
        - "total_quantity" (str): The total quantity of items in the shipment.
    """
    await page.goto("/admin/sales/shipment/")
    shipment_details = []
    rows_selector = "table tr"
    rows = await page.query_selector_all(rows_selector)
    for row in rows[1:]:
        shipment_number = await (
            await row.query_selector("td:nth-child(2)")
        ).text_content()
        ship_date = await (await row.query_selector("td:nth-child(3)")).text_content()
        order_number = await (
            await row.query_selector("td:nth-child(4)")
        ).text_content()
        order_date = await (await row.query_selector("td:nth-child(5)")).text_content()
        total_quantity = await (
            await row.query_selector("td:nth-child(7)")
        ).text_content()
        shipment_details.append(
            {
                "shipment_number": shipment_number.strip(),
                "ship_date": ship_date.strip(),
                "order_number": order_number.strip(),
                "order_date": order_date.strip(),
                "total_quantity": total_quantity.strip(),
            }
        )
    return shipment_details


async def filter_shipments_by_customer(page, ship_to_name):
    """
    [Function description]
    Filters shipments to display only those related to a specific 'Ship-to Name'.

    This function automates the task of filtering and retrieving shipment details
    related to a specific customer from the shipment page. It is useful for managing
    orders for specific customers effectively and retrieving just the relevant data.

    [Usage preconditions]
    - The function assumes you are already on the correct shipments management page
      within the Magento Admin interface.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    ship_to_name : The name of the customer to filter shipments against.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains details of a shipment
        related to the specified 'Ship-to Name', including:
        - "shipment_number" (str): The shipment number.
        - "ship_date" (str): The date the shipment was made.
        - "order_number" (str): The order number related to the shipment.
        - "order_date" (str): The date the order was placed.
        - "total_quantity" (str): The total quantity of items shipped.
    """
    await page.goto("/admin/sales/shipment/")
    await page.goto("/admin/sales/shipment/")
    await page.click("button:has-text('Filters')")
    ship_to_name_input = await page.query_selector('input[placeholder="Ship-to Name"]')
    if ship_to_name_input:
        await ship_to_name_input.fill(ship_to_name)
    else:
        raise ValueError("Ship-to Name input field not found")
    await page.click("button:has-text('Apply Filters')")
    rows = await page.query_selector_all("table tr")
    shipments = []
    for row in rows:
        cells = await row.query_selector_all("td")
        if len(cells) >= 7:
            shipment_number = await cells[1].text_content()
            ship_date = await cells[2].text_content()
            order_number = await cells[3].text_content()
            order_date = await cells[4].text_content()
            customer_name = await cells[5].text_content()
            total_quantity = await cells[6].text_content()
            if customer_name.strip() == ship_to_name.strip():
                shipments.append(
                    {
                        "shipment_number": shipment_number.strip(),
                        "ship_date": ship_date.strip(),
                        "order_number": order_number.strip(),
                        "order_date": order_date.strip(),
                        "total_quantity": total_quantity.strip(),
                    }
                )
    return shipments


async def extract_customer_order_details(page):
    """
    Extracts customer order details from the current page in the Magento Admin Panel.

    This function automates the extraction of customer order details from a table on the Magento Admin
    dashboard page. It collects information about each customer's order, including:

    - Customer name
    - Number of items in the order
    - Total order amount

    [Usage preconditions]
    - You must already be on a page in the Magento Admin Panel that includes the customer order details table.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the customer's order details with keys:
        - "customer" (str): The name of the customer.
        - "items" (str): The number of items in the order.
        - "total" (str): The total amount of the order.
    """
    await page.goto("/admin/admin/dashboard/")
    customer_order_details = []
    rows = await page.query_selector_all("table:nth-of-type(2) tr:nth-child(n+2)")
    for row in rows:
        cells = await row.query_selector_all("td")
        customer_name = await (await cells[0].inner_text()).strip()
        items = await (await cells[1].inner_text()).strip()
        total = await (await cells[2].inner_text()).strip()
        customer_order_details.append(
            {"customer": customer_name, "items": items, "total": total}
        )
    return customer_order_details


async def retrieve_recent_search_terms(page):
    """
    Retrieve recent search terms from the Magento Admin dashboard page.

    This function extracts the recent search terms along with their associated results and uses from the current page
    of the Magento Admin dashboard.

    [Usage preconditions]
    - The function is intended for the Magento Admin dashboard page that already displays recent search terms.
    - The page should already be loaded, and the user must have necessary permissions to view it.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "search_term" (str): The search term used by customers.
        - "results" (str): Number of results returned for the search term.
        - "uses" (str): Number of times the search term was used.
    """
    await page.goto("/admin/admin/dashboard/")
    rows = await page.query_selector_all("table:nth-of-type(3) tbody tr")
    search_terms = []
    for row in rows:
        cells = await row.query_selector_all("td")
        if cells:
            search_term = await (await cells[0].get_property("innerText")).json_value()
            results = await (await cells[1].get_property("innerText")).json_value()
            uses = await (await cells[2].get_property("innerText")).json_value()
            search_terms.append(
                {
                    "search_term": search_term.strip(),
                    "results": results.strip(),
                    "uses": uses.strip(),
                }
            )
    return search_terms


async def extract_categories_information(page):
    """
    [Function description]
    Extracts all categories and subcategories listed in the Magento Admin interface,
    including their IDs and names.

    This function automates the extraction of category details from the Magento Admin
    page and gathers information about each category and subcategory, including:

    - Category name
    - Category ID

    [Usage preconditions]
    - This API retrieves category information for the Magento Admin interface **you are currently at**.
    - **You must already be on the Magento Admin categories page before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the category.
        - "id" (str): The unique ID of the category.
    """
    await page.goto("/admin/catalog/category/")
    categories_list = []
    await page.click('text="Expand All"')
    category_elements = await page.query_selector_all('a:has-text("(ID: ")')
    for element in category_elements:
        text_content = await element.text_content()
        name_id_split = text_content.strip().split(" (ID: ")
        if len(name_id_split) == 2:
            name = name_id_split[0]
            id_and_count = name_id_split[1].split(") ")[0]
            categories_list.append({"name": name, "id": id_and_count})
    return categories_list


async def filter_categories_by_visibility(page):
    """
    [Function description]
    Filters and retrieves categories based on their visibility in the store menu of Magento Admin.

    This function automates the process of identifying categories that are marked as visible in the store menu,
    allowing for quick and efficient data retrieval based on menu inclusion state.

    [Usage preconditions]
    - This API filters categories based on their visibility in the store menu from the **Magento Admin Categories page**.
    - **Ensure you are already on the relevant categories page in the admin panel before executing this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "id" (str): The unique identifier of the category.
        - "name" (str): The name of the category.
        - "menu_included" (bool): Visibility status of the category in the store menu.
    """
    await page.goto("/admin/catalog/category/")
    categories = []
    category_links = await page.query_selector_all('main a[href*="(ID: "]')
    for category_link in category_links:
        category_text = await category_link.inner_text()
        category_info = category_text.split(" (ID: ")[0]
        category_id = category_text.split(" (ID: ")[1].split(")")[0]
        await category_link.click()
        menu_checkbox = await page.query_selector(
            "input[name='include_in_menu'][checked]"
        )
        menu_included = bool(menu_checkbox)
        categories.append(
            {"id": category_id, "name": category_info, "menu_included": menu_included}
        )
        await page.go_back()
    return categories


async def retrieve_product_counts_in_categories(page):
    """
    [Function description]
    Gathers the number of products associated with each category ID listed in the 'Products in Category' section.

    This function automates the extraction of product counts by navigating through the 'Products in Category'
    section and parsing the category information that includes ID and count within the text of each category element.

    [Usage preconditions]
    - **You must already be on a page that lists category products.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "category_id" (str): The unique identifier of the category.
        - "product_count" (int): The number of products in the category.
    """
    await page.goto("/admin/catalog/category/")
    results = []
    category_elements = await page.query_selector_all('a[href*="(ID: "]')
    for element in category_elements:
        text_content = await element.inner_text()
        id_start = text_content.find("(ID: ") + len("(ID: ")
        id_end = text_content.find(")", id_start)
        product_count_start = text_content.find("(", id_end + 1) + 1
        product_count_end = text_content.find(")", product_count_start)
        category_id = text_content[id_start:id_end]
        product_count = int(text_content[product_count_start:product_count_end])
        results.append({"category_id": category_id, "product_count": product_count})
    return results


async def extract_product_details(page):
    """
    [Function description]
    Extracts detailed product information from the product listing table on the current page.

    This function automates the extraction of product details for each product listed in a table
    on the current page. It retrieves information including:
    - ID
    - Name
    - Type
    - SKU
    - Price
    - Quantity Available
    - Visibility
    - Status
    - Last Updated Date

    [Usage preconditions]
    - This API extracts detailed information for products listed in the table on the current page.
    - **You must already be on a product listing page that contains a table of product information.**

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the product details with keys:
        - "id" (str): Product ID.
        - "name" (str): Product name.
        - "type" (str): Product type.
        - "sku" (str): Product SKU.
        - "price" (str): Product price.
        - "quantity" (str): Product quantity available.
        - "visibility" (str): Product visibility status.
        - "status" (str): Product status.
        - "last_updated" (str): Product's last updated date.
    """
    await page.goto("/admin/catalog/product/")
    product_details = []
    product_rows = await page.query_selector_all("table tr")
    for row in product_rows[1:]:
        id_elem = await row.query_selector("td:nth-child(2)")
        name_elem = await row.query_selector("td:nth-child(4)")
        type_elem = await row.query_selector("td:nth-child(5)")
        sku_elem = await row.query_selector("td:nth-child(7)")
        price_elem = await row.query_selector("td:nth-child(8)")
        quantity_elem = await row.query_selector("td:nth-child(9)")
        visibility_elem = await row.query_selector("td:nth-child(11)")
        status_elem = await row.query_selector("td:nth-child(12)")
        last_updated_elem = await row.query_selector("td:nth-child(14)")
        product_details.append(
            {
                "id": await id_elem.text_content() if id_elem else "",
                "name": await name_elem.text_content() if name_elem else "",
                "type": await type_elem.text_content() if type_elem else "",
                "sku": await sku_elem.text_content() if sku_elem else "",
                "price": await price_elem.text_content() if price_elem else "",
                "quantity": await quantity_elem.text_content() if quantity_elem else "",
                "visibility": await visibility_elem.text_content()
                if visibility_elem
                else "",
                "status": await status_elem.text_content() if status_elem else "",
                "last_updated": await last_updated_elem.text_content()
                if last_updated_elem
                else "",
            }
        )
    return product_details


async def identify_zero_quantity_products(page):
    """
    [Function description]
    Identify and retrieve information on products with zero quantity from the current inventory table.

    This function automates the process of checking all products listed in the table,
    extracting details only for those with a quantity of zero.
    The details extracted include:
    - ID
    - Product Name
    - SKU
    - Price
    - Quantity

    [Usage preconditions]
    - **You must already be on the product inventory page before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "id" (str): The ID of the product.
        - "name" (str): The name of the product.
        - "sku" (str): The SKU of the product.
        - "price" (str): The price of the product.
        - "quantity" (str): The quantity of the product.
    """
    await page.goto("/admin/catalog/product/")
    zero_quantity_products = []
    product_rows = await page.query_selector_all("table rowgroup row:nth-of-type(n+2)")
    for row in product_rows:
        quantity_element = await row.query_selector("cell:nth-of-type(9)")
        quantity_text = await quantity_element.text_content()
        if quantity_text.strip() == "0.0000":
            id_element = await row.query_selector("cell:nth-of-type(2)")
            name_element = await row.query_selector("cell:nth-of-type(4)")
            sku_element = await row.query_selector("cell:nth-of-type(7)")
            price_element = await row.query_selector("cell:nth-of-type(8)")
            id_text = await id_element.text_content()
            name_text = await name_element.text_content()
            sku_text = await sku_element.text_content()
            price_text = await price_element.text_content()
            product_info = {
                "id": id_text.strip(),
                "name": name_text.strip(),
                "sku": sku_text.strip(),
                "price": price_text.strip(),
                "quantity": quantity_text.strip(),
            }
            zero_quantity_products.append(product_info)
    return zero_quantity_products


async def filter_products_by_sku_or_name(page, search_term):
    """
    [Function description]
    Filters products on the current page based on SKU or Name.

    This function automates the process of filtering products in a store's admin page
    by entering either a SKU or a product name into the search input and applying the filter.

    [Usage preconditions]
    - You must be on a store's product management page with visible filter options before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.
    search_term : A `str` representing the SKU or product name to filter by.

    Returns:
    None
    """
    await page.goto("/admin/catalog/product/")
    search_input = await page.query_selector('input[placeholder="Search by keyword"]')
    if search_input:
        await search_input.fill(search_term)
        search_button = await page.query_selector('button:has-text("Search")')
        if search_button:
            await search_button.click()
            await page.wait_for_timeout(1000)


async def extract_product_details_from_current_page(page):
    """
    [Function description]
    Extracts product information from the current page of a catalog table.

    This function automates the extraction of product details listed in the product table
    of the current page, capturing essential details for each visible product, including:

    - Product ID
    - Product Name
    - Product Type
    - Product SKU
    - Product Price
    - Product Quantity

    [Usage preconditions]
    - This API extracts product information for the catalog table visible on the page **you are currently at**.
    - **You must already be on a page displaying products in a table format before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "id" (str): The product ID.
        - "name" (str): The product name.
        - "type" (str): The product type.
        - "sku" (str): The product SKU.
        - "price" (str): The price of the product.
        - "quantity" (str): The quantity available.
    """
    await page.goto("/admin/catalog/product/")
    products = []
    rows = await page.query_selector_all("table tr")
    for row in rows:
        id = await (await row.query_selector("td:nth-child(2)")).inner_text()
        name = await (await row.query_selector("td:nth-child(3)")).inner_text()
        type = await (await row.query_selector("td:nth-child(5)")).inner_text()
        sku = await (await row.query_selector("td:nth-child(7)")).inner_text()
        price = await (await row.query_selector("td:nth-child(8)")).inner_text()
        quantity = await (await row.query_selector("td:nth-child(9)")).inner_text()
        product = {
            "id": id,
            "name": name,
            "type": type,
            "sku": sku,
            "price": price,
            "quantity": quantity,
        }
        products.append(product)
    return products


async def find_out_of_stock_products(page):
    """
    [Function description]
    Finds and lists all products with a quantity of zero on the current inventory page.

    This function scans the product table for items that show a quantity of zero, thus identifying them as out of stock.
    It compiles and returns their key details for further inspection or action.

    [Usage preconditions]
    - Ensure the page is already navigated to the correct inventory or product management section.

    Args:
    page :  A Playwright `Page` instance used to access and automate web content.

    Returns:
    list of dict
        A list wherein each dictionary contains the product details:
        - 'id' (str): The unique product identifier.
        - 'name' (str): The product's display name.
        - 'edit_url' (str): URL to edit or view more details about the product.
    """
    await page.goto("/admin/catalog/product/")
    out_of_stock_products = []
    rows = await page.query_selector_all("table > tbody > tr")
    for row in rows:
        quantity_cell = await row.query_selector("td:nth-child(9)")
        quantity_text = await (
            await quantity_cell.get_property("textContent")
        ).json_value()
        quantity = float(quantity_text.strip()) if quantity_text else None
        if quantity == 0:
            id_cell = await row.query_selector("td:nth-child(2)")
            name_cell = await row.query_selector("td:nth-child(4)")
            edit_link = await row.query_selector("td:nth-child(14) a")
            product_id = await (await id_cell.get_property("textContent")).json_value()
            product_name = await (
                await name_cell.get_property("textContent")
            ).json_value()
            edit_url = await (await edit_link.get_property("href")).json_value()
            out_of_stock_products.append(
                {
                    "id": product_id.strip(),
                    "name": product_name.strip(),
                    "edit_url": edit_url.strip(),
                }
            )
    return out_of_stock_products


async def retrieve_and_compare_products(page):
    """
    [Function description]
    Identifies and compares 'Simple Products' with 'Configurable Products' from the product listing page.

    This function retrieves product information about 'Simple Products' and 'Configurable Products'
    from the product catalog and compares them based on specific attributes:
    - Type
    - Price
    - Stock Visibility

    [Usage preconditions]
    - **You must already be on a product listing page** of an e-commerce platform like Magento Admin.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dicts
        A list of dictionaries where each dictionary contains:
        - "id" (str): The product's unique identifier.
        - "name" (str): The product's name.
        - "type" (str): The type of the product ('Simple Product' vs 'Configurable Product').
        - "price" (str): The price of the product.
        - "visibility" (str): Visibility status of the product.
    """
    await page.goto("/admin/catalog/product/")
    products_info = []
    rows = await page.query_selector_all("table tbody tr")
    for row in rows:
        product_type_el = await row.query_selector("td:nth-child(5)")
        product_type = await (
            await product_type_el.get_property("textContent")
        ).json_value()
        if "Simple Product" in product_type or "Configurable Product" in product_type:
            product_id_el = await row.query_selector("td:nth-child(2)")
            product_id = await (
                await product_id_el.get_property("textContent")
            ).json_value()
            product_name_el = await row.query_selector("td:nth-child(3)")
            product_name = await (
                await product_name_el.get_property("textContent")
            ).json_value()
            product_price_el = await row.query_selector("td:nth-child(8)")
            product_price = await (
                await product_price_el.get_property("textContent")
            ).json_value()
            product_visibility_el = await row.query_selector("td:nth-child(10)")
            product_visibility = await (
                await product_visibility_el.get_property("textContent")
            ).json_value()
            products_info.append(
                {
                    "id": product_id.strip(),
                    "name": product_name.strip(),
                    "type": product_type.strip(),
                    "price": product_price.strip(),
                    "visibility": product_visibility.strip(),
                }
            )
    return products_info


async def compare_product_differences(products_info):
    """
    [Function description]
    Compares products categorized as 'Simple Product' and 'Configurable Product'.

    Processes the list of products retrieved to find differences in attributes for further processing.

    [Usage preconditions]
    - Must receive a list of products with their details extracted from 'retrieve_and_compare_products' function.

    Args:
    products_info : list of dicts
        List containing attributes of both Simple and Configurable products for comparison.

    Returns:
    dict
        A dictionary parsing differences between 'Simple Products' and 'Configurable Products'.
    """
    simple_products = [
        prod for prod in products_info if prod["type"] == "Simple Product"
    ]
    configurable_products = [
        prod for prod in products_info if prod["type"] == "Configurable Product"
    ]
    differences = {
        "simple_products_count": len(simple_products),
        "configurable_products_count": len(configurable_products),
        "price_differences": [
            (s_prod["name"], c_prod["name"], s_prod["price"], c_prod["price"])
            for s_prod in simple_products
            for c_prod in configurable_products
            if s_prod["price"] != c_prod["price"]
        ],
        "visibility_differences": [
            (s_prod["name"], c_prod["name"], s_prod["visibility"], c_prod["visibility"])
            for s_prod in simple_products
            for c_prod in configurable_products
            if s_prod["visibility"] != c_prod["visibility"]
        ],
    }
    return differences


async def extract_all_shipments(page):
    """
    [Function description]
    Compiles a list of all current shipments available on the page, extracting details such as:
    - Shipment number
    - Ship date
    - Order number
    - Order date
    - Recipient name
    - Total quantity
    - Detailed view URL

    [Usage preconditions]
    - You must already be on the page containing the shipment table before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "shipment_number" (str): The shipment number.
        - "ship_date" (str): The ship date.
        - "order_number" (str): The order number.
        - "order_date" (str): The order date.
        - "recipient_name" (str): The name of the recipient.
        - "total_quantity" (str): The total quantity of items in the shipment.
        - "detailed_view_url" (str): The URL for the detailed view of the shipment.
    """
    await page.goto("/admin/sales/shipment/")
    shipment_data = []
    rows = await page.query_selector_all("table tr")
    for row in rows[1:]:
        cells = await row.query_selector_all("td")
        shipment_number = await (await cells[1].get_property("innerText")).json_value()
        ship_date = await (await cells[2].get_property("innerText")).json_value()
        order_number = await (await cells[3].get_property("innerText")).json_value()
        order_date = await (await cells[4].get_property("innerText")).json_value()
        recipient_name = await (await cells[5].get_property("innerText")).json_value()
        total_quantity = await (await cells[6].get_property("innerText")).json_value()
        detailed_view_link = await cells[7].query_selector("a")
        detailed_view_url = await (
            await detailed_view_link.get_property("href")
        ).json_value()
        shipment = {
            "shipment_number": shipment_number.strip(),
            "ship_date": ship_date.strip(),
            "order_number": order_number.strip(),
            "order_date": order_date.strip(),
            "recipient_name": recipient_name.strip(),
            "total_quantity": total_quantity.strip(),
            "detailed_view_url": detailed_view_url.strip(),
        }
        shipment_data.append(shipment)
    return shipment_data


async def identify_recent_shipments(page):
    """
    [Function description]
    Identifies and returns the most recent shipments based on the 'Ship Date' field.

    This function extracts shipment details and filters them to determine the most recent
    shipment activities on the page, useful for monitoring recent shipment activities.

    [Usage preconditions]
    - Ensure you are on a page with a shipment table containing shipment data.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "shipment_id" (str): The ID of the shipment.
        - "ship_date" (datetime): The shipment's date as a datetime object.
    """
    await page.goto("/admin/sales/shipment/")
    from datetime import datetime

    shipment_rows = await page.query_selector_all("table tr")
    recent_shipments = []
    for row in shipment_rows[1:]:
        cells = await row.query_selector_all("td")
        shipment_id = await (await cells[0].get_property("innerText")).json_value()
        ship_date_str = await (await cells[2].get_property("innerText")).json_value()
        ship_date = datetime.strptime(ship_date_str, "%b %d, %Y %I:%M:%S %p")
        recent_shipments.append(
            {"shipment_id": shipment_id.strip(), "ship_date": ship_date}
        )
    recent_shipments.sort(key=lambda x: x["ship_date"], reverse=True)
    return recent_shipments


async def retrieve_shipments_by_customer_name(page, customer_name):
    """
    [Function description]
    Retrieves shipment information for a specific customer based on the 'Ship-to Name'.

    This function filters the shipments from the Sales section of the Magento Admin Panel. It locates all shipments
    associated with the specified customer name, which is useful for customer-specific inquiries.

    [Usage preconditions]
    - You must be on the shipments page within the Sales section of the Magento Admin Panel.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    customer_name : The name of the customer whose shipments are to be retrieved.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following shipment details:
        - "shipment_number" (str): The shipment number.
        - "ship_date" (str): The date the shipment was made.
        - "order_number" (str): The associated order number.
        - "order_date" (str): The date the associated order was placed.
        - "ship_to_name" (str): The name of the customer to whom the shipment is addressed.
        - "total_quantity" (str): The total quantity of items in the shipment.
    """
    await page.goto("/admin/sales/shipment/")
    await page.goto("/admin/sales/shipment/")
    shipments = []
    rows = await page.query_selector_all("tbody tr")
    for row in rows:
        ship_to_name_element = await row.query_selector("td:nth-child(6)")
        if ship_to_name_element:
            ship_to_name = await ship_to_name_element.inner_text()
            if ship_to_name.strip() == customer_name.strip():
                shipment_number_element = await row.query_selector("td:nth-child(2)")
                ship_date_element = await row.query_selector("td:nth-child(3)")
                order_number_element = await row.query_selector("td:nth-child(4)")
                order_date_element = await row.query_selector("td:nth-child(5)")
                total_quantity_element = await row.query_selector("td:nth-child(7)")
                shipment_number = (
                    await shipment_number_element.inner_text()
                    if shipment_number_element
                    else ""
                )
                ship_date = (
                    await ship_date_element.inner_text() if ship_date_element else ""
                )
                order_number = (
                    await order_number_element.inner_text()
                    if order_number_element
                    else ""
                )
                order_date = (
                    await order_date_element.inner_text() if order_date_element else ""
                )
                total_quantity = (
                    await total_quantity_element.inner_text()
                    if total_quantity_element
                    else ""
                )
                shipments.append(
                    {
                        "shipment_number": shipment_number.strip(),
                        "ship_date": ship_date.strip(),
                        "order_number": order_number.strip(),
                        "order_date": order_date.strip(),
                        "ship_to_name": ship_to_name.strip(),
                        "total_quantity": total_quantity.strip(),
                    }
                )
    return shipments


async def extract_recent_search_terms(page):
    """
    [Function description]
    Extract data regarding the most recent search terms, results, and usage frequency from the customers.

    This function automates the extraction of search term details provided in a table format on the current page.
    It collects information concerning each search term including:

    - Search Term
    - Number of Results
    - Usage Frequency

    [Usage preconditions]
    - The function retrieves search term data from the HTML table located on the current page.
    - **You must already be on a page containing the required table before calling this function.**

    Args:
    page : Playwright `Page` instance that controls the browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "search_term" (str): The search term used.
        - "results" (int): The number of results for the search term.
        - "uses" (int): The frequency of usage of the search term.
    """
    await page.goto("/admin/admin/dashboard/")
    search_terms_data = []
    rows = await page.query_selector_all('table:has(th:text-is("Search Term")) tr')
    for row in rows[1:]:
        cells = await row.query_selector_all("td")
        search_term = await cells[0].inner_text()
        results = int(await cells[1].inner_text())
        uses = int(await cells[2].inner_text())
        search_terms_data.append(
            {"search_term": search_term, "results": results, "uses": uses}
        )
    return search_terms_data


async def extract_bestseller_products(page):
    """
    [Function description]
    Extracts bestseller product information from the Bestsellers tab on the Magento admin dashboard.

    This function automates the extraction of bestseller product details from the Bestsellers tab,
    capturing the product name, price, and the quantity sold for each bestseller product.

    [Usage preconditions]
    - The API function assumes that you are already on the Magento admin dashboard where the Bestsellers tab is visible.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "product_name" (str): The name of the bestseller product.
        - "price" (str): The price of the bestseller product.
        - "quantity_sold" (str): The quantity sold of the bestseller product.
    """
    await page.goto("/admin/admin/dashboard/")
    rows = await page.query_selector_all(
        'tabpanel[aria-label="Bestsellers"] table tbody tr'
    )
    bestseller_details = []
    for row in rows:
        cells = await row.query_selector_all("td")
        product_name = await (await cells[0].inner_text())
        price = await (await cells[1].inner_text())
        quantity_sold = await (await cells[2].inner_text())
        bestseller_details.append(
            {
                "product_name": product_name,
                "price": price,
                "quantity_sold": quantity_sold,
            }
        )
    return bestseller_details


async def retrieve_customer_order_details(page):
    """
    [Function description]
    Extracts information about recent customer orders from the Customer Orders section of the Magento Admin Dashboard.

    This function automates the extraction of customer order details, which include:
    - Customer names
    - Number of items purchased
    - Total spent amounts

    [Usage preconditions]
    - The function is designed to be used on the Magento Admin Dashboard page currently displaying the Customer Orders section.
    - **You must already be on the Magento Admin Dashboard page with the customer orders data visible.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "customer" (str): The name of the customer.
        - "items" (int): The number of items purchased.
        - "total" (float): The total amount spent by the customer.
    """
    await page.goto("/admin/admin/dashboard/")
    customer_order_details = []
    table_rows = await page.query_selector_all("table:nth-of-type(2) tr")
    for row in table_rows[1:]:
        cells = await row.query_selector_all("td")
        customer = await (await cells[0].get_property("innerText")).json_value()
        items = await (await cells[1].get_property("innerText")).json_value()
        total = await (await cells[2].get_property("innerText")).json_value()
        items = int(items)
        total = float(total.replace("$", ""))
        customer_order_details.append(
            {"customer": customer, "items": items, "total": total}
        )
    return customer_order_details


async def analyze_recent_search_terms(page):
    """
    [Function description]
    Analyzes recent search terms used by customers, gathering information on
    results count and usage frequency to track search behavior and identify
    popular items.

    [Usage preconditions]
    - You must be on a page containing a table with recent search term analytics
      before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "search_term" (str): The search term.
        - "results" (int): The number of results for the search term.
        - "uses" (int): How frequently the search term was used.
    """
    await page.goto("/admin/admin/dashboard/")
    search_data = []
    rows = await page.query_selector_all("table:nth-of-type(3) tr")
    for row in rows:
        cells = await row.query_selector_all("td")
        if len(cells) == 3:
            search_term = await (await cells[0].text_content()).strip()
            results = int(await (await cells[1].text_content()).strip())
            uses = int(await (await cells[2].text_content()).strip())
            search_data.append(
                {"search_term": search_term, "results": results, "uses": uses}
            )
    return search_data


async def navigate_to_store_switcher(page):
    """
    Navigates to the Store Switcher section from the Magento Admin Dashboard.

    This function automates the process of accessing the Store Switcher by first
    clicking on the 'Stores' menu and then selecting 'All Stores' from the submenu.

    [Usage preconditions]
    - You must be authenticated and on the Magento Admin Dashboard page before invoking this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Usage log:
    - Successfully navigated to the Store Switcher section by clicking through the Stores menu.
    """
    await page.goto("/admin/admin/dashboard/")
    stores_menu = page.get_by_role("menubar").get_by_role("link", name="Stores")
    await stores_menu.click()
    all_stores_link = page.get_by_role("menu").get_by_role("link", name="All Stores")
    await all_stores_link.click()


async def retrieve_stores_information(page):
    """
    [Function description]
    Retrieves detailed information of all stores from the current Magento Admin page.

    This function automates the extraction of store details from the Magento Admin interface,
    specifically within the "Stores" section, gathering information about each store's
    specific details including:

    - Web Site Name and Code
    - Store Name and Code
    - Store View Name and Code

    [Usage preconditions]
    - This API extracts store information from the Magento Admin "Stores" section.
    - **You must already be on the Magento Admin Stores page before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "web_site" (str): The name and code of the website.
        - "store" (str): The name and code of the store.
        - "store_view" (str): The name and code of the store view.
    """
    await page.goto("/admin/admin/system_store/")
    row_selector = "table tr"
    rows = await page.query_selector_all(row_selector)
    stores_info = []
    for row in rows[1:]:
        web_site_cell = await row.query_selector("td:nth-of-type(1)")
        web_site_text = await web_site_cell.inner_text()
        store_cell = await row.query_selector("td:nth-of-type(2)")
        store_text = await store_cell.inner_text()
        store_view_cell = await row.query_selector("td:nth-of-type(3)")
        store_view_text = await store_view_cell.inner_text()
        store_info = {
            "web_site": web_site_text,
            "store": store_text,
            "store_view": store_view_text,
        }
        stores_info.append(store_info)
    return stores_info


async def enumerate_store_actions(page):
    """
    Enumerates available actions on the Magento Stores settings page and their impacts.

    This function automates the extraction of available actions such as creating a new website, store,
    or store view on the Magento Stores settings page. It also explores the impacts of these actions
    and extracts current settings data from the page.

    [Usage preconditions]
    - You must already be on the Magento Admin Stores settings page before calling this function.

    Args:
    page : Playwright `Page` instance that controls browser automation.


    Returns:
    dict
        A dictionary containing:
        - "actions" (list): Actions available on the page (e.g., Create Website, Create Store, Create Store View),
        - "currentSettings" (list of dict): Current store settings with following details:
            - "website" (str): The website name and code.
            - "store" (str): The store name and code.
            - "store_view" (str): The store view name and code.
    """
    await page.goto("/admin/admin/system_store/")
    actions = []
    if await page.query_selector('button:has-text("Create Website")'):
        actions.append("Create Website")
    if await page.query_selector('button:has-text("Create Store")'):
        actions.append("Create Store")
    if await page.query_selector('button:has-text("Create Store View")'):
        actions.append("Create Store View")
    settings_locator = await page.query_selector("table")
    rows = await settings_locator.query_selector_all("tr")
    current_settings = []
    for row in rows[1:]:
        cells = await row.query_selector_all("td")
        website = (await cells[0].text_content()).strip()
        store = (await cells[1].text_content()).strip()
        store_view = (await cells[2].text_content()).strip()
        current_settings.append(
            {"website": website, "store": store, "store_view": store_view}
        )
    return {"actions": actions, "currentSettings": current_settings}


async def search_stores(page, search_term):
    """
    Demonstrates search and filter functionalities to find specific stores using the search bar.

    This function automates the process of searching for stores using a search bar and
    filtering the results based on the search criteria.

    [Usage preconditions]
    - You must be on a page that contains a search bar element for stores (e.g., Magento Admin Panel).

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    search_term : String representing the term you wish to search for in stores.

    Returns:
    list of str
        A list of store names that match the search criteria.
    """
    await page.goto("/admin/admin/system_store/")
    search_inputs = await page.query_selector_all(
        "main table rowgroup row:nth-child(2) cell textbox"
    )
    for search_input in search_inputs:
        if search_input:
            await search_input.fill(search_term)
    search_button = await page.query_selector('main button:has-text("Search")')
    await search_button.click()
    store_results = []
    rows = await page.query_selector_all("main table rowgroup:nth-of-type(2) row")
    for row in rows:
        cells = await row.query_selector_all("cell")
        if len(cells) > 1:
            store_link = await cells[1].query_selector("link")
            if store_link:
                store_name = await store_link.inner_text()
                store_results.append(store_name)
    per_page_dropdown = await page.query_selector("main combobox")
    if per_page_dropdown:
        await per_page_dropdown.select_option("50")
    return store_results


async def navigate_to_advance_product_analytics(page):
    """
    Navigates to the Advanced Reporting section from the Magento Admin Dashboard.

    This function automates the process of accessing the Advanced Reporting section by
    clicking on the 'Go to Advanced Reporting' link available on the Dashboard page.

    [Usage preconditions]
    - Ensure you are authenticated and on the Magento Admin Dashboard page before invoking this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Usage log:
    - Successfully navigated to the Advanced Reporting section by clicking the link.
    """
    await page.goto("/admin/admin/dashboard/")
    await page.get_by_role("link", name="Go to Advanced Reporting ").click()


async def get_bestsellers_product_details(page):
    """
    Retrieves a list of best-selling products along with their prices and quantities from the Bestsellers tab.

    This function automates the extraction of product details in the Bestsellers tab of the Magento admin panel.
    It gathers information about each product, including:
    - Product name
    - Price
    - Quantity

    [Usage preconditions]
    - This API retrieves details for products listed in the Bestsellers tab on the Magento dashboard.
    - **You must already be on the Magento admin panel's Dashboard page in the Bestsellers tab.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "product" (str): The name of the product.
        - "price" (str): The price of the product.
        - "quantity" (str): The quantity available of the product.
    """
    await page.goto("/admin/admin/dashboard/")
    product_details = []
    rows = await page.query_selector_all(
        "[role='tabpanel'][aria-labelledby='bestsellers-tab'] table tr"
    )
    for row in rows[1:]:
        cells = await row.query_selector_all("td")
        product_name = await (await cells[0].get_property("innerText")).json_value()
        product_price = await (await cells[1].get_property("innerText")).json_value()
        product_quantity = await (await cells[2].get_property("innerText")).json_value()
        product_details.append(
            {
                "product": product_name.strip(),
                "price": product_price.strip(),
                "quantity": product_quantity.strip(),
            }
        )
    return product_details


async def fetch_recent_orders(page):
    """
    [Function description]
    Extracts the most recent order information from the Magento admin dashboard.

    This function accesses the table where recent order details are displayed and
    retrieves essential information including customer names, item counts, and total order amounts.

    [Usage preconditions]
    - You must be logged into the Magento admin dashboard and on the relevant page before invoking this function.

    Args:
    page :  A Playwright `Page` instance for navigating and controlling the browser.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "customer_name" (str): The name of the customer.
        - "item_count" (int): The number of items in the order.
        - "total_amount" (str): The total amount for the order.
    """
    await page.goto("/admin/admin/dashboard/")
    recent_orders_table_handle = await page.query_selector("table:nth-of-type(2)")
    if not recent_orders_table_handle:
        return []
    rows = await recent_orders_table_handle.query_selector_all("tr:not(:first-child)")
    recent_orders = []
    for row in rows:
        cells = await row.query_selector_all("td")
        customer_name = await cells[0].inner_text()
        item_count = int(await cells[1].inner_text())
        total_amount = await cells[2].inner_text()
        recent_orders.append(
            {
                "customer_name": customer_name,
                "item_count": item_count,
                "total_amount": total_amount,
            }
        )
    return recent_orders


async def extract_latest_search_terms(page):
    """
    [Function description]
    Extracts the latest search terms with the count of search results and usages from the Magento admin dashboard.

    This function automates the extraction of the latest search terms data available in the Magento admin panel.
    It collects information on each search term including:
    - The search term itself
    - The number of results returned for that term
    - The frequency of use for that search term

    [Usage preconditions]
    - The function must be invoked when the browser page is already on the Magento admin dashboard that displays the 'Last Search Terms'.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "term" (str): The search term.
        - "results" (int): Number of results found for the search term.
        - "uses" (int): Usage frequency of the search term.
    """
    await page.goto("/admin/admin/dashboard/")
    search_terms_data = []
    search_terms_rows_locator = 'table >> text="Search Term Results Uses" >> .. >> tr'
    rows = await page.query_selector_all(search_terms_rows_locator)
    for row in rows[1:]:
        columns = await row.query_selector_all("td")
        term = await (await columns[0].text_content()).strip()
        results = int(await (await columns[1].text_content()).strip())
        uses = int(await (await columns[2].text_content()).strip())
        search_terms_data.append({"term": term, "results": results, "uses": uses})
    return search_terms_data


async def extract_store_data(page):
    """
    Extracts a list of websites, stores, and store views from the Magento Admin panel.

    This function automates the extraction of data from the Stores section of the Magento Admin.
    It collates comprehensive details for each website, store, and store view presently listed in the table.
    Details include both their names and codes.

    Usage preconditions:
    - Ensure you are on the Magento Stores settings page.

    Args:
    page : A Playwright `Page` instance controlling the browser automation.

    Returns:
    list of dict
        A list of dictionaries, each containing the following keys:
        - "website_name" (str): The name of the website.
        - "website_code" (str): The code of the website.
        - "store_name" (str): The name of the store.
        - "store_code" (str): The code of the store.
        - "store_view_name" (str): The name of the store view.
        - "store_view_code" (str): The code of the store view.
    """
    await page.goto("/admin/admin/system_store/")
    await page.goto("/admin/admin/system_store/")
    store_data = []
    rows = await page.query_selector_all("table tbody tr")
    for row in rows:
        website_element = await row.query_selector("td:nth-of-type(1)")
        website_name = website_code = ""
        if website_element:
            website_text = await website_element.text_content()
            if "(Code: " in website_text:
                website_name, website_code = website_text.rsplit(" (Code: ", 1)
                website_code = website_code.rstrip(")")
            else:
                website_name = website_text.strip()
        store_element = await row.query_selector("td:nth-of-type(2)")
        store_name = store_code = ""
        if store_element:
            store_text = await store_element.text_content()
            if "(Code: " in store_text:
                store_name, store_code = store_text.rsplit(" (Code: ", 1)
                store_code = store_code.rstrip(")")
            else:
                store_name = store_text.strip()
        store_view_element = await row.query_selector("td:nth-of-type(3)")
        store_view_name = store_view_code = ""
        if store_view_element:
            store_view_text = await store_view_element.text_content()
            if "(Code: " in store_view_text:
                store_view_name, store_view_code = store_view_text.rsplit(" (Code: ", 1)
                store_view_code = store_view_code.rstrip(")")
            else:
                store_view_name = store_view_text.strip()
        store_data.append(
            {
                "website_name": website_name.strip(),
                "website_code": website_code.strip(),
                "store_name": store_name.strip(),
                "store_code": store_code.strip(),
                "store_view_name": store_view_name.strip(),
                "store_view_code": store_view_code.strip(),
            }
        )
    return store_data


async def search_store_view(page, keyword):
    """
    [Function description]
    Searches for a specific store, website, or store view in the Magento Admin panel using a provided keyword.

    This function automates the search process by entering the keyword into a textbox associated with store views and clicking the search button.

    [Usage preconditions]
    - You must already be on the Magento Admin Store settings page to execute this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.
    keyword : str
        The keyword used for searching store, website, or store view.

    Returns:
    None
    """
    await page.goto("/admin/admin/system_store/")
    textbox_selector = 'table >> input[type="text"]'
    search_button_selector = 'button:has-text("Search")'
    textbox = await page.query_selector(textbox_selector)
    await textbox.fill(keyword)
    search_button = await page.query_selector(search_button_selector)
    await search_button.click()


async def create_website_or_store(page):
    """
    [Function description]
    Automates the execution of the 'Create Website', 'Create Store', and 'Create Store View' functionalities
    within the Magento Admin Panel.

    This function facilitates the process by initiating interactions with respective buttons that
    allow administrators to start creating a new website, store, or store view in the Magento
    e-commerce platform.

    [Usage preconditions]
    - You must be logged in and already on the 'Stores' settings page within the Magento Admin Panel.
    - Ensure the admin panel is not in a restricted view that might hide these options.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    None
    """
    await page.goto("/admin/admin/system_store/")
    try:
        await page.locator('button:has-text("Create Website")').click()
    except Exception as e:
        print(f"Failed to click 'Create Website' button: {str(e)}")
    try:
        await page.locator('button:has-text("Create Store")').click()
    except Exception as e:
        print(f"Failed to click 'Create Store' button: {str(e)}")
    try:
        await page.locator('button:has-text("Create Store View")').click()
    except Exception as e:
        print(f"Failed to click 'Create Store View' button: {str(e)}")


async def compile_out_of_stock_products(page):
    """
    [Function description]
    Compiles a list of products with zero quantity available for inventory replenishment planning.

    This function automates the extraction of product details that have a quantity of zero indicated
    in the inventory listing on the current page. It scans through each product row in the table
    and gathers relevant attributes including name, SKU, price, among others.

    [Usage preconditions]
    - You must be on the Magento Admin catalog page where products are listed.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys for products
        with zero quantity:
        - "name" (str): The name of the product.
        - "sku" (str): The SKU identifier of the product.
        - "price" (str): The listed price of the product.
        - "url" (str): The URL to edit the product details.
    """
    await page.goto("/admin/catalog/product/")
    out_of_stock_products = []
    rows = await page.query_selector_all("table tr")
    for row in rows:
        cell_selectors = {
            "name": "td:nth-child(4)",
            "sku": "td:nth-child(7)",
            "price": "td:nth-child(8)",
            "quantity": "td:nth-child(9)",
            "edit_link": "td:last-child a",
        }
        quantity_cell = await row.query_selector(cell_selectors["quantity"])
        if quantity_cell:
            quantity = await quantity_cell.inner_text()
            if re.fullmatch("\\s*0(\\.0+)?\\s*", quantity):
                name_cell = await row.query_selector(cell_selectors["name"])
                sku_cell = await row.query_selector(cell_selectors["sku"])
                price_cell = await row.query_selector(cell_selectors["price"])
                edit_link = await row.query_selector(cell_selectors["edit_link"])
                name = await name_cell.inner_text() if name_cell else ""
                sku = await sku_cell.inner_text() if sku_cell else ""
                price = await price_cell.inner_text() if price_cell else ""
                url = await edit_link.get_attribute("href") if edit_link else ""
                out_of_stock_products.append(
                    {
                        "name": name.strip(),
                        "sku": sku.strip(),
                        "price": price.strip(),
                        "url": url.strip(),
                    }
                )
    return out_of_stock_products


async def search_and_filter_products_by_keyword(page, keyword):
    """
    [Function description]
    Automates the product search functionality by locating products using a specific keyword or SKU.

    This function inputs the given keyword or SKU into the search box on the product catalog page
    and retrieves the list of products that match the search criteria, capturing essential product
    information such as product ID, name, SKU, price, and more.

    [Usage preconditions]
    - You must already be on the product catalog page containing a search functionality.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    keyword : A string keyword or SKU to search products by.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains product information such as:
        - "id": Product ID.
        - "name": Product name.
        - "sku": Product SKU.
        - "price": Product price.
        - "quantity": Available quantity.
    """
    await page.goto("/admin/catalog/product/")
    search_box = await page.query_selector('input[placeholder="Search by keyword"]')
    if search_box:
        await search_box.fill(keyword)
        search_button = await page.query_selector('button:has-text("Search")')
        if search_button:
            await search_button.click()
            rows = await page.query_selector_all("table tbody tr")
            products = []
            for row in rows:
                cells = await row.query_selector_all("td")
                if cells:
                    product = {
                        "id": (await cells[0].text_content()).strip(),
                        "name": (await cells[2].text_content()).strip(),
                        "sku": (await cells[5].text_content()).strip(),
                        "price": (await cells[6].text_content()).strip(),
                        "quantity": (await cells[7].text_content()).strip(),
                    }
                    products.append(product)
            return products
    return []


async def retrieve_image_details(page):
    """
    [Function description]
    Retrieve details of images from the current directory in the Magento Admin Panel.

    This function automates the extraction of image information, usually from a media gallery or similar section.
    It gathers details about each image available in the current context, including:
    - Image name
    - Image URL
    - Dimensions (if available)

    [Usage preconditions]
    - You must already be on the Magento Admin Panel page where images are listed before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the image.
        - "url" (str): The URL to the image.
        - "dimensions" (dict, optional): The dimensions of the image with keys "width" and "height".
    """
    await page.goto("/admin/media_gallery/media/index/")
    image_details = []
    image_elements = await page.query_selector_all(".image-container")
    for image_element in image_elements:
        name_element = await image_element.query_selector(".image-name")
        url_element = await image_element.query_selector("img")
        name = await name_element.inner_text() if name_element else "Unknown"
        url = await url_element.get_attribute("src") if url_element else "Unknown"
        width = (
            await url_element.evaluate("(el) => el.naturalWidth")
            if url_element
            else None
        )
        height = (
            await url_element.evaluate("(el) => el.naturalHeight")
            if url_element
            else None
        )
        dimensions = {"width": width, "height": height} if width and height else {}
        image_details.append({"name": name, "url": url, "dimensions": dimensions})
    return image_details


async def search_images_by_keywords(page, keyword):
    """
    [Function description]
    Searches for images within the Magento Admin Panel using the provided keyword.

    This function inputs a keyword into the search box and triggers the search function
    to find images related to that keyword.

    [Usage preconditions]
    - You must be logged in and on the correct page in the Magento Admin Panel where
      image search functionality is available.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    keyword : str
        The keyword to search images by.

    Returns:
    None
        This function performs an action and does not return a value.
    """
    await page.goto("/admin/media_gallery/media/index/")
    search_box = await page.query_selector("input[type='text']")
    if search_box:
        await search_box.fill(keyword)
    else:
        raise Exception("Search box not found")
    search_button = await page.query_selector("button:has-text('Search')")
    if search_button:
        await search_button.click()
    else:
        raise Exception("Search button not found")


async def navigate_to_sales_transactions(page):
    """
    Navigates to the Sales Transactions section from the Magento Admin Dashboard.

    This function automates the process of accessing the Sales Transactions by selecting
    the 'Sales' link in the menubar and clicking 'Transactions' in the resulting submenu.

    [Usage preconditions]
    - You must be authenticated and on the Magento Admin Dashboard page before invoking this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Usage log:
    - Successfully invoked and navigated to Sales Transactions after clicking through the Sales menu.
    """
    await page.goto("/admin/admin/dashboard/")
    sales_menu = page.get_by_role("menubar").get_by_role("link", name="Sales")
    await sales_menu.click()
    transactions_link = page.get_by_role("menu").get_by_role(
        "link", name="Transactions"
    )
    await transactions_link.click()


async def filter_transactions_by_date_range(page, start_date, end_date):
    """
    Filters transactions based on a specified date range in the system's transaction table.

    This function automates the process of filtering transactions by setting a date range
    in the Magento Admin transactions page, allowing users to easily view transactions
    within a specific timeframe.

    [Usage preconditions]
    - The page should already be on the Magento Admin transaction filtering page.*

    Args:
    page : A Playwright `Page` instance used for browser automation.
    start_date : A string representing the start date in a recognized date format ('yyyy-mm-dd').
    end_date : A string representing the end date in a recognized date format ('yyyy-mm-dd').

    Returns:
    None
        The function filters the transaction table to display results within the specified date range.
    """
    await page.goto("/admin/sales/transactions/")
    from_date_input = await page.query_selector('input[placeholder="From"]')
    await from_date_input.fill(start_date)
    to_date_input = await page.query_selector('input[placeholder="To"]')
    await to_date_input.fill(end_date)
    search_button = await page.query_selector('button:has-text("Search")')
    await search_button.click()


async def search_transactions_by_order_id(page, order_id):
    """
    [Function description]
    Search and retrieve transaction records using a specific Order ID.

    This method automates the process of entering an Order ID into the search field,
    executing the search, and extracting the transaction data related to the provided Order ID.
    The extracted transaction records contain information such as Transaction ID, Payment Method,
    and other key transaction details.

    [Usage preconditions]
    - You must be on the transactions page within the Magento admin panel before invoking this function.

    Args:
    page: A Playwright `Page` instance that facilitates browser interactions.
    order_id: A string representing the specific Order ID for which transaction records are retrieved.

    Returns:
    list of dict
        A list where each entry is a dictionary containing transaction details, with keys like
        "order_id", "transaction_id", "payment_method", etc.
    """
    await page.goto("/admin/sales/transactions/")
    order_id_textbox = await page.query_selector('table input[type="text"]')
    await order_id_textbox.fill(order_id)
    search_button = await page.query_selector('button:has-text("Search")')
    await search_button.click()
    await page.wait_for_load_state("networkidle")
    transactions = []
    transaction_rows = await page.query_selector_all("table tbody tr")
    for row in transaction_rows:
        cells = await row.query_selector_all("td")
        if len(cells) < 7:
            continue
        transaction = {
            "order_id": (await cells[0].text_content()).strip(),
            "transaction_id": (await cells[1].text_content()).strip(),
            "parent_transaction_id": (await cells[2].text_content()).strip(),
            "payment_method": (await cells[3].text_content()).strip(),
            "transaction_type": (await cells[4].text_content()).strip(),
            "closed": (await cells[5].text_content()).strip(),
            "created": (await cells[6].text_content()).strip(),
        }
        transactions.append(transaction)
    return transactions


async def navigate_to_newsletter_subscribers(page):
    """
    Navigate to the 'Newsletter Subscribers' section from the Magento Admin Dashboard.

    This function automates the process of accessing the Newsletter Subscribers section by first
    clicking on the 'Marketing' link in the menu bar and then selecting 'Newsletter Subscribers'.

    [Usage preconditions]
    - You must be authenticated and on the Magento Admin Dashboard page before invoking this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Usage log:
    - Successfully navigated to the 'Newsletter Subscribers' section by clicking through the Marketing menu.

    Example:
    >>> await navigate_to_newsletter_subscribers(page)
    """
    await page.goto("/admin/admin/dashboard/")
    marketing_menu = page.get_by_role("menubar").get_by_role("link", name="Marketing")
    await marketing_menu.click()
    newsletter_link = page.get_by_role("link", name="Newsletter Subscribers")
    await newsletter_link.click()


async def extract_subscriber_details(page):
    """
    [Function description]
    Extracts complete subscriber information from the newsletter subscribers table in Magento Admin Panel.

    This function automates the extraction of subscriber details from the table
    present in the newsletter subscribers section, gathering information including:
    - Email
    - Type
    - First Name
    - Last Name
    - Status
    - Web Site
    - Store
    - Store View

    [Usage preconditions]
    - Ensure that the browser is already directed to the Magento Admin newsletter subscribers page where the subscriber table is visible.

    Args:
    page :  A Playwright `Page` instance pointed to the newsletter subscribers section.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains subscriber information with keys:
        - "email" (str): The subscriber's email.
        - "type" (str): The type of subscriber (Guest/Customer).
        - "first_name" (str): The first name of the subscriber.
        - "last_name" (str): The last name of the subscriber.
        - "status" (str): Subscription status.
        - "website" (str): The website associated.
        - "store" (str): Store information.
        - "store_view" (str): Store view.
    """
    await page.goto("/admin/newsletter/subscriber/")
    subscriber_details = []
    rows = await page.query_selector_all("table > tbody > tr:not(:first-child)")
    for row in rows:
        email = await (await row.query_selector("td:nth-child(2)")).inner_text()
        type_value = await (await row.query_selector("td:nth-child(3)")).inner_text()
        first_name = await (await row.query_selector("td:nth-child(4)")).inner_text()
        last_name = await (await row.query_selector("td:nth-child(5)")).inner_text()
        status = await (await row.query_selector("td:nth-child(6)")).inner_text()
        website = await (await row.query_selector("td:nth-child(7)")).inner_text()
        store = await (await row.query_selector("td:nth-child(8)")).inner_text()
        store_view = await (await row.query_selector("td:nth-child(9)")).inner_text()
        subscriber_details.append(
            {
                "email": email,
                "type": type_value,
                "first_name": first_name,
                "last_name": last_name,
                "status": status,
                "website": website,
                "store": store,
                "store_view": store_view,
            }
        )
    return subscriber_details


async def filter_subscribers(
    page, email=None, first_name=None, last_name=None, status=None
):
    """
    [Function description]
    Filters subscribers based on specified criteria such as Email, First Name, Last Name, and Status.

    This function inputs the provided filter criteria into their respective fields within the newsletter subscriber management page
    and executes a search to return subscribers that match.

    [Usage preconditions]
    - This API must be called on the newsletter subscriber page in the Magento Admin Panel.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    email : (Optional) Email address to filter subscribers.
    first_name : (Optional) First Name of the subscribers to filter.
    last_name : (Optional) Last Name of the subscribers to filter.
    status : (Optional) Subscriber status (e.g., Subscribed, Unsubscribed) to filter.

    Returns:
    None
    """
    if email:
        email_input = await page.query_selector(
            "tr:nth-child(2) > td:nth-child(2) input[type='text']"
        )
        if email_input:
            await email_input.fill(email)
    if first_name:
        first_name_input = await page.query_selector(
            "tr:nth-child(2) > td:nth-child(4) input[type='text']"
        )
        if first_name_input:
            await first_name_input.fill(first_name)
    if last_name:
        last_name_input = await page.query_selector(
            "tr:nth-child(2) > td:nth-child(5) input[type='text']"
        )
        if last_name_input:
            await last_name_input.fill(last_name)
    if status:
        status_combobox = await page.query_selector(
            "tr:nth-child(2) > td:nth-child(6) select"
        )
        if status_combobox:
            await status_combobox.select_option(value=status)
    search_button = await page.query_selector('button:has-text("Search")')
    if search_button:
        await search_button.click()


async def analyze_subscriber_types(page):
    """
    [Function description]
    Extracts and summarizes data to understand the distribution of subscriber types (Guest vs Customer).

    This function automates the process of analyzing subscriber types in a web page.
    It navigates through subscriber information listed in a table and retrieves
    data to provide a summary count of each subscriber type.

    [Usage preconditions]
    - You must be on a page that contains a table with subscriber type details.
    - The table must have columns including "Type" indicating subscriber type.

    Args:
    page : A Playwright `Page` instance for control over browser automation.

    Returns:
    dict : A dictionary containing counts of "Guest" and "Customer" subscriber types.
        - "Guest_count" (int): The number of Guest subscribers.
        - "Customer_count" (int): The number of Customer subscribers.
    """
    await page.goto("/admin/newsletter/subscriber/")
    guest_count = 0
    customer_count = 0
    rows = await page.query_selector_all("table tr")
    for row in rows[1:]:
        type_cell = await row.query_selector("td:nth-child(4)")
        type_text = await type_cell.inner_text()
        if type_text == "Guest":
            guest_count += 1
        elif type_text == "Customer":
            customer_count += 1
    return {"Guest_count": guest_count, "Customer_count": customer_count}


async def extract_all_transaction_details(page):
    """
    [Function description]
    Extracts transaction details from all rows in the transactions table present on the Magento Admin page.

    This function automates the extraction of various transaction details like Order ID, Transaction ID,
    Parent Transaction ID, Payment Method, Transaction Type, Closed status, and Created date from the
    transactions table.

    [Usage preconditions]
    - You must already be on the Magento Admin transactions page where the transaction table is visible.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary represents a transaction and contains the following keys:
        - "order_id" (str): Order ID of the transaction.
        - "transaction_id" (str): The Transaction ID.
        - "parent_transaction_id" (str): The Parent Transaction ID.
        - "payment_method" (str): The Payment Method used.
        - "transaction_type" (str): The type of transaction (e.g., Order, Capture).
        - "closed" (str): Status indicating if the transaction is closed.
        - "created_date" (str): Date when the transaction was created.
    """
    await page.goto("/admin/sales/transactions/")
    transactions_list = []
    transaction_rows = await page.query_selector_all("table tr[data-row-id]")
    for row in transaction_rows:
        order_id = await (await row.query_selector("td:nth-child(2)")).text_content()
        transaction_id = await (
            await row.query_selector("td:nth-child(3)")
        ).text_content()
        parent_transaction_id = await (
            await row.query_selector("td:nth-child(4)")
        ).text_content()
        payment_method = await (
            await row.query_selector("td:nth-child(5)")
        ).text_content()
        transaction_type = await (
            await row.query_selector("td:nth-child(6)")
        ).text_content()
        closed = await (await row.query_selector("td:nth-child(7)")).text_content()
        created_date = await (
            await row.query_selector("td:nth-child(8)")
        ).text_content()
        transactions_list.append(
            {
                "order_id": order_id,
                "transaction_id": transaction_id,
                "parent_transaction_id": parent_transaction_id,
                "payment_method": payment_method,
                "transaction_type": transaction_type,
                "closed": closed,
                "created_date": created_date,
            }
        )
    return transactions_list


async def navigate_to_credit_memos_section(page):
    """
    Navigate to the 'Credit Memos' section in the Magento Admin panel from the dashboard.

    This function automates the navigation from the Magento Admin Dashboard to the 'Credit Memos'
    section within the 'Sales' submenu.

    Usage preconditions:
    - You should be logged into the Magento Admin panel and positioned at the dashboard before
      calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Usage log:
    - Successfully navigated to the 'Credit Memos' section by utilizing this function.
    - The navigation employed the existing browser elements to determine the correct path
      and resulted in reaching the intended destination without errors.

    Example:
    >>> await navigate_to_credit_memos_section(page)
    """
    await page.goto("/admin/admin/dashboard/")
    await page.get_by_role("menubar").get_by_role("link", name="Sales").click()
    await page.get_by_role("menu").get_by_role("link", name="Credit Memos").click()


async def extract_credit_memo_data(page):
    """
    [Function description]
    Extracts credit memo data from the current page.

    This function retrieves all credit memo details including:
    - Credit Memo ID
    - Creation Date
    - Linked Order ID
    - Order Date
    - Billing Name
    - Memo Status
    - Refunded Amount
    - Action link for detailed viewing

    [Usage preconditions]
    - This API retrieves credit memo information for an admin currently on the credit memos page of the Magento Admin panel.
    - **You must already be on the Magento Admin credit memos page before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "credit_memo_id" (str): The credit memo ID.
        - "creation_date" (str): The creation date of the memo.
        - "order_id" (str): The linked order ID.
        - "order_date" (str): The order date.
        - "billing_name" (str): The billing name associated with the memo.
        - "status" (str): The status of the memo.
        - "refunded_amount" (str): The refunded amount.
        - "action_link" (str): The URL for detailed viewing.
    """
    await page.goto("/admin/sales/creditmemo/")
    credit_memo_data = []
    rows = await page.query_selector_all("table tbody tr")
    for row in rows:
        memo_id = await (await row.query_selector("td:nth-of-type(2)")).text_content()
        creation_date = await (
            await row.query_selector("td:nth-of-type(3)")
        ).text_content()
        order_id = await (await row.query_selector("td:nth-of-type(4)")).text_content()
        order_date = await (
            await row.query_selector("td:nth-of-type(5)")
        ).text_content()
        billing_name = await (
            await row.query_selector("td:nth-of-type(6)")
        ).text_content()
        status = await (await row.query_selector("td:nth-of-type(7)")).text_content()
        refunded_amount = await (
            await row.query_selector("td:nth-of-type(8)")
        ).text_content()
        action_element = await row.query_selector("td:nth-of-type(9) a")
        action_link = await action_element.get_attribute("href")
        credit_memo_data.append(
            {
                "credit_memo_id": memo_id.strip(),
                "creation_date": creation_date.strip(),
                "order_id": order_id.strip(),
                "order_date": order_date.strip(),
                "billing_name": billing_name.strip(),
                "status": status.strip(),
                "refunded_amount": refunded_amount.strip(),
                "action_link": action_link.strip(),
            }
        )
    return credit_memo_data


async def filter_credit_memos_by_status(page, status):
    """
    Filter credit memos based on specific statuses such as 'Refunded', 'Pending', or 'Canceled'.

    [Usage preconditions]
    - You must be on the credit memos page of Magento Admin Panel before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    status : The status to filter credit memos by (e.g., 'Refunded', 'Pending', 'Canceled').

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains credit memo details filtered by the given status.
    """
    await page.goto("/admin/sales/creditmemo/")
    await page.goto("/admin/sales/creditmemo/")
    await page.click('button:has-text("Filters")')
    await page.click('select[name="status_filter"]')
    await page.select_option('select[name="status_filter"]', status)
    await page.click('button:has-text("Search")')
    rows = await page.query_selector_all("table > tbody > tr")
    credit_memos = []
    for row in rows:
        status_cell = await row.query_selector("td:nth-child(6)")
        if status_cell:
            result_status = await status_cell.inner_text()
            if result_status.strip() == status:
                credit_memo_data = {
                    "credit_memo": await row.query_selector(
                        "td:nth-child(1)"
                    ).inner_text(),
                    "created": await row.query_selector("td:nth-child(2)").inner_text(),
                    "order": await row.query_selector("td:nth-child(3)").inner_text(),
                    "order_date": await row.query_selector(
                        "td:nth-child(4)"
                    ).inner_text(),
                    "bill_to_name": await row.query_selector(
                        "td:nth-child(5)"
                    ).inner_text(),
                    "status": result_status.strip(),
                    "refunded": await row.query_selector(
                        "td:nth-child(7)"
                    ).inner_text(),
                    "action": await row.query_selector("td:nth-child(8)").inner_text(),
                }
                credit_memos.append(credit_memo_data)
    return credit_memos


async def get_credit_memo_statistics(page):
    """
    [Function description]
    Compiles statistics on the total number of credit memos, total refund amounts, and status distribution.

    This function automates the extraction of credit memo statistics from a Magento Admin page.
    It retrieves:
    - the total number of credit memos
    - total refund amounts
    - distribution of statuses

    [Usage preconditions]
    - The function expects you to be on the Magento Admin credit memos page.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        A dictionary containing the following keys:
        - "total_credit_memos" (int): Total number of credit memos.
        - "total_refund_amount" (float): Sum of all refund amounts.
        - "status_distribution" (dict): A dictionary with status as keys and their respective counts as values.
    """
    await page.goto("/admin/sales/creditmemo/")
    rows = await page.query_selector_all("table > tbody > tr")
    total_credit_memos = 0
    total_refund_amount = 0.0
    status_distribution = {}
    for row in rows:
        credit_memo_number = await (
            await row.query_selector("td:nth-child(2)")
        ).inner_text()
        if credit_memo_number:
            total_credit_memos += 1
        refund_text = await (await row.query_selector("td:nth-child(8)")).inner_text()
        refund_amount = float(refund_text.replace("$", "").replace(",", ""))
        total_refund_amount += refund_amount
        status_text = await (await row.query_selector("td:nth-child(7)")).inner_text()
        if status_text not in status_distribution:
            status_distribution[status_text] = 0
        status_distribution[status_text] += 1
    return {
        "total_credit_memos": total_credit_memos,
        "total_refund_amount": total_refund_amount,
        "status_distribution": status_distribution,
    }


async def identify_duplicate_customers(page):
    """
    [Function description]
    Identifies duplicate customers based on matching names or email addresses.

    This function scans customer data from the current page and identifies
    duplicates by either name or email address. It compiles a list of customers
    with matching names or email addresses, which helps in identifying duplicates
    within the customer data.

    [Usage preconditions]
    - This function requires that the browser is already on the customers page
      containing the customer data table.

    Args:
    page : A Playwright `Page` instance that controls browser automation.


    Returns:
    dict
        A dictionary with lists of duplicate names and emails:
        - "duplicate_names" (list): A list of duplicated customer names.
        - "duplicate_emails" (list): A list of duplicated customer emails.
    """
    await page.goto("/admin/customer/index/")
    name_counts = {}
    email_counts = {}
    rows = await page.query_selector_all("tr")
    for row in rows:
        name_element = await row.query_selector("td:nth-child(2)")
        email_element = await row.query_selector("td:nth-child(3)")
        name = await name_element.inner_text() if name_element else None
        email = await email_element.inner_text() if email_element else None
        if name:
            if name in name_counts:
                name_counts[name] += 1
            else:
                name_counts[name] = 1
        if email:
            if email in email_counts:
                email_counts[email] += 1
            else:
                email_counts[email] = 1
    duplicate_names = [name for name, count in name_counts.items() if count > 1]
    duplicate_emails = [email for email, count in email_counts.items() if count > 1]
    return {"duplicate_names": duplicate_names, "duplicate_emails": duplicate_emails}


async def navigate_to_data_transfer(page):
    """
    Navigates to the Data Transfer section of the Magento Admin interface, specifically the 'Import' page.

    This function automates the navigation to the 'Import' page found under 'System' > 'Data Transfer' in the
    Magento Admin menu. It uses the specified path within the menubar to reach the 'Import' link.

    [Usage preconditions]
    - You must be authenticated and on the Magento Admin Dashboard page before invoking this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Usage log:
    - Successfully navigated to the 'Import' page in the Data Transfer section using the correct menu hierarchy.
    """
    await page.goto("/admin/admin/dashboard/")
    await page.get_by_role("menubar").get_by_role("link", name="System").click()
    await page.get_by_role("link", name="Import", exact=True).click()


async def get_entity_types(page):
    """
    Retrieves the list of available entity types that can be imported.

    This function automates the extraction of all options from the 'Entity Type' dropdown
    located on the data import settings page. It collects the options such as Advanced Pricing,
    Products, Customers, etc., and returns them in a list format.

    [Usage preconditions]
    - This API retrieves entity type options for the import settings page **you are currently at**.
    - **You must already be on the Magento Admin import settings page before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of str
        A list of strings representing the entity types available in the dropdown.
    """
    await page.goto("/admin/admin/import/")
    entity_type_options = []
    entity_type_dropdown = await page.query_selector("select")
    options = await entity_type_dropdown.query_selector_all("option")
    for option in options:
        option_text = await option.inner_text()
        if option_text != "-- Please Select --":
            entity_type_options.append(option_text)
    return entity_type_options


async def confirm_file_size_limit(page):
    """
    [Function description]
    Retrieves information about file size limitations for the import functionality on the current page.

    This function searches for any text on the page that specifies file size limits for data import,
    helping users prepare datasets in compliance with the system requirements.

    [Usage preconditions]
    - You must already be on a page in a system where file import functionality and its related conditions
      are described, such as an admin panel or import settings page.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    str
        A string containing text that indicates the file size restriction for import, or an empty string
        if the condition is not found.
    """
    await page.goto("/admin/admin/import/")
    try:
        element = await page.query_selector(
            "xpath=//*[contains(text(), 'file isn't more than 8M')]"
        )
        if element:
            warning_text = await element.text_content()
            return warning_text.strip()
    except Exception as e:
        print(f"Error locating the condition message: {e}")
    return ""


async def get_import_guidelines_information(page):
    """
    [Function description]
    Searches the Magento Admin interface for guidelines or documentation related to import data formats, required fields, and constraints.

    This function automates the process of checking import settings in the Magento Admin panel to gather information on data import formats, required fields, and constraints.

    [Usage preconditions]
    - This API requires that you are already on the Magento Admin page where import options are accessible.
    - Ensure that the admin interface is fully loaded before executing the function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    dict
        A dictionary containing fields like "entity_types" and any specific guidelines, formats, and constraints found on the page.
    """
    await page.goto("/admin/admin/import/")
    import_guidelines = {}
    entity_type_dropdown_selector = 'select[name="entity_type"] '
    entity_type_dropdown = await page.query_selector(entity_type_dropdown_selector)
    if entity_type_dropdown:
        options_text = await page.evaluate(
            "Array.from(document.querySelectorAll('[name=\"entity_type\"] option')).map(option => option.textContent.trim())"
        )
        import_guidelines["entity_types"] = options_text
    return import_guidelines


async def sort_media_entries(page, sorting_option):
    """
    [Function description]
    Allows users to sort media entries by various parameters in the Magento Admin Panel media management interface.

    This function interacts with the sorting combobox in the media section to organize media entries
    based on the specified sorting option. Available options include:
    - 'Newest first'
    - 'Oldest first'
    - 'Directory: Descending'
    - 'Directory: Ascending'
    - 'Name: A to Z'
    - 'Name: Z to A'

    [Usage preconditions]
    - Ensure that you are already on the media management page of the Magento Admin Panel.
    - The function assumes the presence of a combobox to select sorting options.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    sorting_option (str): The sorting parameter. Must be one of the recognized options.

    Returns:
    None
    """
    await page.goto("/admin/media_gallery/media/index/")
    await page.goto("/admin/media_gallery/media/index/")
    options = {
        "Newest first": "Newest first",
        "Oldest first": "Oldest first",
        "Directory: Descending": "Directory: Descending",
        "Directory: Ascending": "Directory: Ascending",
        "Name: A to Z": "Name: A to Z",
        "Name: Z to A": "Name: Z to A",
    }
    combobox_selector = "select"
    if sorting_option in options:
        await page.select_option(combobox_selector, options[sorting_option])
