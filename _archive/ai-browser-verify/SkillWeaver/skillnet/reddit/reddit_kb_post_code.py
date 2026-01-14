async def navigate_to_subreddit(page, subreddit_name):
    """
    Navigate to a subreddit by its name on the Postmill website.

    This function navigates to the a subreddit specified by the `subreddit_name` input.

    Args:
        page: The Playwright page object.
        subreddit_name: the name of subreddit to navigate to.

    Usage Log:
    - Successfully subscribed to 'iphone13', 'massachusetts', 'news', 'UpliftingNews'.
    """
    await page.goto(f"/f/{subreddit_name}")

async def navigate_to_forum(page, forum_name):
    """
    Navigate to a forum by its name on the Postmill website.

    This function navigates to the a forum specified by the `forum_name` input.

    Args:
        page: The Playwright page object.
        forum_name: the name of forum to navigate to.

    Usage Log:
    - Successfully subscribed to 'iphone13', 'massachusetts', 'news', 'UpliftingNews'.
    """
    await page.goto(f"/f/{forum_name}")


async def extract_forum_names_and_urls(page):
    """
    [Function description]
    Extracts all forum names and URLs from the current page.

    This function automates the extraction of forum details from the page you are currently at.
    It gathers information about each forum, including:
    - Forum name
    - URL for navigation

    [Usage preconditions]
    - This API extracts forum information from the current page.
    - You must already be on the forums listing page before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The forum name.
        - "url" (str): The relative URL of the forum.
    """
    forums = []
    articles = await page.query_selector_all("main article")
    for article in articles:
        link_element = await article.query_selector("a")
        name = (await link_element.text_content()).strip()
        url = await link_element.get_attribute("href")
        forums.append({"name": name, "url": url})
    return forums


async def gather_forums_statistics(page):
    """
    [Function description]
    Gather all forums' subscriber and submission statistics directly from the list page.

    This function extracts data on each forum's subscriber count and submission statistics
    directly from the forums list page without navigating away.

    [Usage preconditions]
    - You must be on the forums list page before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "forum_name" (str): The name of the forum.
        - "subscribers" (str): The number of subscribers to the forum.
        - "submissions" (str): The submission statistics of the forum.
    """
    forums_data = []
    articles = await page.query_selector_all("article")
    for article in articles:
        heading_element = await article.query_selector("h2")
        heading_text = await heading_element.inner_text()
        forum_name = heading_text.split(" — ")[0]
        subscribers_elem = await article.query_selector(".subscriber-count")
        submissions_elem = await article.query_selector(".submission-stats")
        subscribers = await subscribers_elem.inner_text() if subscribers_elem else "N/A"
        submissions = await submissions_elem.inner_text() if submissions_elem else "N/A"
        forums_data.append(
            {
                "forum_name": forum_name,
                "subscribers": subscribers,
                "submissions": submissions,
            }
        )
    return forums_data


async def sort_and_list_forums_by_submission_count(page):
    """
    Sorts and lists forums by submission count.

    This function automates the sorting of forums based on their submission count and
    retrieves the list of forums, providing their names and respective URLs.

    Usage preconditions:
    - Ensure the page is on the forums listing section before invoking this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "name" (str): The name of the forum.
        - "url" (str): The URL leading to the forum-specific page.
    """
    button = await page.query_selector('button:text("Sort by: Submissions")')
    await button.click() if button else None
    articles = await page.query_selector_all("main article")
    forums = []
    for article in articles:
        heading_el = await article.query_selector("h2")
        heading_text = await heading_el.inner_text() if heading_el else ""
        link_el = await article.query_selector("a")
        link_href = await link_el.get_attribute("href") if link_el else ""
        forums.append({"name": heading_text, "url": link_href})
    return forums


async def retrieve_forum_statistics(page):
    """
    [Function description]
    Retrieves subscriber and submission information for each forum listed on the current page.

    This function automates the navigation and data extraction process to gather statistics from
    each forum's individual page, including:
    - Subscriber count
    - Submission count

    [Usage preconditions]
    - You must already be on the page that lists the forums before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "forum_name" (str): The name of the forum.
        - "subscribers" (str): The subscriber count of the forum.
        - "submissions" (str): The submission count of the forum.
    """
    forums_statistics = []
    forum_articles = await page.query_selector_all("main article")
    forum_links = []
    for forum_article in forum_articles:
        forum_link_element = await forum_article.query_selector("h2 a")
        forum_name = await forum_link_element.inner_text()
        forum_link = await forum_link_element.get_attribute("href")
        forum_links.append((forum_name, forum_link))
    for forum_name, forum_link in forum_links:
        await page.goto(forum_link)
        subscribers_selector = "span.subscribers-count"
        submissions_selector = "span.submissions-count"
        subscriber_element = await page.query_selector(subscribers_selector)
        submission_element = await page.query_selector(submissions_selector)
        subscribers = (
            await subscriber_element.inner_text() if subscriber_element else "N/A"
        )
        submissions = (
            await submission_element.inner_text() if submission_element else "N/A"
        )
        forums_statistics.append(
            {
                "forum_name": forum_name,
                "subscribers": subscribers,
                "submissions": submissions,
            }
        )
    return forums_statistics


async def filter_forums_by_submission_count(page):
    """
    [Function description]
    Filters the list of forums on the page by submission count.

    This function interacts with the webpage to ensure that forums
    are sorted by the number of submissions. It clicks on the corresponding
    dropdown menu or button to apply the sorting criteria.

    [Usage preconditions]
    - **You must be on a page containing the forums list**.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of str
        A list of forum titles sorted by submission count as displayed on the page.
    """
    sort_button = await page.query_selector('button:text("Sort by: Submissions")')
    if sort_button is not None:
        expanded_state = await sort_button.get_attribute("aria-expanded")
        if expanded_state == "false":
            await sort_button.click()
    forum_articles = await page.query_selector_all("article > h2 > a")
    forums = [(await article.inner_text()) for article in forum_articles]
    return forums


async def navigate_to_comments_section(page):
    """
    Navigate to the Comments section from the homepage.

    This function navigates from the Postmill homepage to the Comments section by clicking
    on the 'Comments' link in the main content area.

    Args:
    page (Page): The Playwright page object used to interact with the web page.

    Usage log:
    - Successfully navigated to the Comments section by clicking the 'Comments' link.

    Note:
    - Ensure the page object is directed to the homepage before calling this function.
    """
    await page.goto("/")
    await page.get_by_role("main").get_by_role("link", name="Comments").click()


async def extract_comment_data(page):
    """
    Extract data from the comments section including unique users, comment counts, and timestamps to analyze engagement.

    [Usage preconditions]
    - **You must already be on the page containing the comments section**.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        A dictionary containing the following keys:
        - "unique_users" (set): A set of unique usernames who have commented.
        - "comments" (list of dict): A list of dictionaries each representing a comment with the following keys:
            - "user" (str): The username of the commenter.
            - "timestamp" (str): The timestamp of the comment.
            - "text" (str): The actual comment text.
        - "comment_count" (int): Total number of comments retrieved.
    """
    comment_elements = await page.query_selector_all(".comment")
    unique_users = set()
    comments = []
    for element in comment_elements:
        user_element = await element.query_selector(".username")
        user = await user_element.inner_text() if user_element else "Unknown"
        timestamp_element = await element.query_selector(".timestamp")
        timestamp = (
            await timestamp_element.inner_text() if timestamp_element else "Unknown"
        )
        text_element = await element.query_selector(".comment-text")
        text = await text_element.inner_text() if text_element else ""
        unique_users.add(user)
        comments.append({"user": user, "timestamp": timestamp, "text": text})
    return {
        "unique_users": unique_users,
        "comments": comments,
        "comment_count": len(comments),
    }


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://example.com/comment-page")
        comment_data = await extract_comment_data(page)
        print(comment_data)
        await browser.close()


async def fetch_unique_commenters_with_profiles(page):
    """
    Extracts a list of unique users who have commented recently, along with links to their profiles.

    This function navigates the current page to retrieve a list of users who have left comments, ensuring each user is unique.
    Each entry is encapsulated as a dictionary containing the user's name and profile link.

    [Usage preconditions]
    - The function should be executed on a "Comments" page with a list of recent comments.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "username" (str): The name of the user.
        - "profile_link" (str): The URL to the user's profile.
    """
    unique_users = set()
    comment_articles = await page.query_selector_all("article")
    for article in comment_articles:
        heading = await article.query_selector('h1:has(a[href^="/user/"])')
        if heading:
            user_link = await heading.query_selector('a[href^="/user/"]')
            username = await (await user_link.get_property("textContent")).json_value()
            profile_link = await (await user_link.get_property("href")).json_value()
            if username and profile_link:
                unique_users.add((username.strip(), profile_link.strip()))
    user_list = [
        {"username": username, "profile_link": profile_link}
        for username, profile_link in unique_users
    ]
    return user_list


async def get_forum_list_from_recent_comments(page):
    """
    [Function description]
    Retrieves the list of forums associated with the recent comments, providing both forum names and their respective URLs.

    This function automates the extraction of forum names and URLs from the recent comments section of a discussion page.

    [Usage preconditions]
    - You must already be on a page that lists recent comments associated with forums.

    Args:
    page : A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - 'forum_name' (str): The name of the forum.
        - 'forum_url' (str): The URL of the forum.
    """
    forums = []
    articles = await page.query_selector_all("article")
    for article in articles:
        forum_link = await (await article.query_selector_all("a"))[1].get_attribute(
            "innerText"
        )
        forum_url = await (await article.query_selector_all("a"))[1].get_attribute(
            "href"
        )
        forums.append({"forum_name": forum_link, "forum_url": forum_url})
    return forums


async def extract_complete_comment_details(page):
    """
    Extracts complete details of comments from the current page.

    This function automates the extraction of detailed comment information from a
    discussion or forum page. It gathers data for each comment, including:

    - Username
    - Comment ID
    - Comment timestamp
    - Related post title
    - Links to Permalink and Parent comment if available

    [Usage preconditions]
    - The page must be loaded with recent comment articles visible.
    - Each comment section should have a structure that is valid for extraction.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each entry contains:
        - 'username': Username of the commenter.
        - 'comment_id': The unique identifier for the comment.
        - 'timestamp': The time when the comment was made.
        - 'post_title': The title of the post associated with the comment.
        - 'permalink': Direct link to the comment.
        - 'parent_link': Link to the parent comment if available.
    """
    comment_details = []
    articles = await page.query_selector_all("article")
    for article in articles:
        heading = await article.query_selector("h1")
        username_elem = await heading.query_selector('a[href^="/user/"]')
        username = await username_elem.inner_text()
        comment_id = await heading.inner_text()
        timestamp = comment_id.split(" wrote ")[-1]
        comment_id = comment_id.split(" ")[-1].strip("[]")
        post_title_elem = await article.query_selector('a[href^="/f/"]')
        post_title = await post_title_elem.inner_text()
        permalink_elem = await article.query_selector('a:has-text("Permalink")')
        permalink = await permalink_elem.get_attribute("href")
        parent_link_elem = await article.query_selector('a:has-text("Parent")')
        parent_link = (
            await parent_link_elem.get_attribute("href") if parent_link_elem else None
        )
        comment_details.append(
            {
                "username": username,
                "comment_id": comment_id,
                "timestamp": timestamp,
                "post_title": post_title,
                "permalink": permalink,
                "parent_link": parent_link,
            }
        )
    return comment_details


async def list_unique_users_and_comments(page):
    """
    [Function description]
    Retrieves a list of unique users and their respective comments from the current page.

    This function extracts user information and their comments from a webpage containing forum-style "recent comments" entries.
    It organizes the data so that each unique user has their commented-upon entries listed in association.

    [Usage preconditions]
    - This API extracts user and comment information from the forum page you are currently located at.
    - Ensure you are at a page consisting of the appropriately structured user-comment articles before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        A dictionary where each key represents a unique username, and the value is a list of comments attributed to that user.
        For example, {"username1": ["comment1", "comment2"], "username2": ["comment3"]}
    """
    unique_users_comments = {}
    articles = await page.query_selector_all("article")
    for article in articles:
        heading = await article.query_selector("h1")
        if heading:
            user_link = await heading.query_selector('a[href^="/user/"]')
            if user_link:
                username = await user_link.inner_text()
                comment_block = await article.query_selector(
                    "p, blockquote, .comment-text"
                )
                if comment_block:
                    comment_text = await comment_block.inner_text()
                    if username not in unique_users_comments:
                        unique_users_comments[username] = []
                    unique_users_comments[username].append(comment_text)
    return unique_users_comments


async def identify_most_active_forum(page):
    """
    [Function description]
    Identifies the most active forum based on the number of recent comments.

    This function processes the recent comments section to determine which forum
    has the highest number of associated comments, indicating activity. Each comment
    is linked to a forum through its URL, and this function counts the occurrences
    per forum.

    [Usage preconditions]
    - You must already be on the page with recent comments before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    dict:
        A dictionary containing the most active forum URL and the count of associated comments.
        - "forum_url" (str): The URL of the most active forum.
        - "count" (int): The number of comments associated with this forum.
    """
    articles = await page.query_selector_all("article")
    forum_count = {}
    for article in articles:
        link_elements = await article.query_selector_all('a[href*="/f/"]')
        for link_element in link_elements:
            forum_url = await link_element.get_attribute("href")
            if forum_url in forum_count:
                forum_count[forum_url] += 1
            else:
                forum_count[forum_url] = 1
    most_active_forum = max(forum_count.items(), key=lambda x: x[1])
    return {"forum_url": most_active_forum[0], "count": most_active_forum[1]}


async def extract_wiki_data(page):
    """
    [Function description]
    Extracts structured data from the wiki pages including all listed pages and recent changes.

    This function automates the extraction of detailed information from the Wiki section. It navigates
    through the sections 'All pages' and 'Recent changes', gathering data such as page names, update
    timestamps, and URLs for each entry.

    [Usage preconditions]
    - Ensure that you are on a webpage with access to the Wiki section containing 'All pages' and 'Recent changes'.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the wiki page.
        - "timestamp" (str): The last updated timestamp of the page.
        - "url" (str): The URL of the wiki page.
    """
    await page.goto("/wiki/_all")
    page_list_all = await page.query_selector_all("li.page-list-item")
    wiki_data = []
    for page_element in page_list_all:
        name = await (await page_element.query_selector("a.page-name")).text_content()
        url = await (await page_element.query_selector("a.page-name")).get_attribute(
            "href"
        )
        timestamp = await (
            await page_element.query_selector("time.page-timestamp")
        ).text_content()
        wiki_data.append(
            {"name": name.strip(), "timestamp": timestamp.strip(), "url": url.strip()}
        )
    await page.goto("/wiki/_recent")
    page_list_recent = await page.query_selector_all("li.page-list-item")
    for page_element in page_list_recent:
        name = await (await page_element.query_selector("a.page-name")).text_content()
        url = await (await page_element.query_selector("a.page-name")).get_attribute(
            "href"
        )
        timestamp = await (
            await page_element.query_selector("time.page-timestamp")
        ).text_content()
        wiki_data.append(
            {"name": name.strip(), "timestamp": timestamp.strip(), "url": url.strip()}
        )
    return wiki_data


async def extract_user_engagement_from_forums(page):
    """
    [Function description]
    Analyze user engagement in the forums section of the website.

    This function navigates to the Forums page and extracts user engagement metrics such as:
    - Number of active users
    - Number of comments
    - Number of interactions

    [Usage preconditions]
    - The current page must be able to navigate to the forums section.
    - The extracted data reflects general engagement metrics from forums across varying contents.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        A dictionary containing the user engagement metrics with keys:
        - "active_users" (int): Number of active users interacting on the forums.
        - "comments_count" (int): Total number of comments made in the forums.
        - "interactions_count" (int): Total number of other interactions in the forums.
    """
    await page.click('text="Forums"')
    active_users_element = await page.query_selector("div[data-type='active-users']")
    comments_element = await page.query_selector("div[data-type='comments-count']")
    interactions_element = await page.query_selector(
        "div[data-type='interactions-count']"
    )
    active_users_count = (
        await active_users_element.text_content() if active_users_element else "0"
    )
    comments_count = await comments_element.text_content() if comments_element else "0"
    interactions_count = (
        await interactions_element.text_content() if interactions_element else "0"
    )
    return {
        "active_users": int(active_users_count),
        "comments_count": int(comments_count),
        "interactions_count": int(interactions_count),
    }


async def extract_forum_metadata(page):
    """
    [Function description]
    Extracts metadata from forum pages to determine their creation dates, last updated timestamps, and size/popularity metrics.

    This function automates the gathering of metadata from a forum page, capturing essential metrics including:
    - Creation date
    - Last updated timestamp
    - Number of posts
    - Active discussions

    [Usage preconditions]
    - The page must be open to a forum where the metadata is accessible before calling this function.

    Args:
    page : A Playwright `Page` instance which controls browser automation.

    Returns:
    dict
        A dictionary containing metadata details including:
        - "creation_date" (str): The creation date of the forum in ISO format.
        - "last_updated" (str): The timestamp of the last update on the forum.
        - "num_posts" (int): Number of posts in the forum.
        - "active_discussions" (int): Number of active discussions.
    """
    metadata = {}
    creation_date_element = await page.query_selector('[data-selector="creation-date"]')
    if creation_date_element:
        metadata["creation_date"] = await (
            await creation_date_element.get_property("textContent")
        ).json_value()
    else:
        metadata["creation_date"] = None
    last_updated_element = await page.query_selector('[data-selector="last-updated"]')
    if last_updated_element:
        metadata["last_updated"] = await (
            await last_updated_element.get_property("textContent")
        ).json_value()
    else:
        metadata["last_updated"] = None
    num_posts_element = await page.query_selector('[data-selector="num-posts"]')
    if num_posts_element:
        metadata["num_posts"] = int(
            await (await num_posts_element.get_property("textContent")).json_value()
        )
    else:
        metadata["num_posts"] = 0
    active_discussions_element = await page.query_selector(
        '[data-selector="active-discussions"]'
    )
    if active_discussions_element:
        metadata["active_discussions"] = int(
            await (
                await active_discussions_element.get_property("textContent")
            ).json_value()
        )
    else:
        metadata["active_discussions"] = 0
    return metadata


async def extract_wiki_changes(page):
    """
    [Function description]
    Extracts the titles of all changed pages and their timestamps from the Wiki section's recent changes on the website.

    This function navigates to the recent changes section of the Wiki and retrieves information, including:
    - Page name
    - Timestamp of the change

    [Usage preconditions]
    - You must be on the Wiki main page of the website before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "name" (str): The title of the changed page.
        - "timestamp" (str): The timestamp of the change in ISO 8601 format.
    """
    await page.goto("/wiki/_recent")
    changes = await page.query_selector_all(".change-entry")
    result = []
    for change in changes:
        name_elem = await change.query_selector(".page-title")
        timestamp_elem = await change.query_selector(".change-timestamp")
        if name_elem and timestamp_elem:
            name = await name_elem.inner_text()
            timestamp = await timestamp_elem.get_attribute("datetime")
            result.append({"name": name, "timestamp": timestamp})
    return result


async def fetch_recent_changes(page):
    """
    Navigate the 'Recent changes' link and list new and updated wiki entries.

    This function automates the process of navigating to the 'Recent changes' section
    of a wiki and gathers the details of new and updated entries. It retrieves the
    entries' titles and any associated metadata or links presented on the page.

    [Usage preconditions]
    - Ensure you are on a page that contains a navigable 'Recent changes' link.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "title" (str): The title of the wiki entry.
        - "link" (str): The URL to the wiki entry.
        Additional relevant metadata might be included depending on the page structure.
    """
    await page.click('a[href="/wiki/_recent"]')
    entries = []
    entry_elements = await page.query_selector_all(".wiki-entry")
    for element in entry_elements:
        title = await (await element.query_selector(".entry-title")).text_content()
        link = await (await element.query_selector(".entry-link")).get_attribute("href")
        entries.append({"title": title, "link": link})
    return entries


async def user_registration_and_experience(page):
    """
    Facilitate the user registration process followed by navigation to test the experience for new users.

    This function guides a new user through the registration process and simulates typical navigation tasks
    to test the experience.

    [Usage preconditions]
    - You must be on the main page of the website where registration can be initiated.

    Args:
    page : A Playwright `Page` instance representing the browser page.

    Returns:
    dict
        A dictionary containing the registration and navigation status.
    """
    await page.click("text='Sign up'")
    await page.fill('input[name="username"]', "newuser")
    await page.fill('input[name="email"]', "newuser@example.com")
    await page.fill('input[name="password"]', "password123")
    await page.click('button:has-text("Register")')
    welcome_message = await page.inner_text("div.welcome-message")
    await page.click("text='Home'")
    await page.click("text='Forums'")
    await page.click("text='Wiki'")
    forums_content = await page.inner_text("div.forums-content")
    return {
        "registration_status": "Success" if "Welcome" in welcome_message else "Failure",
        "navigation_experience": "Test Completed",
    }


async def navigate_to_submissions_section(page):
    """
    Navigate to the Submissions section from the homepage.

    This function uses the Playwright API to check if it is already on the Submissions page.
    If not, it navigates to the Postmill homepage first and then to the Submissions section
    within the main content area. It primarily utilizes relative URL navigation to ensure
    the user is redirected correctly.

    Args:
        page (Page): The Playwright page object used to interact with the web page.

    Usage log:
    - Successfully navigated to the Submissions section directly from the homepage using the main link.
    - Handled the scenario when already on the Submissions page without performing additional navigation.

    Note:
    - Ensure the page object is directed and initialized to the homepage if this function is called directly
      without being on the homepage.
    - This function does not attempt to navigate when already on the Submissions section.
    """
    current_url = page.url
    if current_url.endswith("/"):
        return
    await page.goto("/")
    await page.get_by_role("main").get_by_role("link", name="Submissions").click()


async def navigate_to_submissions(page):
    """
    [Function description]
    Navigates to the 'Submissions' section to view the main feed.

    This function automates the navigation to the 'Submissions' section, which serves as the hub for content sharing and interaction.

    [Usage preconditions]
    - Ensure the Playwright page instance is already initialized and on a relevant starting page where this function can be executed correctly.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    None
    """
    await page.click("text=Submissions")


async def analyze_user_registration_process(page):
    """
    [Function description]
    Automates the user registration process and evaluates the initial navigation experience on a website.

    This function navigates a website's registration page, submits user details
    to create a new account, and then checks the initial navigation experience
    after successful registration, focusing on the user-friendliness of the
    interface presented to new users.

    [Usage preconditions]
    - You must be on a website's homepage or any navigable page with access to
      the registration link before calling this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        A dictionary containing:
        - "registration_success" (bool): Whether registration was successful.
        - "welcome_experience" (list of str): List of observed navigation elements
          promoting user engagement post-registration.
    """
    await page.click('text="Sign up"')
    await page.fill('input[name="username"]', "testuser")
    await page.fill('input[name="password"]', "password123")
    await page.fill('input[name="email"]', "testuser@example.com")
    await page.click('button:has-text("Register")')
    registration_success = await page.is_visible("text=Welcome, testuser")
    welcome_experience = []
    if await page.is_visible('button:has-text("Filter on: Featured")'):
        welcome_experience.append("Filter on: Featured")
    if await page.is_visible('button:has-text("Sort by: Hot")'):
        welcome_experience.append("Sort by: Hot")
    return {
        "registration_success": registration_success,
        "welcome_experience": welcome_experience,
    }

async def quick_post_submission(page, url, title, body=None, forum_name="AskReddit"):
    """
    Automates the process of submitting a post on Postmill.

    This function navigates to the submission page, selects a specified forum, fills in the URL,
    Title, and optionally the Body of the post, and submits the form.

    Parameters:
    - page: The Playwright page object.
    - url: The URL to be submitted.
    - title: The title of the submission.
    - body: Optional body content for the submission.
    - forum_name: The name of the forum to post in (default is "AskReddit").

    Usage log:
    - Ensure the page is fully loaded and elements are visible before interaction.
    - Verify that the correct selectors are used for each element.
    - Handle any potential timeouts by ensuring elements are interactable.
    - Added explicit waits to ensure elements are ready before interaction.
    - Updated to ensure the URL radio button is checked before filling the URL textbox.
    - Encountered repeated timeouts when filling the URL textbox, suggesting a need for improved element readiness checks.
    - Updated to include explicit waits for elements to be visible and interactable before filling.
    - Updated to include additional checks for URL textbox visibility to prevent timeouts.
    - Repeated timeouts indicate a need for further investigation into element readiness.
    - Updated to ensure the URL radio button is checked before filling the URL textbox to prevent visibility issues.
    """
    await page.goto("/submit")
    await page.wait_for_load_state("networkidle")
    url_radio = page.get_by_role("radio", name="URL")
    if not await url_radio.is_checked():
        await url_radio.check()
    url_textbox = page.get_by_role("textbox", name="URL")
    await url_textbox.wait_for(state="visible")
    await url_textbox.fill(url)
    title_textbox = page.get_by_role("textbox", name="Title This field is required.")
    await title_textbox.wait_for(state="visible")
    await title_textbox.fill(title)
    if body:
        body_textbox = page.get_by_role("textbox", name="Body")
        await body_textbox.wait_for(state="visible")
        await body_textbox.fill(body)
    forum_combobox = page.get_by_role("combobox", name="Choose one…")
    await forum_combobox.wait_for(state="visible")
    await forum_combobox.click()
    forum_option = page.get_by_role("option", name=forum_name.lower(), exact=True)
    await forum_option.wait_for(state="visible")
    await forum_option.click()
    submit_button = page.get_by_role("button", name="Create submission")
    await submit_button.wait_for(state="visible")
    await submit_button.click()


async def extract_recent_submissions(page):
    """
    Extract comprehensive data regarding recent submissions.

    This function automates the extraction of detailed information from recent submissions available
    on the current webpage. It gathers information for each submission, including:

    - Title
    - Author
    - Interaction metrics
    - Timestamp

    [Usage preconditions]
    - This API retrieves recent submission information for generalized pages showing submissions.
    - You must already be on a webpage that lists submissions before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title of the submission.
        - "author" (str): The name of the submission author.
        - "interaction_metrics" (str): Metrics showing user interactions (e.g., upvotes, comments).
        - "timestamp" (str): The timestamp of the submission in ISO 8601 format.
    """
    submissions = []
    submission_elements = await page.query_selector_all("div.submission")
    for element in submission_elements:
        title = await (await element.query_selector(".submission-title")).inner_text()
        author = await (await element.query_selector(".submission-author")).inner_text()
        interaction_metrics = await (
            await element.query_selector(".submission-metrics")
        ).inner_text()
        timestamp = await (
            await element.query_selector(".submission-timestamp")
        ).inner_text()
        submissions.append(
            {
                "title": title,
                "author": author,
                "interaction_metrics": interaction_metrics,
                "timestamp": timestamp,
            }
        )
    return submissions


async def extract_submission_features(page):
    """
    [Function description]
    Extracts and lists prominent features of the newest submissions
    from the Postmill website.

    This function automates the extraction of essential details from the
    latest submissions section on the Postmill homepage. It gathers data
    regarding trending topics, the number of votes received by submissions,
    and the diversity of interaction such as likes and comments.

    [Usage preconditions]
    - The function retrieves information from the Submissions page on
      the Postmill website.
    - Ensure you are on the Postmill homepage where submissions are listed
      before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title or trending topic of the submission.
        - "votes" (int): Number of votes the submission has received.
        - "interactions" (dict): A dictionary detailing interaction diversity
          with keys "likes" and "comments".
    """
    submissions = []
    submission_elements = await page.query_selector_all(".submission-entry")
    for submission in submission_elements:
        title = await (
            await submission.query_selector(".submission-title")
        ).inner_text()
        votes_text = await (
            await submission.query_selector(".votes-count")
        ).inner_text()
        votes = int(votes_text)
        likes_text = await (
            await submission.query_selector(".likes-count")
        ).inner_text()
        comments_text = await (
            await submission.query_selector(".comments-count")
        ).inner_text()
        likes = int(likes_text)
        comments = int(comments_text)
        submissions.append(
            {
                "title": title,
                "votes": votes,
                "interactions": {"likes": likes, "comments": comments},
            }
        )
    return submissions


async def analyze_filter_options(page):
    """
    [Function description]
    Examines the functionality and variety of filtering options available on the 'Submissions' and 'Comments' sections.

    This function navigates through the 'Submissions' and 'Comments' sections of the current page,
    examining all available filter options with the possibility of expanding any unexpanded filters.

    [Usage preconditions]
    - Assumes you are already on a webpage containing 'Submissions' and 'Comments'.

    Args:
    page : A Playwright `Page` instance representing the current browsing context.

    Returns:
    dict
        A dictionary containing the types and states of available filters in both 'Submissions' and 'Comments' sections:
        - 'submissions_filters': A list representing available filters in the Submissions;
        - 'comments_filters': A list representing available filters in the Comments.
    """
    submissions_filters = []
    submissions_elements = await page.query_selector_all("main >> button")
    for element in submissions_elements:
        filter_text = await element.inner_text()
        is_expanded = "expanded" in await element.get_attribute("class")
        submissions_filters.append((filter_text, is_expanded))
    comments_link = await page.query_selector("main >> text=Comments")
    await comments_link.click()
    comments_filters = []
    comments_elements = await page.query_selector_all("main >> button")
    for element in comments_elements:
        filter_text = await element.inner_text()
        is_expanded = "expanded" in await element.get_attribute("class")
        comments_filters.append((filter_text, is_expanded))
    return {
        "submissions_filters": submissions_filters,
        "comments_filters": comments_filters,
    }


async def monitor_user_engagement_in_comments(page):
    """
    [Function description]
    Retrieve user engagement in the comments section by listing users and their activity levels over time.

    This function automates the extraction of user engagement information from the comments section of a webpage.
    For each user who comments, it notes their activity level which could be reflected by the number of comments or frequency.

    [Usage preconditions]
    - You should already be on the page containing the comments section for the desired content.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "username" (str): The username of the engager.
        - "activity_level" (int): The frequency or count of the user's comments.
    """
    comment_items_selector = "div.comment-item"
    username_selector = "span.username"
    comment_elements = await page.query_selector_all(comment_items_selector)
    user_activity = {}
    for comment_element in comment_elements:
        username_elem = await comment_element.query_selector(username_selector)
        username = await username_elem.inner_text()
        if username in user_activity:
            user_activity[username] += 1
        else:
            user_activity[username] = 1
    activity_list = [
        {"username": user, "activity_level": activity_level}
        for user, activity_level in user_activity.items()
    ]
    return activity_list


async def retrieve_recent_submissions(page):
    """
    [Function description]
    Retrieves titles, authors, votes, and comments from recent submissions on the Postmill platform.

    This function automates the extraction of information from recent submissions, including:
    - Submission title
    - Author name
    - Number of votes
    - Number of comments

    [Usage preconditions]
    - You must already be on the Postmill main page containing the recent submissions before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title of the submission.
        - "author" (str): The name of the submission author.
        - "votes" (int): The number of votes the submission has received.
        - "comments" (int): The number of comments on the submission.
    """
    submissions = []
    submission_elements = await page.query_selector_all(".submission")
    for element in submission_elements:
        title_element = await element.query_selector(".submission-title")
        author_element = await element.query_selector(".submission-author")
        votes_element = await element.query_selector(".submission-votes")
        comments_element = await element.query_selector(".submission-comments")
        title = await (await title_element.inner_text()).strip()
        author = await (await author_element.inner_text()).strip()
        votes = int(await (await votes_element.inner_text()).strip())
        comments = int(await (await comments_element.inner_text()).strip())
        submissions.append(
            {"title": title, "author": author, "votes": votes, "comments": comments}
        )
    return submissions


async def collect_forum_data(page):
    """
    [Function description]
    Extracts forum information including creation dates, subscriber numbers, and activity levels.

    This function automates the extraction of data pertaining to forum trends which includes:
    - Creation date of the forum
    - Number of subscribers
    - Activity levels

    [Usage preconditions]
    - The page should already be on the forums dashboard before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the forum.
        - "creation_date" (str): The creation date of the forum.
        - "subscribers" (str): The number of subscribers.
        - "activity_level" (str): Description or metric of how active the forum is.
    """
    forums = []
    forum_elements = await page.query_selector_all(".forum-class")
    for forum in forum_elements:
        name = await (await forum.query_selector(".forum-name")).inner_text()
        creation_date = await (
            await forum.query_selector(".creation-date")
        ).inner_text()
        subscribers = await (
            await forum.query_selector(".subscriber-count")
        ).inner_text()
        activity_level = await (
            await forum.query_selector(".activity-level")
        ).inner_text()
        forums.append(
            {
                "name": name,
                "creation_date": creation_date,
                "subscribers": subscribers,
                "activity_level": activity_level,
            }
        )
    return forums


async def explore_links_from_error_page(page):
    """
    [Function description]
    Validates and follows operational links from a 404 error page, ensuring accessibility across different sections of the website.

    This function automates navigation from a 404 error page through links such as 'Home', 'Forums', or 'Wiki', validating their accessibility by navigating to them and checking successful load.

    [Usage preconditions]
    - This API navigates links for accessibility testing starting from a 404 error page.
    - **You must already be on the 404 error page before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.


    Returns:
    list
        A list of strings representing successful navigations.
    """
    successful_links = []
    links_to_navigate = [
        {"name": "Home", "url": "/"},
        {"name": "Forums", "url": "/forums"},
        {"name": "Wiki", "url": "/wiki"},
    ]
    for link in links_to_navigate:
        await page.goto(link["url"])
        state = await page.evaluate("document.readyState")
        if state == "complete":
            successful_links.append(link["name"])
    return successful_links


async def access_login(page):
    """
    Perform the action to access the 'Log In' page.

    [Function description]
    Automates the process of navigating to the 'Log In' page from the current page.

    [Usage preconditions]
    - The starting point is a page with a 'Log In' link.
    - The link should lead to the login functionality of the website.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    None
    """
    await (await page.query_selector('a[href="/login"]')).click()


async def access_signup(page):
    """
    Perform the action to access the 'Sign Up' page.

    [Function description]
    Automates the process of navigating to the 'Sign Up' page from the current page.

    [Usage preconditions]
    - The starting point is a page with a 'Sign Up' link.
    - The link should lead to the subscription or account creation functionality of the website.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    None
    """
    await (await page.query_selector('a[href="/registration"]')).click()


async def extract_recent_changes_contributions(page):
    """
    [Function description]
    Extracts data on recent contributions from the 'Recent changes' section in the Wiki,
    identifying which entries have been most frequently updated or discussed.

    [Usage preconditions]
    - Ensure you are on the Wiki's 'Recent changes' page before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title of the Wiki entry.
        - "edits" (int): The number of edits made to the entry.
        - "discussions" (int): The count of discussions related to the entry.
    """
    await page.goto("/wiki/_recent")
    entries_selector = ".recent-change-entry"
    entries = await page.query_selector_all(entries_selector)
    changes_list = []
    for entry in entries:
        title_element = await entry.query_selector(".title")
        edits_element = await entry.query_selector(".edits")
        discussions_element = await entry.query_selector(".discussions")
        title = await (await title_element.inner_text()) if title_element else ""
        edits = int(await (await edits_element.inner_text()) if edits_element else 0)
        discussions = int(
            await (await discussions_element.inner_text()) if discussions_element else 0
        )
        changes_list.append(
            {"title": title, "edits": edits, "discussions": discussions}
        )
    return changes_list


async def navigate_to_featured_forums(page):
    """
    Navigate to the featured forums section on the homepage by applying the 'Featured' filter.

    This function navigates to the Postmill homepage, locates the 'Filter on: Featured' button,
    and clicks it to display the featured forums.

    Args:
        page (Page): The Playwright page object used to interact with the web page.

    Usage log:
    - Successfully navigated to the 'Featured forums' section using the filter button. No featured forums were displayed at the time.

    Note:
    - Ensure that 'Featured' forums exist for content to be displayed after filtering.

    """
    await page.goto("/")
    await page.get_by_role("button", name="Filter on: Featured").click()


async def extract_featured_submissions_info(page):
    """
    [Function description]
    Extracts information about featured submissions including titles, authors, timestamps, votes, and comments.

    This function navigates the page to collect all featured submissions data, providing insight into trending content.
    Information gathered includes:
      - Submission title
      - Author name
      - Submission timestamp
      - Number of votes
      - Number of comments

    [Usage preconditions]
    - You must already be on the page listing featured submissions before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "title" (str): The title of the submission.
        - "author" (str): The name of the author.
        - "timestamp" (str): The time when the submission was made.
        - "votes" (int): The number of votes the submission has received.
        - "comments" (int): The number of comments on the submission.
    """
    submission_elements = await page.query_selector_all(
        '[data-qa="featured-submission"]'
    )
    featured_submissions = []
    for submission in submission_elements:
        title_element = await submission.query_selector('[data-qa="submission-title"]')
        author_element = await submission.query_selector(
            '[data-qa="submission-author"]'
        )
        timestamp_element = await submission.query_selector(
            '[data-qa="submission-timestamp"]'
        )
        votes_element = await submission.query_selector('[data-qa="submission-votes"]')
        comments_element = await submission.query_selector(
            '[data-qa="submission-comments"]'
        )
        title = await title_element.inner_text()
        author = await author_element.inner_text()
        timestamp = await timestamp_element.inner_text()
        votes = await votes_element.inner_text()
        comments = await comments_element.inner_text()
        featured_submissions.append(
            {
                "title": title,
                "author": author,
                "timestamp": timestamp,
                "votes": int(votes),
                "comments": int(comments),
            }
        )
    return featured_submissions


async def get_recent_wiki_changes(page):
    """
    [Function description]
    Navigates to the Wiki section and extracts details of the latest page changes such as titles, timestamps, and URLs.

    This function helps in tracking updates and modifications within the Wiki by automating the process of gathering recent change details.
    It gathers key information about each change including:

    - Change title
    - Change timestamp
    - Change URL

    [Usage preconditions]
    - You must be on a page that has a direct link to the Wiki section.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title of the page change.
        - "timestamp" (str): The timestamp of the change.
        - "url" (str): The URL to the page change.
    """
    await page.click('a:has-text("Wiki")')
    changes_info = []
    recent_changes = await page.query_selector_all(".recent-change")
    for change in recent_changes:
        title_element = await change.query_selector(".change-title")
        title = await (await title_element.get_property("innerText")).json_value()
        timestamp_element = await change.query_selector(".change-timestamp")
        timestamp = await (
            await timestamp_element.get_property("innerText")
        ).json_value()
        url_element = await change.query_selector(".change-url a")
        url = await (await url_element.get_property("href")).json_value()
        changes_info.append({"title": title, "timestamp": timestamp, "url": url})
    return changes_info


async def extract_hot_submissions(page):
    """
    [Function description]
    Retrieves submissions currently ordered by 'Hot' from the submissions page including their titles, authors, interactions, and votes.

    This function automates the process of sorting submissions by 'Hot' and extracting relevant information for each submission, including:
    - Title
    - Author
    - Interactions (comments, shares etc.)
    - Votes

    [Usage preconditions]
    - This API assumes that you are already on the page where submissions are displayed.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title of the submission.
        - "author" (str): The name of the author of the submission.
        - "interactions" (str): Details of the interactions for the submission.
        - "votes" (str): The number of votes the submission has received.
    """
    button = await page.query_selector("button:text('Sort by: Hot')")
    if button:
        await button.click()
    submissions = await page.query_selector_all(".submission")
    submissions_info = []
    for submission in submissions:
        title_element = await submission.query_selector(".title")
        author_element = await submission.query_selector(".author")
        interactions_element = await submission.query_selector(".interactions")
        votes_element = await submission.query_selector(".votes")
        title = await title_element.inner_text() if title_element else ""
        author = await author_element.inner_text() if author_element else ""
        interactions = (
            await interactions_element.inner_text() if interactions_element else ""
        )
        votes = await votes_element.inner_text() if votes_element else ""
        submissions_info.append(
            {
                "title": title,
                "author": author,
                "interactions": interactions,
                "votes": votes,
            }
        )
    return submissions_info


async def navigate_to_user_registration_and_login(page):
    """
    [Function description]
    Facilitates access to the functionality for user registration and login by extracting navigation paths.

    This function automates navigation to user registration and login pages, allowing users to access these pages directly.

    It will navigate to:
    - User login page
    - User registration page

    [Usage preconditions]
    - You must already be on the website before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    dict
        A dictionary containing navigation paths for login and registration,
        with keys:
        - "login_path" (str): The URL path for the login page.
        - "registration_path" (str): The URL path for the registration page.
    """
    login_path = "/login"
    registration_path = "/registration"
    await page.goto(login_path)
    await page.goto(registration_path)
    return {"login_path": login_path, "registration_path": registration_path}


async def search_and_extract_submissions(page, query):
    """
    [Function description]
    Searches for submissions based on a provided query and extracts detailed information.

    This function performs a search using the provided query string, filtering submissions
    by titles or authors, and retrieves detailed information including:
    - Title
    - Submission timestamp
    - Number of votes
    - Number of comments

    [Usage preconditions]
    - This API assumes you are already on the page where submission search functionality is available.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    query : A string representing the search query for titles or authors.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title of the submission.
        - "timestamp" (str): The timestamp when the submission was made.
        - "votes" (int): The number of votes on the submission.
        - "comments" (int): The number of comments on the submission.
    """
    search_box = await page.query_selector('input[placeholder="Search query"]')
    if search_box is not None:
        await search_box.fill(query)
        await search_box.press("Enter")
    submissions = []
    submission_elements = await page.query_selector_all(
        ".submission-list .submission-item"
    )
    for element in submission_elements:
        title_element = await element.query_selector(".submission-title")
        timestamp_element = await element.query_selector(".submission-timestamp")
        votes_element = await element.query_selector(".submission-votes")
        comments_element = await element.query_selector(".submission-comments")
        if title_element and timestamp_element and votes_element and comments_element:
            title = await title_element.inner_text()
            timestamp = await timestamp_element.inner_text()
            votes = int(await votes_element.inner_text())
            comments = int(await comments_element.inner_text())
            submissions.append(
                {
                    "title": title,
                    "timestamp": timestamp,
                    "votes": votes,
                    "comments": comments,
                }
            )
    return submissions


async def sort_submissions_by_hot(page):
    """
    [Function description]
    Automates the interaction with a page element to sort submissions by their "Hot" status.

    This function finds and clicks the "Sort by: Hot" button to change the sorting order of submissions on the current page to highlight popular content.

    [Usage preconditions]
    - The page being controlled should have a sorting button labeled "Sort by: Hot" available.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    None
    """
    sort_button = page.locator("button", has_text="Sort by: Hot")
    if await sort_button.is_visible():
        await sort_button.click(force=True)


async def extract_all_submissions_data(page):
    """
    Extracts comprehensive data for all submissions present on the current page.

    This function automates the extraction of detailed information from each submission
    on the page, aiming to gather comprehensive details such as:

    - Submission title
    - Author name
    - Submission timestamp

    Usage Preconditions:
    - The current page should be the submissions listing page.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title of the submission.
        - "author" (str): The author of the submission.
        - "timestamp" (str): The timestamp of the submission.
    """
    submissions_data = []
    submissions = await page.query_selector_all('article[data-qa="submission"]')
    for submission in submissions:
        title_element = await submission.query_selector("h2.title")
        author_element = await submission.query_selector("span.author")
        timestamp_element = await submission.query_selector("time.timestamp")
        title = await (await title_element).text_content() if title_element else ""
        author = await (await author_element).text_content() if author_element else ""
        timestamp = (
            await (await timestamp_element).text_content() if timestamp_element else ""
        )
        submissions_data.append(
            {"title": title, "author": author, "timestamp": timestamp}
        )
    return submissions_data


async def extract_comments_data(page):
    """
    [Function description]
    Extracts all comments data from the webpage you are currently at.

    This function automates the extraction of comments from the current page.
    It gathers information about each comment, including:

    - Comment text
    - Author name

    [Usage preconditions]
    - This API retrieves comments information for the webpage **you are currently at**.
    - **You must already be on the webpage containing comments before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "text" (str): The text content of the comment.
        - "author" (str): The name of the comment author.
    """
    comments_data = []
    comments_elements = await page.query_selector_all(".comment-element-selector")
    for comment_element in comments_elements:
        text = await (
            await comment_element.query_selector(".text-selector")
        ).text_content()
        author = await (
            await comment_element.query_selector(".author-selector")
        ).text_content()
        comments_data.append({"text": text, "author": author})
    return comments_data


async def navigate_and_extract_wiki_data(page):
    """
    Navigate to the Wiki section and extract data.

    This function automates navigation to the Wiki section of a website and extracts
    comprehensive text data from the page. It collects the content visible on this
    section for further processing or analysis.

    [Usage preconditions]
    - The function assumes that you are on a website with a '/wiki' section accessible
      through a relative URL.
    - Make sure you are logged in or have appropriate access if required to view the Wiki content.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    str
        The text content of the Wiki page extracted as a raw string.
    """
    await page.goto("/wiki")
    content_element = await page.query_selector("main")
    text_content = await content_element.text_content() if content_element else ""
    return text_content


async def find_accessible_links_on_error_page(page):
    """
    [Function description]
    This function identifies and retrieves all clickable links present on a 'Page not found' error page,
    verifying which links are operationally accessible. It helps in understanding the navigational paths,
    providing insight into links that can still be accessed despite the page error.

    [Usage preconditions]
    - You must be on a 'Page not found' error page before calling this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "text" (str): The accessible link text.
        - "url" (str): The URL the link navigates to, if clickable.
    """
    links = await page.query_selector_all("a")
    accessible_links = []
    for link in links:
        href = await link.get_attribute("href")
        link_text = await link.inner_text()
        if href:
            accessible_links.append({"text": link_text, "url": href})
    return accessible_links


async def explore_error_page_metadata(page):
    """
    [Function description]
    Explores the HTML of the error page to find metadata, identifiers, or tracking information that could provide insight into the cause of the error or server responses.

    This function inspects the meta tags and other structured HTML elements to extract information that may be relevant in identifying the cause of an error.

    [Usage preconditions]
    - This API assumes that the page being analyzed is an error page and that it contains HTML content consistent with typical web standards.
    - **You must already be on the error page before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        A dictionary containing metadata and tracking insights including:
        - "meta_tags": List of meta tags found on the page.
        - "identifiers": List of unique IDs or classes used within the body of the page.
        - "tracking_info": Any tracking-related tags or attributes if present.
    """
    metadata = {}
    meta_tags = await page.query_selector_all("meta")
    metadata_info = []
    for meta in meta_tags:
        name = await meta.get_attribute("name")
        content = await meta.get_attribute("content")
        if name and content:
            metadata_info.append({"name": name, "content": content})
        elif content:
            metadata_info.append({"content": content})
    metadata["meta_tags"] = metadata_info
    identifiers = []
    all_elements = await page.query_selector_all("*")
    for element in all_elements:
        element_id = await element.get_attribute("id")
        class_name = await element.get_attribute("class")
        if element_id:
            identifiers.append({"id": element_id})
        if class_name:
            identifiers.append({"class": class_name})
    metadata["identifiers"] = identifiers
    tracking_info = []
    data_tracking_elements = await page.query_selector_all("[data-tracking]")
    for element in data_tracking_elements:
        tracking = await element.get_attribute("data-tracking")
        if tracking:
            tracking_info.append(tracking)
    metadata["tracking_info"] = tracking_info
    return metadata


async def extract_navigation_paths(page):
    """
    [Function description]
    Extracts likely navigational paths or use cases leading to a 'Page not found' error.

    This function automates the retrieval of link information from a 'Page not found' error page.
    It gathers data on potential navigation paths users might follow, aiming to provide insights
    for UX improvements or debugging of navigation issues.

    [Usage preconditions]
    - You must already be on a 'Page not found' error page before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "text" (str): The link text.
        - "url" (str): The destination URL of the link.
    """
    navigation_links = []
    links = await page.query_selector_all("a")
    for link in links:
        text = await (await link.get_property("textContent")).json_value()
        href = await (await link.get_property("href")).json_value()
        navigation_links.append({"text": text.strip(), "url": href.strip()})
    return navigation_links


async def extract_featured_forums(page):
    """
    Extracts the list of featured forums including their names, submission counts, and links.

    [Function description]
    This function automates the extraction of featured forum details from a webpage.
    It gathers the name of the forum, the number of submissions, and the link associated with each forum.

    [Usage preconditions]
    - You must already be on the page that displays the featured forums before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the forum.
        - "submissions" (int): The number of submissions in the forum.
        - "link" (str): The URL link to the forum.
    """
    forums = await page.query_selector_all(".forum-entry")
    result = []
    for forum in forums:
        name_element = await forum.query_selector(".forum-name")
        name = await name_element.text_content() if name_element else "N/A"
        submissions_element = await forum.query_selector(".submission-count")
        submissions_text = (
            await submissions_element.text_content() if submissions_element else "0"
        )
        submissions = int(submissions_text.split()[0]) if submissions_element else 0
        link_element = await forum.query_selector("a.forum-link")
        link = await link_element.get_attribute("href") if link_element else "#"
        result.append({"name": name, "submissions": submissions, "link": link})
    return result


async def gather_user_interactions_for_submissions(page):
    """
    Gather data on user interactions for each submission, including votes and comments.

    This function automates the extraction of user interaction details from the current page of a submissions list.
    It gathers information about each submission including:

    - Vote count
    - Comments attached to the submission

    [Usage preconditions]
    - This API gathers user interaction information for submissions on the page **you are currently at**.
    - **You must already be on the webpage containing the list of submissions before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "votes" (int): The number of votes for the submission.
        - "comments" (list of str): The comments attached to the submission.
    """
    submissions_data = []
    submission_elements = await page.query_selector_all(".submission")
    for submission in submission_elements:
        vote_element = await submission.query_selector(".vote-count")
        vote_count = await (await vote_element.inner_text()) if vote_element else 0
        comment_elements = await submission.query_selector_all(".comment")
        comments = [
            (await (await comment.inner_text()).strip()) for comment in comment_elements
        ]
        submissions_data.append({"votes": int(vote_count), "comments": comments})
    return submissions_data


async def search_submissions(page, keyword):
    """
    [Function description]
    Enables search functionality to find submissions by keywords and extracts detailed submission information from the current page.

    This function automates the process of performing a search for submissions based on a given keyword and collects relevant details
    about each matched submission on the resulting page.

    [Usage preconditions]
    - You must be on a page that supports submission search functionality.

    Args:
    page :  A Playwright `Page` instance to drive browser automation.
    keyword: A string representing the keyword used for searching submissions.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title of the submission.
        - "url" (str): The URL to view the submission.
        - "author" (str): The name of the submission author.
        - "timestamp" (str): The time when the submission was created.
    """
    search_box = await page.query_selector('input[aria-label="Search query"]')
    if search_box:
        await search_box.fill(keyword)
        await search_box.press("Enter")
    else:
        raise Exception("Search box not found")
    submissions = []
    submission_elements = await page.query_selector_all(
        "selector-for-submission-elements"
    )
    for element in submission_elements:
        title_elem = await element.query_selector("selector-for-title")
        title = await title_elem.inner_text()
        url_elem = await element.query_selector("selector-for-url")
        url = await url_elem.get_attribute("href")
        author_elem = await element.query_selector("selector-for-author")
        author = await author_elem.inner_text()
        timestamp_elem = await element.query_selector("selector-for-timestamp")
        timestamp = await timestamp_elem.inner_text()
        submissions.append(
            {"title": title, "url": url, "author": author, "timestamp": timestamp}
        )
    return submissions


async def extract_comments(page):
    """
    Extract all comments details, including authors and content.

    This function navigates through a page containing comments and retrieves details
    for each comment including:
    - Comment author
    - Comment text/content

    [Usage preconditions]
    - Ensure you are already on the comments page.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "author" (str): The name of the comment author.
        - "content" (str): The text content of the comment.
    """
    comments_elements = await page.query_selector_all("main article")
    comments_data = []
    for comment_element in comments_elements:
        heading_element = await comment_element.query_selector("h1 > a")
        author = await heading_element.text_content() if heading_element else "Unknown"
        content = await comment_element.text_content()
        comments_data.append({"author": author, "content": content})
    return comments_data


async def list_and_count_unique_active_users(page):
    """
        Lists and counts all unique active users in the comments section of the current page.

        This function gathers usernames from the comments section of the current page, where each username is
    derived from the user profile link within each comment. It then computes and returns the list of unique
    users and the number of such users.

        Usage preconditions:
        - Ensure that the `page` instance is already on the comments section page before calling this function.

        Args:
        page: A Playwright `Page` instance that controls browser automation.

        Returns:
        dict of {
            "unique_users": list,
            "unique_count": int
        }
            A dictionary containing:
            - "unique_users": A list of unique usernames as strings.
            - "unique_count": The count of unique usernames as an integer.
    """
    user_links = await page.query_selector_all(
        "article > header > h1 > a[href^='/user/']"
    )
    user_urls = [(await link.get_attribute("href")) for link in user_links]
    usernames = {url.split("/")[-1] for url in user_urls if url}
    return {"unique_users": list(usernames), "unique_count": len(usernames)}


async def retrieve_comment_links(page):
    """
    [Function description]
    Retrieves permalink and parent comment links for each comment on the current page.

    This function automates the process of extracting the permalink and parent comment links
    for each comment present on the webpage. It scans through all comment elements and captures
    their permalink and parent link URLs to return them in a structured format.

    [Usage preconditions]
    - This API function retrieves comment links from the page you are currently on.
    - **You must already be on the page containing comments before calling this function.**

    Args:
    page :  A Playwright `Page` instance controlling browser automation.

    Returns:
    list of dict:
        A list of dictionaries where each dictionary contains:
        - "permalink" (str): URL of the comment's permalink.
        - "parent" (str): URL of the parent comment link if present (else None).
    """
    comment_data = []
    articles = await page.query_selector_all("article")
    for article in articles:
        permalink_element = await article.query_selector('a:text("Permalink")')
        permalink_url = (
            await page.evaluate(
                '(element) => element.getAttribute("href")', permalink_element
            )
            if permalink_element
            else None
        )
        parent_element = await article.query_selector('a:text("Parent")')
        parent_url = (
            await page.evaluate(
                '(element) => element.getAttribute("href")', parent_element
            )
            if parent_element
            else None
        )
        comment_data.append({"permalink": permalink_url, "parent": parent_url})
    return comment_data


async def extract_comment_details(page):
    """
    [Function description]
    Extracts comprehensive details for each comment on the page.

    This function automates the extraction of detailed comment information.
    It analyzes the page content to gather information such as:
    - Username
    - Comment text
    - Upvotes
    - Downvotes
    - Permalink
    - Parent data

    [Usage preconditions]
    - You must already be on the comments page before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "username" (str): The username of the comment author.
        - "comment_text" (str): The text content of the comment.
        - "upvotes" (str): The number of upvotes.
        - "downvotes" (str): The number of downvotes.
        - "permalink" (str): The permalink URL of the comment.
        - "parent" (str): The URL of the parent comment if available.
    """
    comments = []
    articles = await page.query_selector_all("article")
    for article in articles:
        username_elem = await article.query_selector("h1 > a")
        username = (
            await (await username_elem.get_property("textContent")).json_value()
            if username_elem
            else "Unknown"
        )
        comment_text_elem = await article.query_selector("p")
        comment_text = (
            await (await comment_text_elem.get_property("textContent")).json_value()
            if comment_text_elem
            else ""
        )
        permalink_elem = await article.query_selector('a:has-text("Permalink")')
        permalink = (
            await (await permalink_elem.get_property("href")).json_value()
            if permalink_elem
            else ""
        )
        parent_elem = await article.query_selector('a:has-text("Parent")')
        parent = (
            await (await parent_elem.get_property("href")).json_value()
            if parent_elem
            else ""
        )
        upvote_button = await article.query_selector('button:has-text("Upvote")')
        upvotes = "N/A"
        downvote_button = await article.query_selector('button:has-text("Downvote")')
        downvotes = "N/A"
        comments.append(
            {
                "username": username.strip(),
                "comment_text": comment_text.strip(),
                "upvotes": upvotes,
                "downvotes": downvotes,
                "permalink": permalink.strip(),
                "parent": parent.strip(),
            }
        )
    return comments


async def list_comment_authors_and_frequencies(page):
    """
    [Function description]
    Gathers a list of comment authors from the current page and analyzes the frequency
    of their comments to determine engagement levels.

    This function locates and extracts author information from the visible comments sections
    on a web page. It aggregates this data to output a frequency analysis of comment authors.

    [Usage preconditions]
    - You must be on a page that contains comments with author information.

    Args:
    page :  A Playwright `Page` instance representing the current page with comments.

    Returns:
    dict
        A dictionary where keys are author names (str) and values are their comment
        frequencies (int), representing the number of comments each author has made.
    """
    authors = {}
    comment_articles = await page.query_selector_all("article")
    for article in comment_articles:
        heading = await article.query_selector("h1")
        if heading:
            author_link = await heading.query_selector("a")
            if author_link:
                author_name = await (
                    await author_link.get_property("innerText")
                ).json_value()
                if author_name:
                    authors[author_name] = authors.get(author_name, 0) + 1
    return authors


async def identify_comment_trends(page):
    """
    [Function description]
    Analyze comment themes or keywords to identify trending topics or common subjects discussed in the comments.

    This function automates the extraction and analysis of comments from the current page.
    It identifies common keywords and themes and returns a summary of the trending topics.

    [Usage preconditions]
    - This API analyzes comments on the page **you are currently at** for trends.
    - **You must already be on a page with a list of comments before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        A dictionary containing trending topics keywords as keys, and their frequency as values.
    """
    comment_elements = await page.query_selector_all("article")
    comments = []
    for element in comment_elements:
        heading_element = await element.query_selector("h1")
        if heading_element:
            text_content = await heading_element.inner_text()
            comments.append(text_content)
    word_count = Counter()
    for comment in comments:
        words = comment.split()
        word_count.update(words)
    trending = {word: count for word, count in word_count.most_common(10)}
    return trending


async def extract_user_profiles_from_submissions(page):
    """
    [Function description]
    Extracts detailed profiles of users who have made recent submissions.

    This function scrapes each user profile from the submissions on the current
    webpage, collecting details including:
    - Profile URL
    - Registration date
    - Notable interactions on the platform

    [Usage preconditions]
    - You must be on the submissions section of the relevant forum or site
      page where user submissions are displayed.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains user profile metadata:
        - "username" (str): The username of the user.
        - "profile_url" (str): The user's profile URL.
        - "registration_date" (str): The date the user registered.
        - "interactions" (list of str): Notable interactions by the user.
    """
    user_profiles = []
    submission_elements = await page.query_selector_all(".submission")
    for submission in submission_elements:
        user_link_elem = await submission.query_selector("a.user-link")
        profile_url = (
            await (await user_link_elem.get_attribute("href"))
            if user_link_elem
            else None
        )
        username_elem = await submission.query_selector(".username")
        username = (
            await (await username_elem.text_content()) if username_elem else "Unknown"
        )
        reg_date_elem = await submission.query_selector(".registration-date")
        registration_date = (
            await (await reg_date_elem.text_content()) if reg_date_elem else "Unknown"
        )
        interactions_elem = await submission.query_selector(".interactions")
        interactions = []
        if interactions_elem:
            interaction_items = await interactions_elem.query_selector_all("li")
            for item in interaction_items:
                interaction_text = await (await item.text_content())
                interactions.append(interaction_text)
        user_profiles.append(
            {
                "username": username,
                "profile_url": profile_url,
                "registration_date": registration_date,
                "interactions": interactions,
            }
        )
    return user_profiles


async def extract_trending_wiki_topics(page):
    """
    [Function description]
    Extracts and analyzes the most frequently updated topics from the Wiki section to determine
    which subjects are gaining traction on the website.

    This function navigates to the Wiki section and scrapes the topics listed there, analyzing
    them based on metadata that indicates the frequency of updates. The exact criteria for
    frequency will depend on the site's internal structure, typically the last updated timestamp
    or an update counter.

    [Usage preconditions]
    - You must be on a page that includes a navigation link to the Wiki section.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "topic" (str): The name of the topic.
        - "update_count" (str): The number of updates or latest update timestamp.
    """
    await (await page.wait_for_selector('a[href="/wiki"]')).click()
    topics_elements = await page.query_selector_all(".topic-class")
    trending_topics = []
    for element in topics_elements:
        title = await (await element.query_selector(".topic-title")).text_content()
        update_info = await (
            await element.query_selector(".update-info")
        ).text_content()
        trending_topics.append({"topic": title, "update_count": update_info})
    return trending_topics


async def compile_most_discussed_comments(page):
    """
    [Function description]
    Compiles a list of the most discussed comments based on engagement metrics such as replies and upvotes.
    This function collects data from the comments section on the current page and organizes it to identify the
    most engaging comments. It includes details like the number of replies, upvotes, and context of discussion.

    [Usage preconditions]
    - You must be on a page that lists comments, specifically designed for displaying post comments.

    Args:
    page : A Playwright `Page` instance representing the current browser page context.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "comment_text" (str): The text of the comment.
        - "replies_count" (int): The number of replies to the comment.
        - "upvotes_count" (int): The number of upvotes the comment has received.
        - "submission_context" (str): Context or title of the associated submission.
    """
    comments_list = []
    comment_elements = await page.query_selector_all("div.comment")
    for comment_element in comment_elements:
        comment_text_element = await comment_element.query_selector("div.comment-body")
        comment_text = await comment_text_element.inner_text()
        replies_count_element = await comment_element.query_selector(
            "span.replies-count"
        )
        replies_count = int(await replies_count_element.inner_text())
        upvotes_count_element = await comment_element.query_selector(
            "span.upvotes-count"
        )
        upvotes_count = int(await upvotes_count_element.inner_text())
        submission_element = await comment_element.query_selector(
            "span.submission-context"
        )
        submission_context = await submission_element.inner_text()
        comments_list.append(
            {
                "comment_text": comment_text,
                "replies_count": replies_count,
                "upvotes_count": upvotes_count,
                "submission_context": submission_context,
            }
        )
    return comments_list


async def list_clickable_links(page):
    """
    [Function description]
    Identifies and lists all clickable links on a webpage.

    This function automates the process of finding all clickable link elements on a page.
    It retrieves the visible text and URL (href attribute) of each link.

    [Usage preconditions]
    - This function can be invoked from any page where you want to list clickable links.
    - The page should be loaded and ready for interaction.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "text" (str): The link text content.
        - "url" (str): The URL to which the link points.
    """
    links = await page.query_selector_all("a")
    clickable_links = []
    for link in links:
        text = await (await link.get_property("textContent")).json_value()
        href = await (await link.get_property("href")).json_value()
        if href.strip():
            clickable_links.append({"text": text.strip(), "url": href.strip()})
    return clickable_links


async def extract_meta_information(page):
    """
    [Function description]
    Extracts meta information from the current web page.

    This function navigates through the DOM of a webpage and retrieves meta elements data,
    such as meta-title, description, and other relevant metadata stored in meta tags.

    [Usage preconditions]
    - Ensure that the page is fully loaded and contains meta information tags.
    - The function should be used on any web page where meta information is required.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        A dictionary containing the meta keys and their respective values extracted from the page.
    """
    meta_info = {}
    title = await (await page.query_selector("head > title")).text_content()
    meta_info["title"] = title.strip() if title else None
    meta_description_element = await page.query_selector(
        'head > meta[name="description"]'
    )
    if meta_description_element:
        meta_description = await meta_description_element.get_attribute("content")
        meta_info["description"] = (
            meta_description.strip() if meta_description else None
        )
    meta_keywords_element = await page.query_selector('head > meta[name="keywords"]')
    if meta_keywords_element:
        meta_keywords = await meta_keywords_element.get_attribute("content")
        meta_info["keywords"] = meta_keywords.strip() if meta_keywords else None
    return meta_info


async def navigate_to_wiki(page):
    """
    [Function description]
    Navigates to the Wiki page from the current page using a click action.

    This function simulates a user clicking on the 'Wiki' link present in the page
    navigation menu. This interaction causes the page to navigate to the Wiki section
    of the website.

    [Usage preconditions]
    - You are already on the landing page containing the main navigation menu.
    - The account should have access to view the Wiki page.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    None
    """
    link = await page.query_selector('a[href="/wiki"]')
    await link.click()


async def extract_comments_with_attributes(page):
    """
    Extract comment details including author, content, timestamp, upvotes, downvotes, and submission links.

    Retrieves comprehensive information for each comment on the current comments page.

    [Usage preconditions]
    - This API extracts comments from a page containing comments.
    - **You must already be on a page that lists comments before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "author" (str): The author's name.
        - "content" (str): The content of the comment.
        - "timestamp" (str): When the comment was posted.
        - "upvotes" (int): Number of upvotes.
        - "downvotes" (int): Number of downvotes.
        - "permalink" (str): Link to the specific comment.
    """
    comments = []
    comment_articles = await page.query_selector_all("article")
    for article in comment_articles:
        heading = await article.query_selector("h1")
        author_elem = await heading.query_selector("a")
        if author_elem:
            author = await author_elem.inner_text()
        else:
            author = "Unknown"
        header_text = await heading.inner_text()
        timestamp = header_text.split("wrote", 1)[1].strip().replace(" ago", "")
        content_elem = await article.query_selector("p")
        content = await content_elem.inner_text() if content_elem else "No content"
        permalink_element = await article.query_selector('a[href*="/comment/"]')
        permalink = (
            await (await permalink_element.get_property("href")).json_value()
            if permalink_element
            else "No link"
        )
        upvote_button = await article.query_selector('button:has-text("Upvote")')
        upvote_count = int(await upvote_button.inner_text()) if upvote_button else 0
        downvote_button = await article.query_selector('button:has-text("Downvote")')
        downvote_count = (
            int(await downvote_button.inner_text()) if downvote_button else 0
        )
        comment_data = {
            "author": author,
            "content": content,
            "timestamp": timestamp,
            "upvotes": upvote_count,
            "downvotes": downvote_count,
            "permalink": permalink,
        }
        comments.append(comment_data)
    return comments


async def get_most_active_commenters(page):
    """
    [Function description]
    Identifies the most active commenters by listing users and calculating the frequency of their comments to rank them in terms of engagement.

    This function automates the extraction of user comment data from the current page
    and counts the frequency of comments made by each user. It will then rank the users
    by their comment frequency.

    [Usage preconditions]
    - This API analyzes comments from the page you are currently at.
    - **You must already be on a page with user comments displayed.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.


    Returns:
    dict
        A dictionary with usernames as keys and their comment frequencies as values.
    """
    import collections

    comment_selector = "article h1.heading > a"
    elements = await page.query_selector_all(comment_selector)
    usernames = []
    for element in elements:
        user_link = await element.get_attribute("href")
        if user_link:
            username_start_index = user_link.rfind("/") + 1
            username = user_link[username_start_index:]
            usernames.append(username)
    frequency = collections.Counter(usernames)
    return dict(frequency)


async def extract_comment_links(page):
    """
    [Function description]
    Extracts all permalink and parent links from comments on the current page.

    This function navigates through the comments on a page and gathers all permalink
    and parent links associated with each comment. It aids in tracking comment threads and interactions.

    [Usage preconditions]
    - The page must contain comments with permalinks and, optionally, parent links.
    - You should be on the page that lists comments, like a forum or discussion thread.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "permalink" (str): The permalink URL of the comment.
        - "parent" (str, optional): The parent URL of the comment, if available.
    """
    comment_links = []
    articles = await page.query_selector_all("article")
    for article in articles:
        permalink = await (
            await article.query_selector("a:has-text('Permalink')")
        ).get_attribute("href")
        try:
            parent = await (
                await article.query_selector("a:has-text('Parent')")
            ).get_attribute("href")
        except:
            parent = None
        comment_links.append({"permalink": permalink, "parent": parent})
    return comment_links


async def extract_user_info_from_submissions(page):
    """
    [Function description]
    Gathers information about users who have recent submissions on the current page.

    This function automates the extraction of user details from the submissions section of a page.
    It collects information about users who have recently submitted content, specifically:

    - Username
    - Profile link

    [Usage preconditions]
    - This API extracts user information from the submissions section **you are currently at**.
    - **You must already be on the page containing the submissions section before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "username" (str): The username of the user.
        - "profile_link" (str): The URL to the user's profile, extracted as a link.
    """
    users_info = []
    user_elements = await page.query_selector_all("div.submission .user")
    for user_element in user_elements:
        username_element = await user_element.query_selector(".username")
        profile_element = await user_element.query_selector("a.profile-link")
        if username_element and profile_element:
            username = await (
                await username_element.get_property("textContent")
            ).json_value()
            profile_link = await (
                await profile_element.get_property("href")
            ).json_value()
            users_info.append(
                {"username": username.strip(), "profile_link": profile_link.strip()}
            )
    return users_info


async def analyze_submission_interactions(page):
    """
    [Function description]
    Computes the interaction metrics of submissions to identify popular ones based on votes and comments.

    This function automates the process of gathering interaction details such as the number of votes and comments for each submission on the current page. These metrics can be used to determine the popularity of each submission.

    [Usage preconditions]
    - This API analyzes interaction metrics of the submissions on the active page.
    - **You should already be on the main Submissions page before using this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title of the submission.
        - "votes" (int): The number of votes the submission has received.
        - "comments" (int): The number of comments on the submission.
    """
    submissions = await page.query_selector_all(".submission")
    result = []
    for submission in submissions:
        title_element = await submission.query_selector(".submission-title")
        votes_element = await submission.query_selector(".submission-votes")
        comments_element = await submission.query_selector(".submission-comments")
        title = await title_element.text_content() if title_element else "N/A"
        votes_text = await votes_element.text_content() if votes_element else "0"
        comments_text = (
            await comments_element.text_content() if comments_element else "0"
        )
        votes = int(votes_text) if votes_text.isdigit() else 0
        comments = int(comments_text) if comments_text.isdigit() else 0
        result.append({"title": title.strip(), "votes": votes, "comments": comments})
    return result


async def collect_recent_wiki_changes(page):
    """
    [Function description]
    Collects timestamps and details of the most recent changes made in the Wiki section, indicating active topics.

    This function automates the extraction of recent change details from the Wiki section.
    It gathers information about each change, including:

    - Topic title
    - Timestamp of change

    [Usage preconditions]
    - You must be already on the Wiki page before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The topic title.
        - "timestamp" (str): The timestamp of the change.
    """
    change_elements = await page.query_selector_all(
        '//div[contains(@class, "recent-change-entry")]'
    )
    recent_changes = []
    for element_handle in change_elements:
        title_handle = await element_handle.query_selector(".change-title")
        timestamp_handle = await element_handle.query_selector(".change-timestamp")
        title = await title_handle.inner_text() if title_handle else "Unknown Title"
        timestamp = (
            await timestamp_handle.inner_text()
            if timestamp_handle
            else "Unknown Timestamp"
        )
        recent_changes.append({"title": title, "timestamp": timestamp})
    return recent_changes


async def search_and_list_submissions(page, keyword):
    """
    [Function description]
    Searches for submissions on the Postmill site using specific keywords and lists the results.

    This function automates the process of searching for submissions based on a keyword in
    the search box of the Postmill website and retrieves the list of submissions that match
    the search criteria.

    [Usage preconditions]
    - You must already be on the submissions page of the Postmill site before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    keyword : A string representing the keyword to search for in submissions.

    Returns:
    list of str
        A list of submission titles that match the search keyword.
    """
    search_box = await page.query_selector('input[aria-label="Search query"]')
    await search_box.fill(keyword)
    await search_box.press("Enter")
    await page.wait_for_load_state("networkidle")
    submissions = await page.query_selector_all("div.submission-title")
    results = [
        (await (await submission.get_property("textContent")).json_value())
        for submission in submissions
    ]
    return results


async def sort_submissions_by_interactions(page):
    """
    [Function description]
    Uses sorting options to list submissions by interactions such as votes and comments.

    This function automates the interaction with sorting options on a page displaying
    submissions. You can set it to sort submissions by various interaction metrics
    like votes and comments if such options are available.

    [Usage preconditions]
    - This API assumes that you are on a page with submission sorting options.
    - The page should have sorting buttons that allow ordering by interactions.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    None.
    """
    button = page.locator('button:has-text("Sort by: Hot")')
    if await button.is_visible():
        await button.click()


async def retrieve_forum_subscriber_submission_counts(page):
    """
    [Function description]
    Retrieves subscriber and submission counts for enabled forums across all pages.

    This function automates the extraction of subscriber and submission counts for forums from a listing page.
    It navigates through all the pages and collects data from each forum listed.

    [Usage preconditions]
    - Ensure that you are already on the initial page of the forum listing.

    Args:
    page : A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the forum.
        - "subscribers" (str): The count of subscribers.
        - "submissions" (str): The count of submissions.
    """
    forums_data = []
    while True:
        forum_articles = await page.query_selector_all("article")
        for forum in forum_articles:
            forum_name_element = await forum.query_selector("h2 a")
            forum_name = await (
                await forum_name_element.get_property("innerText")
            ).json_value()
            subscribers_element = await forum.query_selector(".subscribers")
            submissions_element = await forum.query_selector(".submissions")
            subscribers = ""
            submissions = ""
            if subscribers_element:
                subscribers = await (
                    await subscribers_element.get_property("innerText")
                ).json_value()
            if submissions_element:
                submissions = await (
                    await submissions_element.get_property("innerText")
                ).json_value()
            forums_data.append(
                {
                    "name": forum_name.strip(),
                    "subscribers": subscribers.strip(),
                    "submissions": submissions.strip(),
                }
            )
        next_button = await page.query_selector("text=Next")
        if (
            next_button
            and not await (await next_button.get_property("disabled")).json_value()
        ):
            await next_button.click()
            await page.wait_for_load_state("networkidle")
        else:
            break
    return forums_data


async def extract_clickable_links(page):
    """
    Extracts all clickable links and their URLs on the homepage.

    [Function description]
    This function automates the extraction of all clickable links available
    on a webpage, specifically from the homepage, for quick navigation access.
    It identifies link elements, retrieves their text content and URLs,
    and compiles this information for further use.

    [Usage preconditions]
    - You must already be on the homepage of the website before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "text" (str): The text content of the link.
        - "url" (str): The URL to which the link points.
    """
    elements = await page.query_selector_all("a")
    links = []
    for element in elements:
        text = await element.text_content()
        url = await element.get_attribute("href")
        links.append({"text": text, "url": url})
    return links


async def list_user_accessible_paths(page):
    """
    [Function description]
    Lists all user login and registration paths accessible from the homepage to test their accessibility.

    This function navigates through the homepage and locates the paths for user login and registration.
    It ensures these paths are easily accessible for new and returning users by identifying:

    - Login path
    - Registration path

    [Usage preconditions]
    - This API identifies accessible paths for user login and registration from the homepage.
    - **Ensure you are on the homepage before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.


    Returns:
    dict
        A dictionary containing the paths and their corresponding accessibility status.
    """
    results = {}
    login_button = await page.query_selector("text=Log in")
    if login_button:
        await login_button.click()
        results["login_path"] = "/login"
    else:
        results["login_path"] = "Not accessible"
    await page.goto("/homepage")
    signup_button = await page.query_selector("text=Sign up")
    if signup_button:
        await signup_button.click()
        results["registration_path"] = "/registration"
    else:
        results["registration_path"] = "Not accessible"
    return results


async def extract_sort_and_filter_options(page):
    """
    [Function description]
    Extracts sorting and filtering options available for submissions and comments to assist users in customizing their content viewing preferences effectively.

    [Usage preconditions]
    - The page is expected to be fully loaded with sorting and filtering elements visible.
    - The page structure adheres to the provided AST, where sorting and filtering buttons exist directly accessible.

    Args:
    page : A Playwright `Page` instance representing the page to be operated on.

    Returns:
    dict
        A dictionary containing lists for sorting and filtering options as keys:
        - "sort_options" (list): List of available sorting options.
        - "filter_options" (list): List of available filtering options.
    """
    filter_button = await page.query_selector('main button[aria-label^="Filter on:"]')
    if filter_button:
        await filter_button.click()
    else:
        return {"sort_options": [], "filter_options": []}
    filter_options_elements = await page.query_selector_all(
        "#filter-options-selector li"
    )
    filter_options = [(await option.inner_text()) for option in filter_options_elements]
    sort_button = await page.query_selector('main button[aria-label^="Sort by:"]')
    if sort_button:
        await sort_button.click()
    else:
        return {"sort_options": [], "filter_options": []}
    sort_options_elements = await page.query_selector_all("#sort-options-selector li")
    sort_options = [(await option.inner_text()) for option in sort_options_elements]
    return {"sort_options": sort_options, "filter_options": filter_options}


async def navigate_to_forums_submissions(page):
    """
    Navigate directly to the Submissions section within the forums.

    This function automates the navigation process to move from the homepage to the submissions section in the forum area.

    Usage preconditions:
    - Ensure the page is on the homepage before calling this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Usage log:
    - Successfully navigated to the Submissions section of the forums using the identified navigation flow.
    """
    await page.goto("/")
    await page.get_by_role("link", name="Forums").click()
    await page.get_by_role("button", name="Sort by: Submissions").click()


async def extract_submissions_details(page):
    """
    [Function description]
    Extracts all submissions and their details from the Postmill website.

    This function automates the gathering of submission details from the page you're currently
    visiting on the Postmill platform. It retrieves comprehensive information regarding each
    submission, such as:

    - Submission title
    - Submission author
    - Submission URL
    - Submission timestamp

    [Usage preconditions]
    - This API retrieves submission information for the current page.
    - Ensure you are on a page that displays submissions before using this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "title" (str): The title of the submission.
        - "author" (str): The name of the author of the submission.
        - "url" (str): The URL link to the submission.
        - "timestamp" (str): The timestamp of when the submission was created.
    """
    submissions = []
    submission_elements = await page.query_selector_all(".submission-item")
    for submission_element in submission_elements:
        title = await (
            await submission_element.query_selector(".submission-title")
        ).inner_text()
        author = await (
            await submission_element.query_selector(".submission-author")
        ).inner_text()
        url = await (
            await submission_element.query_selector(".submission-link")
        ).get_attribute("href")
        timestamp = await (
            await submission_element.query_selector(".submission-timestamp")
        ).inner_text()
        submissions.append(
            {"title": title, "author": author, "url": url, "timestamp": timestamp}
        )
    return submissions


async def navigate_to_active_forums(page):
    """
    [Function description]
    Navigates to the most active forums section on a website.

    This function automates the process of locating the forums section of a site
    and determines the most active forums based on indicators on the page.

    [Usage preconditions]
    - You must be on the website's homepage to execute this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of str
        A list of URLs of the most active forums as determined by the site indicators.
    """
    await page.click('a:has-text("Forums")')
    active_forums = []
    forum_elements = await page.query_selector_all("selector-for-forum-items")
    for forum in forum_elements:
        activity_indicator = await forum.inner_text()
        if "Active" in activity_indicator or "Popular" in activity_indicator:
            url = await (await forum.query_selector("a")).get_attribute("href")
            active_forums.append(url)
    return active_forums


async def retrieve_comment_trends(page):
    """
    [Function description]
    Retrieve and analyze comment trends from the current page of the Postmill website.

    This function automates the extraction of comment details, analyzing trends based
    on the frequency of comments and their metadata such as author names, timestamps,
    and votes.

    [Usage preconditions]
    - This API retrieves comment information from the Postmill website **you are currently at**.
    - **You must already be on a Postmill comments page before calling this function.**

    Args:
    page : A Playwright `Page` instance that is controlling browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "text" (str): The comment text.
        - "author" (str): The name of the comment author.
        - "time" (str): The timestamp of when the comment was posted.
        - "votes" (int): The number of votes the comment has received.
        - "trend" (str): An analysis of the comment trend based on predefined criteria.
    """
    comment_elements = await page.query_selector_all(".comment")
    comments_data = []
    for element in comment_elements:
        text_element = await element.query_selector(".comment-text")
        author_element = await element.query_selector(".comment-author")
        time_element = await element.query_selector(".comment-time")
        votes_element = await element.query_selector(".comment-votes")
        if (
            not text_element
            or not author_element
            or not time_element
            or not votes_element
        ):
            continue
        text = await text_element.inner_text()
        author = await author_element.inner_text()
        time = await time_element.inner_text()
        votes = await votes_element.inner_text()
        if int(votes) > 10:
            trend = "Popular"
        else:
            trend = "Not Popular"
        comments_data.append(
            {
                "text": text,
                "author": author,
                "time": time,
                "votes": int(votes),
                "trend": trend,
            }
        )
    return comments_data


async def extract_links_from_error_page(page):
    """
    [Function description]
    Extract operational links from the 'Page not found' error page to assist users in navigating to other sections of the website.

    This function automates the extraction of accessible links on a 'Page not found' error page. It identifies operational links such as 'Home', 'Forums', 'Wiki', 'Log in', and 'Sign up' to help users access different sections of the website.

    [Usage preconditions]
    - Ensure you are on the 'Page not found' error page of the website before using this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary represents an accessible link with:
        - 'text' (str): The displayed text of the link.
        - 'url' (str): The URL the link points to.
    """
    links = []
    elements = await page.query_selector_all("a")
    for element in elements:
        text = await element.inner_text()
        url = await element.get_attribute("href")
        if text and url:
            links.append({"text": text.strip(), "url": url.strip()})
    return links


async def collect_error_page_metadata(page):
    """
    [Function description]
    Collects metadata from an error page including navigation links, search feature,
    and complementary information.

    This function extracts various metadata elements from a generic error page, which
    typically contain links to other sections of a site, a search box, and some complementary
    links. This metadata can be useful for debugging or understanding site navigation.

    [Usage preconditions]
    - **The current page should be an error page containing standard navigation** like the example provided.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries containing:
        - "text" (str): The display text of the element.
        - "href" (str): The URL link associated with the element, if any.
    """
    error_page_metadata = []
    links_selector = "a"
    navigation_links = await page.query_selector_all(links_selector)
    for link in navigation_links:
        text = await (await link.get_property("innerText")).json_value()
        href = await (await link.get_property("href")).json_value()
        error_page_metadata.append({"text": text.strip(), "href": href})
    search_selector = 'input[type="text"]'
    search_element = await page.query_selector(search_selector)
    if search_element:
        placeholder = await (
            await search_element.get_property("placeholder")
        ).json_value()
        error_page_metadata.append({"text": "Search query", "placeholder": placeholder})
    return error_page_metadata


async def identify_error_navigation_paths(page):
    """
    [Function description]
    Identify navigational paths and user actions leading to a 'Page not found' error.

    This function analyzes the error page to determine possible navigational paths or user
    actions that might lead to a 'Page not found' error, aiding in debugging or UX improvements.
    It collects links and search elements present on the error page.

    [Usage preconditions]
    - **You must already be on the 'Page not found' error page before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        A dictionary containing navigation paths including:
        - "links" (list): A list of navigable URLs present on the error page.
        - "search" (str, optional): The selector for the search box if available.
    """
    link_elements = await page.query_selector_all("a")
    link_paths = []
    for element in link_elements:
        href = await element.get_attribute("href")
        if href:
            link_paths.append(href)
    search_selector = 'input[name="search"]'
    search_element = await page.query_selector(search_selector)
    search_path = search_selector if search_element else None
    return {"links": link_paths, "search": search_path}


async def extract_forum_details(page):
    """
    [Function description]
    Extracts all forum names, URLs, and submission counts across all pages.
    Identifies the most and least submitted forums.

    This function automates the extraction of forum details such as name, URL,
    and submission count from each forum listed on the current page.
    It navigates through multiple pages of forums and combines results.

    [Usage preconditions]
    - **You must already be on a forum listing page before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        Contains two keys:
        - "forums": a list of dictionaries where each dictionary includes:
          - "name" (str): The name of the forum.
          - "url" (str): The URL to visit the forum.
          - "submissions" (int): The number of submissions to the forum.
        - "most_submissions" (dict): Details of the forum with the most submissions.
        - "least_submissions" (dict): Details of the forum with the least submissions.
    """
    forums = []
    next_page_selector = 'a:text("Next")'

    async def extract_current_page_details():
        articles = await page.query_selector_all("article")
        for article in articles:
            h2_element = await article.query_selector("h2")
            if not h2_element:
                continue
            heading = await h2_element.inner_text()
            a_element = await article.query_selector("h2 a")
            if not a_element:
                continue
            link = await a_element.get_attribute("href")
            name = heading.split(" — ")[0]
            url = f"/f/{name}" if link else ""
            submission_count = await article.query_selector(".submission-count")
            count = int(await submission_count.inner_text()) if submission_count else 0
            forums.append({"name": name, "url": url, "submissions": count})

    await extract_current_page_details()
    while await page.query_selector(next_page_selector):
        await page.click(next_page_selector)
        await extract_current_page_details()
    most_submissions = max(forums, key=lambda x: x["submissions"]) if forums else {}
    least_submissions = min(forums, key=lambda x: x["submissions"]) if forums else {}
    return {
        "forums": forums,
        "most_submissions": most_submissions,
        "least_submissions": least_submissions,
    }


async def retrieve_forums_sorted_by_submissions(page):
    """
    [Function description]
    Retrieves all forums sorted by the number of submissions, gathering metadata such as forum names, URLs, submissions, and subscribers.

    [Usage preconditions]
    - The function assumes that you are already on the forums listing page.
    - The forums page should be loaded with sortable options by submissions.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries, where each dictionary contains the following keys:
        - "name" (str): The name of the forum.
        - "url" (str): The URL of the forum.
        - "submissions" (int): The number of submissions in the forum.
        - "subscribers" (int): The number of subscribers to the forum.
    """
    sort_button = await page.query_selector("text=Sort by: Submissions")
    if sort_button:
        await sort_button.click()
    forums = []
    articles = await page.query_selector_all("article")
    for article in articles:
        heading = await article.query_selector("h2")
        link = await heading.query_selector("a")
        name = await link.text_content() if link else ""
        url = await link.get_attribute("href") if link else ""
        submissions = await article.query_selector("[data-submissions]")
        subscribers = await article.query_selector("[data-subscribers]")
        submissions_count = await submissions.text_content() if submissions else "0"
        subscribers_count = await subscribers.text_content() if subscribers else "0"
        forums.append(
            {
                "name": name,
                "url": url,
                "submissions": int(submissions_count.replace(",", "")),
                "subscribers": int(subscribers_count.replace(",", "")),
            }
        )
    return forums


async def extract_forums_with_no_subscribers(page):
    """
    [Function description]
    Extracts a list of forums with no subscribers, including their names and submission counts.

    This function navigates the forums list page, identifies forums that do not have any subscribers,
    and extracts their names and submission counts. The information will be returned in a structured format.

    [Usage preconditions]
    - This API retrieves forum information for the page **you are currently at** that lists forums.
    - **You must already be on a page listing multiple forums before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the forum.
        - "submissions" (int): The count of submissions in the forum.
    """
    forums_list = []
    articles = await page.query_selector_all("article")
    for article in articles:
        name_element = await article.query_selector("h2 > a")
        if name_element:
            forum_name = await name_element.inner_text()
        subscribers_element = await article.query_selector(".subscriber-count")
        if not subscribers_element:
            submissions_element = await article.query_selector(".submission-count")
            forum_submissions = (
                await submissions_element.inner_text() if submissions_element else "0"
            )
            forums_list.append(
                {"name": forum_name, "submissions": int(forum_submissions)}
            )
    return forums_list


async def extract_forum_names_and_submission_counts(page):
    """
    Extracts forum names and submission counts from the current page.

    This function automates the extraction of forum details from the current
    page, gathering information about each forum, including:

    - Forum name
    - Submission count (if available)

    [Usage preconditions]
    - This API retrieves forum information from the page **you are currently at**.
    - **Ensure that you are on a forum listing page before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "name" (str): The name of the forum.
        - "submissions" (int or None): The count of submissions if available.
    """
    forum_elements = await page.query_selector_all("article")
    forums = []
    for element in forum_elements:
        heading_elem = await element.query_selector("h2")
        forum_name = await (await heading_elem.query_selector("a")).inner_text()
        submission_elem = await element.query_selector("span.submissions-count")
        if submission_elem:
            submission_count_text = await submission_elem.inner_text()
            submission_count = (
                int(submission_count_text) if submission_count_text.isdigit() else None
            )
        else:
            submission_count = None
        forums.append({"name": forum_name, "submissions": submission_count})
    return forums


async def sort_forums_by_submissions(page):
    """
    [Function description]
    Sorts forums by the number of submissions on the current page.

    The function automates the action of sorting forums based on the number of submissions
    by clicking the respective sorting button available on the forums page.

    [Usage preconditions]
    - This API expects that you are on a page where a forum listing is displayed with an option to "Sort by: Submissions".

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    None
        This function does not return any value. It performs an in-place operation to sort the forums.
    """
    sort_button = page.locator("button:has-text('Sort by: Submissions')").first()
    await sort_button.click()


async def gather_forums_with_no_subscribers(page):
    """
    [Function description]
    Gather forums that currently have no subscribers from the list of forums.

    This function automates the process of identifying forums on the current page
    that have no subscribers or a specified indicator representing no subscriptions.
    It reads through each forum section and collects those without subscribers.

    [Usage preconditions]
    - You must be on the forums listing page for subscriber information for the forums.

    Args:
    page : A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the forum.
        - "link" (str): The url for accessing the forum.
    """
    no_subscriber_forums = []
    articles = await page.query_selector_all("article")
    for article in articles:
        heading = await article.query_selector("h2")
        forum_name = await heading.inner_text()
        forum_link = await (await heading.query_selector("a")).get_attribute("href")
        subscriber_info = await article.query_selector(".subscriber-info")
        subscriber_count = None
        if subscriber_info:
            subscriber_count = await subscriber_info.inner_text()
        if not subscriber_count:
            no_subscriber_forums.append({"name": forum_name, "link": forum_link})
    return no_subscriber_forums


async def extract_navigation_links_from_error_page(page):
    """
    [Function description]
    Extracts operational navigation links from the error page.

    This function automates the extraction of textual navigation links and their URLs
    from the error page, providing quick access to operational areas of the site.
    It retrieves links present in the main content, sidebar, and complements.

    [Usage preconditions]
    - You must already be on a specific error page where navigation links are defined.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "text" (str): The text within the navigation link.
        - "url" (str): The URL the navigation link points to.
    """
    navigation_links = []
    elements = await page.query_selector_all("a")
    for element in elements:
        text = await element.inner_text()
        href = await element.get_attribute("href")
        if text and href:
            navigation_links.append({"text": text.strip(), "url": href.strip()})
    return navigation_links


async def perform_search_from_error_page(page):
    """
    [Function description]
    Automates the process of executing a search query from the error page.

    This function interacts with the search functionality on a web page, inputs a predefined search query,
    and submits it, simulating a user's search action on the page.

    [Usage preconditions]
    - Ensure that the page contains a search functionality accessible from an error page with a labeled search box "Search query".

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    None
        The function does not return any value. It only performs a search operation by automating inputs into the search box.
    """
    search_box = await page.query_selector('[placeholder="Search query"]')
    if search_box:
        await search_box.fill("Sample search query")
        await search_box.press("Enter")


async def extract_wiki_links(page):
    """
    [Function description]
    Extract wiki-related links from the sidebar of an error page.

    This function automates the extraction of links related to wiki functionalities,
    such as the general wiki access, all wiki pages, and recent changes, which are located
    in the sidebar of the error page.

    [Usage preconditions]
    - This API extracts information from an error page with a sidebar containing relevant wiki links.
    - **You must already be on the error page before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "text" (str): The text description of the link.
        - "url" (str): The URL of the link.
    """
    sidebar_links = []
    links = await page.query_selector_all("aside a")
    for link in links:
        href = await link.get_attribute("href")
        text = await link.inner_text()
        if href in ["/wiki", "/wiki/_all", "/wiki/_recent"]:
            sidebar_links.append({"text": text, "url": href})
    return sidebar_links


async def perform_search_on_error_page(page):
    """
    [Function description]
    Performs a search operation using the search query box on the current error page to identify and navigate to potential pages.

    This function automates the search action on an error page with a specific search box.
    It enters a given query into the box and triggers the search functionality to access relevant pages.

    [Usage preconditions]
    - The page should be the error page containing a search query box before this function is invoked.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    None
    """
    search_box_element = await page.query_selector('input[aria-label="Search query"]')
    if search_box_element:
        await search_box_element.fill("example query")
        await search_box_element.press("Enter")


async def retrieve_error_page_navigation_links(page):
    """
    Retrieve all navigation links from an error page.

    This function collects all available navigation links on an error page,
    including links to sections like Home, Forums, Wiki, Log In, and Sign Up.

    [Usage preconditions]
    - This API must be called on an error page where navigation links are present.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "text" (str): The visible text of the link.
        - "url" (str): The URL to which the link navigates.
    """
    links = await page.query_selector_all("a")
    link_details = []
    for link in links:
        text = await (await link.get_property("textContent")).json_value()
        url = await (await link.get_property("href")).json_value()
        link_details.append({"text": text.strip(), "url": url})
    return link_details


async def gather_error_page_metadata(page):
    """
    [Function description]
    Extracts structured HTML metadata from a general error page to identify potential reasons for the error or insights into the server response.

    This function automates the extraction of metadata from error pages, focusing on gathering structured data, such as available links, search boxes, and main content indicators.

    [Usage preconditions]
    - This function assumes that the user is already on an error page from which metadata needs to be extracted.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        A dictionary containing structured metadata, including lists of links and search box placeholders from the error page.
    """
    link_elements = await page.query_selector_all("a")
    links = []
    for element in link_elements:
        href = await element.get_attribute("href")
        text = await element.inner_text()
        links.append({"text": text, "url": href})
    search_placeholder = None
    search_box = await page.query_selector('input[type="search"]')
    if search_box:
        search_placeholder = await search_box.get_attribute("placeholder")
    return {"links": links, "search_placeholder": search_placeholder}


async def extract_forums_info(page):
    """
    Extracts forum information from the current page.

    This function automates the extraction of all forums with their respective
    number of subscribers and submissions from the current page.

    [Usage preconditions]
    - You must already be on a page that lists forums, such as a forum directory or catalog page.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries, where each dictionary contains:
        - "title" (str): The title of the forum.
        - "subscribers" (int): The number of subscribers to the forum.
        - "submissions" (int): The number of submissions made in the forum.
    """
    forum_data = []
    forum_elements = await page.query_selector_all("article")
    for forum_element in forum_elements:
        heading_elem = await forum_element.query_selector("h2")
        forum_title = (
            await heading_elem.inner_text() if heading_elem else "Unknown Title"
        )
        subscribers_elem = await forum_element.query_selector(".subscribers")
        submissions_elem = await forum_element.query_selector(".submissions")
        subscribers = (
            int(await subscribers_elem.inner_text()) if subscribers_elem else 0
        )
        submissions = (
            int(await submissions_elem.inner_text()) if submissions_elem else 0
        )
        forum_data.append(
            {
                "title": forum_title,
                "subscribers": subscribers,
                "submissions": submissions,
            }
        )
    return forum_data


async def identify_forums_without_subscribers(page):
    """
    [Function description]
    Identifies forums without any subscribers from the current page listing.

    This function automates the process of selecting forums from the webpage that
    do not have subscriber information listed. It checks each forum article to
    determine the presence of subscriber data and returns a list of forums
    lacking subscriber details.

    [Usage preconditions]
    - Ensure you are on a page that lists forums with subscriber info.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of str
        A list of forum names that do not have any subscribers indicated.
    """
    forums_without_subscribers = []
    forums = await page.query_selector_all("main >> article")
    for forum in forums:
        heading_handle = await forum.query_selector("h2")
        heading_text = await heading_handle.inner_text()
        subscriber_info_handle = await forum.query_selector(".subscriber-info")
        if not subscriber_info_handle:
            forums_without_subscribers.append(heading_text)
    return forums_without_subscribers


async def extract_forums_sorted_by_submissions(page):
    """
    [Function description]
    Extracts a list of forums sorted by the number of submissions from the current page and subsequent pages.

    The function automates the process of gathering forum information from the page you are currently at.
    It retrieves forums sorted by the number of submissions, ensures the data is gathered from all available pages,
    and compiles a comprehensive list of forum names along with their links.

    [Usage preconditions]
    - You must already be on a page listing forums possibly unsorted by submissions.

    Args:
    page : A Playwright `Page` instance to control browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the:
        - "name" (str): The name of the forum.
        - "url" (str): The URL of the forum.
    """
    forums = []
    sort_button = await page.query_selector('button:has-text("Sort by: Submissions")')
    if sort_button:
        await sort_button.click()
    while True:
        articles = await page.query_selector_all("article")
        for article in articles:
            heading = await article.query_selector("h2")
            forum_name = await heading.inner_text()
            forum_link = await heading.query_selector("a")
            forum_url = await forum_link.get_attribute("href")
            forums.append({"name": forum_name, "url": forum_url})
        next_link = await page.query_selector('a:has-text("Next")')
        if next_link:
            next_url = await next_link.get_attribute("href")
            await page.goto(next_url)
        else:
            break
    return forums


async def navigate_to_forums_section(page):
    """
    Navigate to the Forums section from the homepage.

    This function uses the Playwright API to navigate the Postmill homepage, find
    the 'Forums' link, and click it to proceed to the forums section.

    Args:
    page (Page): A Playwright `Page` instance that controls browser automation.

    Usage log:
    - Successfully navigated to the forums section by clicking the 'Forums' link from the homepage.

    Note:
    - Ensure you are on the homepage before calling this function.
    """
    await page.goto("/")
    await page.get_by_role("link", name="Forums").click()


async def extract_forum_urls_and_pages(page):
    """
    [Function description]
    Extracts all forum URLs and their corresponding page numbers to help streamline
    navigation to specific content hubs efficiently.

    This function automates the extraction of forum information including the URLs
    and their respective page numbers from the current page of a forum listing. This
    helps users navigate to specific forums based on their name more efficiently.

    [Usage preconditions]
    - The API expects you to be on the forum listing page and it extracts forum links present.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title of the forum.
        - "url" (str): The URL of the forum.
        - "page_number" (int): The page number on which the forum is found.
    """
    forum_info = []
    current_page_number = 1
    page_links = await page.query_selector_all("a[href^='/forums/by_submissions']")
    for page_link in page_links:
        page_number_text = await (
            await page_link.get_property("textContent")
        ).json_value()
        if "Page" in page_number_text:
            current_page_number = int(page_number_text.split()[1])
            break
    forum_articles = await page.query_selector_all("article > h2 > a")
    for article in forum_articles:
        title = await (await article.get_property("textContent")).json_value()
        url = await (await article.get_property("href")).json_value()
        forum_info.append(
            {"title": title.strip(), "url": url, "page_number": current_page_number}
        )
    return forum_info


async def list_active_forums_without_subscribers(page):
    """
    Identify and list forums without subscribers that have the highest submission count.

    This function automates the extraction of forums that do not have any subscribers
    but have significant submission activity by using pre-extracted forum details
    directly from the current forums listing page.

    [Usage preconditions]
    - This API should be used when on the main 'Forums' page listing.
    - You must already be on a page listing all forums before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries sorted by submission count, containing:
        - "forum_name" (str): The name of the forum.
        - "submission_count" (int): The total number of submissions in the forum.
        - "link" (str): The direct link to the forum.
    """
    forum_articles = await page.query_selector_all("article")
    active_forums = []
    for article in forum_articles:
        forum_link_tag = await article.query_selector("a")
        if forum_link_tag:
            forum_link = await forum_link_tag.get_attribute("href")
            forum_name = await forum_link_tag.inner_text()
            submission_count_elem = await article.query_selector(
                '[data-test-id="submission-count"]'
            )
            subscriber_count_elem = await article.query_selector(
                '[data-test-id="subscriber-count"]'
            )
            if subscriber_count_elem and submission_count_elem:
                subscriber_count = int(await subscriber_count_elem.inner_text())
                submission_count = int(await submission_count_elem.inner_text())
                if subscriber_count == 0:
                    active_forums.append(
                        {
                            "forum_name": forum_name.strip(),
                            "submission_count": submission_count,
                            "link": forum_link,
                        }
                    )
    sorted_forums = sorted(
        active_forums, key=lambda x: x["submission_count"], reverse=True
    )
    return sorted_forums


async def summarize_forum_activity(page):
    """
    [Function description]
    Summarizes forum name occurrences and submission counts across multiple pages,
    highlighting trends or anomalies in forum activity.

    [Usage preconditions]
    - The function starts from a forums listing page that includes pagination.
    - The user should remain on forums pages while this function navigates through them automatically.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        A dictionary where each key is a forum name and each value is its occurrence count across the pages.
    """
    forum_counts = {}
    next_page_selector = 'a:text("Next")'
    while True:
        forum_elements = await page.query_selector_all("article h2")
        for forum_element in forum_elements:
            forum_name = await (
                await forum_element.get_property("innerText")
            ).json_value()
            if forum_name in forum_counts:
                forum_counts[forum_name] += 1
            else:
                forum_counts[forum_name] = 1
        next_page = await page.query_selector(next_page_selector)
        if next_page:
            await next_page.click()
            await page.wait_for_load_state("networkidle")
        else:
            break
    return forum_counts


async def extract_forum_info(page):
    """
    Extracts forum names, URLs, and activity levels from the 'Forums' section.

    This function automates the retrieval of data from a 'Forums' section on a webpage.
    It gathers information about each forum, including:

    - Forum name
    - Forum URL
    - Activity level

    [Usage preconditions]
    - This script assumes you are already on a page with a 'Forums' section.

    Args:
    page : A Playwright `Page` instance for controlling browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "name" (str): The name of the forum.
        - "url" (str): The URL to access the forum.
        - "activity" (str): Description of the activity level in the forum.
    """
    forums = []
    forum_elements = await page.query_selector_all('a[href^="/forum"]')
    for forum_element in forum_elements:
        name_element = await forum_element.query_selector(".forum-name")
        name = await name_element.inner_text() if name_element else "Unknown"
        url = await forum_element.get_attribute("href")
        activity_element = await forum_element.query_selector(".forum-activity")
        activity = (
            await activity_element.inner_text() if activity_element else "Not Available"
        )
        forums.append(
            {"name": name.strip(), "url": url.strip(), "activity": activity.strip()}
        )
    return forums


async def analyze_user_engagement(page):
    """
    [Function description]
    Extracts data about unique commenters and their activity levels from the comments section
    of a discussion page to help assess community engagement levels.

    This function scans the comments section of a page for unique commenters and calculates
    how active each commenter is by counting their number of comments.

    [Usage preconditions]
    - This function assumes you are currently on a page with a comments section.
    - The page should be fully loaded with content visible for extraction.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        A dictionary where each key is a commenter's name and the value is their number of comments.
    """
    comment_elements = await page.query_selector_all(".comment-author")
    comment_data = {}
    for element in comment_elements:
        commenter_name = await element.text_content()
        if commenter_name not in comment_data:
            comment_data[commenter_name] = 0
        comment_data[commenter_name] += 1
    return comment_data


async def get_forum_submission_counts(page):
    """
    [Function description]
    Retrieve submission counts for all forums on the current page to identify active discussions or popular forums.

    This function automates the extraction of submission details for forums listed on the current page.

    [Usage preconditions]
    - You must already be on a page listing multiple forums where submission details are accessible.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "name" (str): The name of the forum.
    """
    forums_data = []
    forum_elements = await page.query_selector_all("article > h2")
    for forum in forum_elements:
        name = await (await forum.get_property("innerText")).json_value()
        forums_data.append({"name": name.strip()})
    return forums_data


async def sort_forums_by_submission_count(page):
    """
    Sorts forums on the page by their submission count to highlight the most active forums.

    This function automates the interaction with the sorting button on the forums page,
    which sorts the list of forums by the number of submissions. This highlights the most
    active forums currently present on the page.

    [Usage preconditions]
    - This function assumes the page is already displaying a list of forums.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    None
    """
    await page.locator("button:has-text('Sort by: Submissions')").click()


async def search_and_locate_alternative_pages(page):
    """
    [Function description]
    Navigates and searches for alternative pages available through common links and search functionalities on the current webpage.

    This function automates the process of exploring a webpage by accessing general links and utilizing the search box,
    effectively discovering available pages under common categories such as Home, Forums, Wiki etc.

    [Usage preconditions]
    - You must already be on a webpage containing common navigation links and a search box as described in the AST.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        List containing information of alternative pages including their titles and URLs.
    """
    alternative_pages = []
    if await page.query_selector('a:has-text("Home")'):
        await page.click('a:has-text("Home")')
        alternative_pages.append({"title": "Home", "url": page.url})
    if await page.query_selector('a:has-text("Forums")'):
        await page.click('a:has-text("Forums")')
        alternative_pages.append({"title": "Forums", "url": page.url})
    if await page.query_selector('a:has-text("Wiki")'):
        await page.click('a:has-text("Wiki")')
        alternative_pages.append({"title": "Wiki", "url": page.url})
    search_box = await page.query_selector('[placeholder="Search query"]')
    if search_box:
        await search_box.fill("alternative pages")
        await page.keyboard.press("Enter")
        alternative_pages.append({"title": "Search Results", "url": page.url})
    return alternative_pages


async def extract_operational_links(page):
    """
    [Function description]
    Extracts all operational links from the current web page.

    This function automates the process of identifying and extracting all operational links
    from the current page. The links include navigational and complementary links that are
    visible in the DOM.

    [Usage preconditions]
    - This API must be called while you are currently viewing the web page from which links are to be extracted.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "text" (str): The displayed text of the link.
        - "url" (str): The URL that the link points to.
    """
    links = []
    elements = await page.query_selector_all("a")
    for element in elements:
        text = await element.inner_text()
        url = await element.get_attribute("href")
        if url:
            links.append({"text": text, "url": url})
    return links


async def identify_most_discussed_topics(page):
    """
    [Function description]
    Extracts the titles of discussion threads and counts the number of comments associated with each title
    to rank which topics are currently attracting the most engagement on the webpage.

    [Usage preconditions]
    - This function assumes you are on a webpage containing discussion threads.
    - The structure of the page should follow the assumed format, where each topic is enclosed in an article element.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title of the discussion thread.
        - "count" (int): The number of comments or engagements associated with the thread.
    """
    topic_counts = {}
    articles = await page.query_selector_all("article")
    for article in articles:
        link_element = await article.query_selector("link:not([expanded])")
        if link_element:
            title = await (await link_element.get_property("innerText")).json_value()
            if title in topic_counts:
                topic_counts[title] += 1
            else:
                topic_counts[title] = 1
    sorted_topic_counts = sorted(
        topic_counts.items(), key=lambda item: item[1], reverse=True
    )
    result = [{"title": title, "count": count} for title, count in sorted_topic_counts]
    return result


async def list_users_comment_frequencies(page):
    """
    [Function description]
    List all users who have commented along with the frequency of their comments.

    This function scans the current page for user comments, extracting usernames and
    counting the frequency of comments made by each user. This helps identify the
    most active users on the page.

    [Usage preconditions]
    - You must already be on a page containing the user comments before calling this function.

    Args:
    page : Playwright `Page` instance for browser automation.

    Returns:
    dict
        A dictionary where the keys are usernames (str) and the values are the frequencies of comments (int) they made.
    """
    user_frequencies = {}
    articles = await page.query_selector_all("article")
    for article in articles:
        heading = await article.query_selector("h1")
        if heading:
            user_link = await heading.query_selector("a")
            if user_link:
                username = await user_link.inner_text()
                if username in user_frequencies:
                    user_frequencies[username] += 1
                else:
                    user_frequencies[username] = 1
    return user_frequencies


async def analyze_vote_patterns(page):
    """
    [Function description]
    Analyzes comment voting patterns to determine trends based on upvote and downvote metrics.

    This function traverses through the comments section of a page, extracting voting metrics such as upvotes and downvotes for each comment.
    It identifies the most upvoted or downvoted comments, providing insights into community approval or disapproval metrics.

    [Usage preconditions]
    - Ensure the page navigated is a comments section containing voting button information.
    - **You must already be on a page that contains comments with voting information before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.


    Returns:
    dict
        A dictionary containing upvote and downvote counts for each comment, with comment identifiers as keys.
        - "comment_id" (str): Unique identifier for the comment.
        - "upvotes" (int): The number of upvotes the comment has received.
        - "downvotes" (int): The number of downvotes the comment has received.
    """
    comments_data = {}
    articles = await page.query_selector_all("article")
    for article in articles:
        heading = await article.query_selector("heading")
        if heading is None:
            continue
        heading_content = await heading.text_content()
        comment_id = heading_content.split(" ")[1]
        upvote_button = await article.query_selector('button:has-text("Upvote")')
        downvote_button = await article.query_selector('button:has-text("Downvote")')
        upvotes = int(await upvote_button.get_attribute("data-upvotes") or 0)
        downvotes = int(await downvote_button.get_attribute("data-downvotes") or 0)
        comments_data[comment_id] = {"upvotes": upvotes, "downvotes": downvotes}
    return comments_data


async def navigate_to_featured_submissions(page):
    """
    Navigates to the Featured Submissions section on the homepage by clicking the 'Filter on: Featured' button.

    This function automates the navigation from the homepage to the Featured Submissions section.
    It ensures the submissions are filtered to display only the featured ones.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Usage log:
    - Successfully navigated to the Featured Submissions section using the 'Filter on: Featured' button.

    Note:
    - Ensure that 'Featured' submissions exist for content to be displayed after filtering.

    """
    await page.goto("/")
    await page.get_by_role("button", name="Filter on: Featured").click()


async def extract_comment_analysis(page):
    """
    [Function description]
    Extracts detailed comment analysis including user engagement levels, timestamps, content, and trends.

    This function automates the extraction of detailed comment information from a specific webpage. It retrieves
    comprehensive data related to user comments, such as engagement levels (likes, replies), timestamps
    (date and time), content of the comment, and any observable trends.

    [Usage preconditions]
    - You must already be on the webpage that contains comments before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains detailed information for each comment including:
        - "content" (str): The textual content of the comment.
        - "timestamp" (str): The timestamp of when the comment was made.
        - "engagement" (dict): A dictionary containing engagement metrics like "likes" and "replies".
        - "trend" (str): Observable comment trends like sentiment or common topics.
    """
    comments_elements = await page.query_selector_all(".comment")
    comments_data = []
    for comment_element in comments_elements:
        content = await comment_element.query_selector(".comment-content")
        content_text = await content.inner_text()
        timestamp = await comment_element.query_selector(".comment-timestamp")
        timestamp_text = await timestamp.inner_text()
        likes_element = await comment_element.query_selector(".comment-likes")
        likes_count = await likes_element.inner_text()
        replies_element = await comment_element.query_selector(".comment-replies")
        replies_count = await replies_element.inner_text()
        trend = await comment_element.query_selector(".comment-trend")
        trend_text = await trend.inner_text()
        comments_data.append(
            {
                "content": content_text,
                "timestamp": timestamp_text,
                "engagement": {"likes": likes_count, "replies": replies_count},
                "trend": trend_text,
            }
        )
    return comments_data


async def extract_main_navigation_links(page):
    """
    Extracts links from the main navigation menu for sections like 'Home', 'Forums', 'Wiki'.

    This function automates the extraction of navigation links from the main navigation menu
    on the site like 'Home', 'Forums', and 'Wiki'.

    Usage preconditions:
    - This API retrieves navigation links that are presumably visible on the navigation bar
      of a page that follows a similar structure as described in the document AST.
    - **You must already be on the page with a navigation menu before calling this function.**

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
         - "text" (str): The visible text of the navigation link.
         - "url" (str): The URL that the link points to.
    """
    links = await page.query_selector_all("nav a")
    navigation_links = []
    for link in links:
        text = await link.text_content()
        url = await link.get_attribute("href")
        if text and url:
            navigation_links.append({"text": text.strip(), "url": url.strip()})
    return navigation_links


async def search_content_and_extract_details(page, keyword):
    """
    [Function description]
    Explore the search functionality on the page by utilizing the search box to find content related to a specific
    keyword. Extract relevant details such as titles and URLs of the resulting submissions or pages.

    [Usage preconditions]
    - This function operates on a page that contains a search box element.
    - You must be already navigated to the page containing the search functionality.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    keyword : A string keyword to be searched in the search box.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - 'title' (str): The title of the search result item.
        - 'url' (str): The URL associated with the search result item.
    """
    search_box = await page.query_selector('[aria-label="Search query"]')
    await search_box.fill(keyword)
    await search_box.press("Enter")
    results = []
    result_elements = await page.query_selector_all(".search-result-item")
    for element in result_elements:
        title_elem = await element.query_selector(".result-title")
        url_elem = await element.query_selector(".result-url")
        if title_elem and url_elem:
            title = await title_elem.text_content()
            url = await page.evaluate('(el) => el.getAttribute("href")', url_elem)
            results.append({"title": title.strip(), "url": url.strip()})
    return results


async def list_and_count_submissions(page):
    """
    [Function description]
    Lists and counts submissions after applying 'Featured' and 'Hot' filters.

    This function automates the process of applying specific context filters like 'Featured'
    and 'Hot', and then compiles a list of all visible submissions on the page, counting them.

    [Usage preconditions]
    - This API requires the page to be at a section where submissions can be filtered by 'Featured' and sorted by 'Hot'.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        A dictionary containing:
        - "submissions" (list): A list of all submission titles.
        - "count" (int): The total number of submissions.
    """
    filter_button = await page.query_selector(
        'button:text-matches("Filter on: Featured", "i")'
    )
    if filter_button:
        await filter_button.click()
    sort_button = await page.query_selector('button:text-matches("Sort by: Hot", "i")')
    if sort_button:
        await sort_button.click()
    submissions = await page.query_selector_all("div[data-submission]")
    submission_titles = []
    for submission in submissions:
        title_element = await submission.query_selector("h2 a")
        title_text = await (
            await title_element.get_property("textContent")
        ).json_value()
        submission_titles.append(title_text.strip())
    return {"submissions": submission_titles, "count": len(submission_titles)}


async def extract_featured_hot_submissions(page):
    """
    [Function description]
    Extracts submissions that are filtered by 'Featured' and sorted by 'Hot', retrieving their titles, authors, votes, and comments.

    This function automates the extraction of details from the displayed submissions on a forum-like webpage.
    It navigates through each submission in the current listings and gathers necessary information, including:

    - Submission title
    - Submission author
    - Number of votes
    - Number of comments

    [Usage preconditions]
    - The page must be pre-filtered by 'Featured' and pre-sorted by 'Hot' before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title of the submission.
        - "author" (str): The author of the submission.
        - "votes" (str): The number of votes the submission has received.
        - "comments" (str): The number of comments on the submission.
    """
    submissions = []
    submission_elements = await page.query_selector_all(".submission")
    for submission in submission_elements:
        title_element = await submission.query_selector(".submission-title")
        title = await title_element.text_content() if title_element else ""
        author_element = await submission.query_selector(".submission-author")
        author = await author_element.text_content() if author_element else ""
        votes_element = await submission.query_selector(".submission-votes")
        votes = await votes_element.text_content() if votes_element else ""
        comments_element = await submission.query_selector(".submission-comments")
        comments = await comments_element.text_content() if comments_element else ""
        submissions.append(
            {
                "title": title.strip(),
                "author": author.strip(),
                "votes": votes.strip(),
                "comments": comments.strip(),
            }
        )
    return submissions


async def get_navigation_paths(page):
    """
    Retrieves navigation paths from the main navigation bar leading to main sections like 'Home', 'Forums', 'Wiki', and other main areas.

    This function automates the process of gathering navigation links and URLs from the main navigation bar of a website.
    It captures essential paths that are typically used to access core sections of the site.

    Usage preconditions:
    - You must already be on a webpage containing a main navigation bar with links to sections such as 'Home', 'Forums', 'Wiki'.

    Args:
    page : A Playwright `Page` instance used for browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "link" (str): The text of the navigation link.
        - "url" (str): The URL path associated with the navigation link.
    """
    navigation_links = []
    selectors = ['a[href="/"]', 'a[href="/forums"]', 'a[href="/wiki"]']
    for selector in selectors:
        link_element = await page.query_selector(selector)
        link_text = await link_element.inner_text()
        url = await link_element.get_attribute("href")
        navigation_links.append({"link": link_text, "url": url})
    return navigation_links


async def search_and_collect_submissions(page):
    """
    [Function description]
    Searches for specific topics or keywords using the search box, collecting all relevant submissions and details such as title, author, and URL.

    This function automates the search process by typing a given query into a search box and retrieves submission details
    including title, author, and URL from the search results.

    [Usage preconditions]
    - The function assumes you are already on a page that contains a search box and submissions results.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title of the submission.
        - "author" (str): The author of the submission.
        - "url" (str): The URL to access the submission.
    """
    search_box = await page.query_selector("input")
    if search_box:
        await search_box.fill("desired keyword")
        await search_box.press("Enter")
    else:
        raise Exception("Search box not found")
    submissions = []
    submission_elements = await page.query_selector_all(".submission-class")
    for element in submission_elements:
        title_element = await element.query_selector(".title-class")
        author_element = await element.query_selector(".author-class")
        url_element = await element.query_selector("a[href]")
        title = await title_element.inner_text() if title_element else ""
        author = await author_element.inner_text() if author_element else ""
        url = await url_element.get_attribute("href") if url_element else ""
        submissions.append({"title": title, "author": author, "url": url})
    return submissions


async def navigate_main_sections(page):
    """
    [Function description]
    Navigate to main sections of a webpage titled "Postmill" using direct URL navigation.

    This function automates the navigation to crucial sections by accessing known URLs for
    'Home', 'Forums', 'Wiki', 'Submissions', and 'Comments'. This approach facilitates
    reliable navigation without relying solely on the text-matching selectors.

    [Usage preconditions]
    - It is assumed the caller is already on a "Postmill" webpage where
      these navigation options are available.

    Args:
    page : A Playwright `Page` instance that controls browser automation.


    Returns:
    None
    """
    await page.goto("/")
    await page.goto("/forums")
    await page.goto("/wiki")
    await page.goto("/")
    await page.goto("/comments")


async def search_extract_submissions(page):
    """
    Extracts submission data from the Postmill platform.

    This function automates the process of navigating to the Submissions section on
    the Postmill website and extracting details of each submission present in that section.

    [Usage preconditions]
    - You must already be on the main page of the Postmill website where the "Submissions" navigation link is present.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains information of a submission, e.g.,
        - "title" (str): The title of the submission.
        - "url" (str): The URL to the submission.
        - Additional potential metadata as retrieved from the page.
    """
    await (await page.query_selector('a:has-text("Submissions")')).click()
    submissions = []
    submission_elements = await page.query_selector_all(".submission-class")
    for submission in submission_elements:
        title = await (await submission.query_selector(".title-class")).inner_text()
        url = await (await submission.query_selector(".link-class")).get_attribute(
            "href"
        )
        submissions.append({"title": title, "url": url})
    return submissions


async def list_and_filter_submissions_comments(page):
    """
    Automate listing and filtering of submissions and comment filters on the Postmill webpage.

    This function interacts with the filter options on a page containing submissions and comments, providing
    capabilities to automate filter settings adjustments. By clicking filter and sort buttons, users can
    dictate how content is displayed based on predefined criteria (e.g., "Featured", "Hot").

    [Usage preconditions]
    - Ensure that you are navigating the main content of the Postmill homepage, where submissions and comments are listed.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    tuple
        A tuple containing two elements:
        - a boolean indicating success of filter automation.
        - a list of available filter and sort criteria (labels).
    """
    result = []
    filter_button = await page.query_selector('button:has-text("Filter on: Featured")')
    if filter_button:
        await filter_button.click()
        result.append("Filter clicked successfully")
    sort_button = await page.query_selector('button:has-text("Sort by: Hot")')
    if sort_button:
        await sort_button.click()
        result.append("Sort clicked successfully")
    return len(result) == 2, result
