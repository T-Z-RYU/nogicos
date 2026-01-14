async def navigate_to_all_projects_list(page):
    """
    Navigate to the All Projects List on GitLab.

    This function will open the GitLab dashboard, which is where all projects are listed.
    It makes use of the default URL and verifies that the correct page title is present.

    Usage Log:
    - Called when starting from the main dashboard and successfully verified that it was already on the correct page.

    Arguments:
    page: A Playwright page object representing the browser page.

    Expected Outcome:
    - The function navigates to the GitLab dashboard where all projects are listed.
    """
    await page.goto("/")
    assert "Projects · Dashboard · GitLab" in await page.title()


async def extract_repository_information(page):
    """
    Extracts detailed information about all listed repositories on the current GitLab explore page.

    This function automates the extraction of repository details from the GitLab explore page, such as:
    - Repository name
    - Description
    - Owner/maintainer role
    - Star counts
    - Fork counts
    - Merge requests
    - Issue counts
    - Last updated time

    Usage preconditions:
    - You must already be on the GitLab "Explore Projects" page before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the detailed information for a given repository.
    """
    await page.goto("/explore")
    repository_list = []
    repo_elements = await page.query_selector_all("div.js-project-list-item")
    for repo in repo_elements:
        name = await (await repo.query_selector("h2 > a")).inner_text()
        description_elem = await repo.query_selector("div.project-item-description")
        description = await description_elem.inner_text() if description_elem else ""
        owner_elem = await repo.query_selector("h2")
        owner = await owner_elem.inner_text() if owner_elem else ""
        star_count_elem = await repo.query_selector('a[href$="starrers"]')
        star_count = await star_count_elem.inner_text() if star_count_elem else "0"
        fork_count_elem = await repo.query_selector('a[href$="forks"]')
        fork_count = await fork_count_elem.inner_text() if fork_count_elem else "0"
        merge_request_elem = await repo.query_selector('a[href$="merge_requests"]')
        merge_requests = (
            await merge_request_elem.inner_text() if merge_request_elem else "0"
        )
        issue_count_elem = await repo.query_selector('a[href$="issues"]')
        issues = await issue_count_elem.inner_text() if issue_count_elem else "0"
        last_updated_elem = await repo.query_selector("time")
        last_updated = await last_updated_elem.inner_text() if last_updated_elem else ""
        repository_info = {
            "name": name,
            "description": description,
            "owner": owner,
            "star_count": star_count,
            "fork_count": fork_count,
            "merge_requests": merge_requests,
            "issues": issues,
            "last_updated": last_updated,
        }
        repository_list.append(repository_info)
    return repository_list

async def retrieve_repo_information(page):
    '''
    Retrieve information about all repositories associated with my account from Gitlab.

    This function navigates to the main page of GitLab and extracts details of all repositories 
    associated with my account. It gathers information including:
    
    - Repository name
    - Visibility status (Public/Private)
    - My role in the repository
    - Number of stars, forks, merge requests, and issues
    - Last updated timestamp

    Args:
        page (Page): A Playwright `Page` instance that controls browser automation.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing details of all my repositories:
            - "name" (str): Repository name with namespace
            - "visibility" (str): Repository visibility status ('Public' or 'Private')
            - "role" (str): My role in the repository
            - "stars" (str): Number of stars
            - "forks" (str): Number of forks
            - "merge_requests" (str): Number of merge requests
            - "issues" (str): Number of issues
            - "last_updated" (str): Last updated timestamp
    '''
    await page.goto("/")
    repo_list = await page.query_selector_all(".project-row")
    repos_info = []

    for repo in repo_list:
        # Retrieve repository name with namespace
        name_element = await repo.query_selector("a.text-plain.js-prefetch-document")
        name = await name_element.inner_text() if name_element else "N/A"

        # Retrieve visibility status
        visibility_element = await repo.query_selector("span.has-tooltip svg")
        visibility = "Private" if visibility_element and await visibility_element.get_attribute('data-testid') == "lock-icon" else "Public"

        # Retrieve user role
        role_element = await repo.query_selector('span[data-qa-selector="user_role_content"]')
        user_role = await role_element.inner_text() if role_element else "N/A"

        # Retrieve counts for stars, forks, merge requests, and issues
        try:
            stars_element = await repo.query_selector("a.stars")
            stars = await stars_element.inner_text() if stars_element else "0"

            forks_element = await repo.query_selector("a.forks")
            forks = await forks_element.inner_text() if forks_element else "0"

            merge_requests_element = await repo.query_selector("a.merge-requests")
            merge_requests = await merge_requests_element.inner_text() if merge_requests_element else "0"

            issues_element = await repo.query_selector("a.issues")
            issues = await issues_element.inner_text() if issues_element else "0"
        except:
            stars = forks = merge_requests = issues = "0"

        # Retrieve last updated time
        updated_element = await repo.query_selector("time.js-timeago")
        last_updated = await updated_element.get_attribute("datetime") if updated_element else "N/A"

        repos_info.append({
            "name": name,
            "visibility": visibility,
            "role": user_role,
            "stars": stars.strip(),
            "forks": forks.strip(),
            "merge_requests": merge_requests.strip(),
            "issues": issues.strip(),
            "last_updated": last_updated.strip(),
        })

    return repos_info


async def navigate_to_current_repo_contributors(page):
    '''
    Navigate to the contributors of the GitLab repository you are currently at.

    **Important:**
    - **You must already be on a GitLab project repository page before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.
    '''
    await page.locator('[data-track-label="repository_menu"]').click()
    await page.locator('[data-track-label="contributors"] a').click()


async def get_current_repo_commits(page):
    '''
    Retrieves commit information from the GitLab repository you are currently at.

    This function automates the extraction of commit details from the current page
    of a GitLab repository. It navigates through the repository's commits section
    and gathers information about each commit, including:
    
    - Commit message
    - Author name
    - Commit SHA (hash identifier)
    - Commit timestamp

    **Important:**
    - This API retrieves commit information for the GitLab repository **you are currently at**.
    - **You must already be on a GitLab project repository page before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "message" (str): The commit message.
        - "author" (str): The name of the commit author.
        - "sha" (str): The unique SHA identifier of the commit.
        - "time" (str): The timestamp of the commit in ISO 8601 format.
    '''
    await page.locator('[data-track-label="repository_menu"]').click()
    await page.locator('[data-track-label="commits"] a').click()
    
    commit_elements = await page.query_selector_all("li.commit")
    commit_data = []

    for commit_element in commit_elements:
        message_element = await commit_element.query_selector("a.commit-row-message")
        if message_element:
            commit_message = await message_element.inner_text()
        else:
            commit_message = ""

        author_element = await commit_element.query_selector("a.commit-author-link")
        if author_element:
            author_name = await author_element.inner_text()
        else:
            author_name = ""

        sha_element = await commit_element.query_selector("div.commit-sha-group div.label")
        if sha_element:
            commit_sha = await sha_element.inner_text()
        else:
            commit_sha = ""

        time_element = await commit_element.query_selector("time.js-timeago")
        if time_element:
            commit_time = await time_element.get_attribute("datetime")
        else:
            commit_time = ""

        commit_data.append(
            {
                "message": commit_message,
                "author": author_name,
                "sha": commit_sha,
                "time": commit_time,
            }
        )
    return commit_data


async def get_repository_engagement_metrics(page):
    """
    [Function description]
    Retrieves engagement metrics for each repository listed on the current GitLab dashboard page.

    This function automates the collection of repository metrics from the current dashboard page
    and identifies the number of starrers, forks, merge requests, and issues associated with each repository.

    [Usage preconditions]
    - You must be on the GitLab dashboard page where repositories are listed before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "repository" (str): The name of the repository.
        - "starrers" (int): The number of starrers.
        - "forks" (int): The number of forks.
        - "merge_requests" (int): The number of merge requests.
        - "issues" (int): The number of issues.
    """
    await page.goto("/")
    repositories = []
    repository_elements = await page.query_selector_all("h2.heading")
    for repo_element in repository_elements:
        repo_link_element = await repo_element.query_selector("a")
        repo_name = (await repo_link_element.inner_text()).strip()
        metrics = {}
        starrers_link_element = await repo_element.query_selector(
            'a[href*="/-/starrers"]'
        )
        forks_link_element = await repo_element.query_selector('a[href*="/-/forks"]')
        merge_requests_link_element = await repo_element.query_selector(
            'a[href*="/-/merge_requests"]'
        )
        issues_link_element = await repo_element.query_selector('a[href*="/-/issues"]')
        metrics["repository"] = repo_name
        metrics["starrers"] = (
            int(await starrers_link_element.inner_text())
            if starrers_link_element
            else 0
        )
        metrics["forks"] = (
            int(await forks_link_element.inner_text()) if forks_link_element else 0
        )
        metrics["merge_requests"] = (
            int(await merge_requests_link_element.inner_text())
            if merge_requests_link_element
            else 0
        )
        metrics["issues"] = (
            int(await issues_link_element.inner_text()) if issues_link_element else 0
        )
        repositories.append(metrics)
    return repositories


async def identify_most_starred_repositories(page):
    """
    [Function description]
    Identify and list repositories sorted by star count to determine popularity.

    This function automates the extraction of repository information, including title and star count,
    from the dashboard of a GitLab page where repositories are listed. It then sorts the repositories
    based on star count in descending order to highlight the most popular ones.

    [Usage preconditions]
    - **You must already be on the repository dashboard or projects listing page before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title of the repository.
        - "stars" (int): The star count of the repository.
    """
    await page.goto("/")
    repo_elements = await page.query_selector_all("h2 > a")
    star_elements = await page.query_selector_all('a[href*="/-/starrers"]')
    repositories = []
    for repo, star in zip(repo_elements, star_elements):
        title = await repo.text_content()
        stars = await star.text_content()
        repositories.append({"title": title.strip(), "stars": int(stars.strip())})
    sorted_repositories = sorted(repositories, key=lambda x: x["stars"], reverse=True)
    return sorted_repositories


async def get_all_repository_details_by_update_recency(page):
    """
    [Function description]
    Retrieves repository details from the GitLab dashboard page, assuming the repositories are already sorted by update recency.

    This function extracts the following information for each repository:
    - Repository name
    - Repository URL

    [Usage preconditions]
    - You must already be on the GitLab dashboard page listing all repositories.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the repository.
        - "url" (str): The URL of the repository.
    """
    await page.goto("/")
    repos = []
    repo_elements = await page.query_selector_all("h2 a")
    for link_element in repo_elements:
        repo_name = await (await link_element.get_property("innerText")).json_value()
        repo_url = await (await link_element.get_property("href")).json_value()
        repos.append({"name": repo_name.strip(), "url": repo_url})
    return repos


async def get_repositories_sorted_by_fork_count(page):
    """
    Retrieve repository information sorted by fork count from the current page.

    This function automates the extraction of repository details including the
    number of forks, and sorts the repositories in descending order based on
    their fork counts.

    [Usage preconditions]
    - You must already be on a page displaying a list of repositories with fork count visible.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries sorted by fork count, where each dictionary contains:
        - "name" (str): The name of the repository.
        - "forks" (int): The fork count of the repository.
    """
    await page.goto("/")
    repo_elements = await page.query_selector_all("main > h2.heading")
    repo_data = []
    for repo_element in repo_elements:
        name_element = await repo_element.query_selector("a")
        name = await name_element.inner_text() if name_element else ""
        link_pattern = "/forks"
        forks_count = (
            await page.eval_on_selector(
                f"a[href*='{link_pattern}']", "element => element.innerText"
            )
            if name
            else "0"
        )
        forks = int(forks_count)
        repo_data.append({"name": name, "forks": forks})
    sorted_repos = sorted(repo_data, key=lambda x: x["forks"], reverse=True)
    return sorted_repos


async def search_repositories_by_keyword(page, keyword):
    """
    [Function description]
    Searches for repositories on the GitLab page using a specified keyword.
    Executes a search operation in the repository section and retrieves a list of repositories' details based on the search keyword.

    [Usage preconditions]
    - You must be on a GitLab repository dashboard or search page before invoking this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    keyword : A string representing the keyword to search for.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains repository information, such as:
        - "name" (str): The name of the repository.
        - "url" (str): The URL leading to the repository.
    """
    await page.goto("/")
    search_input = await page.query_selector('input[placeholder="Search GitLab"]')
    await search_input.fill(keyword)
    await page.keyboard.press("Enter")
    await page.wait_for_load_state("networkidle")
    projects_list = await page.query_selector_all("main div a[title]")
    results = []
    for project_link in projects_list:
        project_name = await project_link.get_attribute("title")
        project_url = await project_link.get_attribute("href")
        results.append({"name": project_name.strip(), "url": project_url})
    return results


async def navigate_to_new_project_creation(page):
    """
    Navigate to the 'New Project' creation page on GitLab.

    This function automates the process of opening the GitLab dashboard and clicking
    the 'New project' link to navigate to the project creation page.

    Usage Log:
    - Called from the 'Projects · Dashboard · GitLab' page and successfully navigated to the project creation section.

    Arguments:
    page: A Playwright page object representing the browser page.

    Expected Outcome:
    - The function navigates to the 'New Project' creation section on GitLab.
    """
    await page.goto("/")
    await page.get_by_role("link", name="New project").click()


async def get_new_project_options(page):
    """
    [Function description]
    Identifies and describes the different options available for setting up a new project on GitLab.

    This function automates the extraction of project setup options from the GitLab "New Project" page.
    It retrieves information on the options available for creating a new project:

    - Creating a blank project
    - Creating from a template
    - Importing a project from an external source

    [Usage preconditions]
    - This API extracts information from the GitLab "New Project" page.
    - **You must already be on the GitLab "New Project" page before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "title" (str): The title of the project setup option.
        - "description" (str): The description of what the option does.
    """
    await page.goto("/projects/new")
    blank_project_option = await (
        await page.query_selector('a[href="#blank_project"]')
    ).inner_text()
    template_project_option = await (
        await page.query_selector('a[href="#create_from_template"]')
    ).inner_text()
    import_project_option = await (
        await page.query_selector('a[href="#import_project"]')
    ).inner_text()
    options = [
        {"title": "Create blank project", "description": blank_project_option},
        {"title": "Create from template", "description": template_project_option},
        {"title": "Import project", "description": import_project_option},
    ]
    return options


async def retrieve_show_command_instructions(page):
    """
    Retrieve command-line instructions from the current page.

    This function automates the process of interacting with a 'Show command'
    link on the page where new projects can be created. When clicked, it
    retrieves any command-line instructions that are displayed as a result.

    Usage preconditions:
    - Make sure the page contains a 'Show command' link for retrieving instructions.
    - The function assumes you are already on a correct page that includes
      this functionality.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    str
        The command-line instructions displayed after clicking the 'Show command' link.
    """
    await page.goto("/projects/new")
    show_command_link = await page.query_selector('main >> text="Show command"')
    if show_command_link:
        await show_command_link.click()
        instructions_element = await page.query_selector("main >> .instructions")
        if instructions_element:
            instructions_text = await instructions_element.inner_text()
            return instructions_text
    return


async def summarize_navigation_links(page):
    """
    [Function description]
    Gather quick navigation options available on the GitLab page.

    This function automates gathering shortcut navigation links from a GitLab page
    to understand the quick navigation options available to users. It identifies
    links such as 'Issues', 'Merge requests', and others.

    [Usage preconditions]
    - You must already be on a GitLab page with navigation links before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The text content of the navigation link.
        - "url" (str): The URL the navigation link points to.
    """
    await page.goto("/projects/new")
    navigation_links_text = [
        "Issues",
        "Merge requests",
        "To-Do List",
        "Help",
        "Create new...",
        "Dashboard",
    ]
    links_summary = []
    for link_text in navigation_links_text:
        link_element = await page.query_selector(f"a:text('{link_text}')")
        if link_element:
            link_url = await link_element.get_attribute("href")
            if link_url is not None:
                links_summary.append({"name": link_text, "url": link_url})
    return links_summary


async def get_byte_blaze_projects(page):
    """
    [Function description]
    Extracts all projects owned or maintained by 'Byte Blaze' from the current GitLab page.

    This function scans the current web page for projects associated with 'Byte Blaze', retrieving
    both the project names and descriptions (if available) under the current site's project lists.

    [Usage preconditions]
    - The page should be displaying a list of projects where 'Byte Blaze' can be present as a maintainer or owner.
    - **You must already be on the GitLab projects dashboard page.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
       A list of dictionaries where each dictionary contains:
       - "name" (str): The name of the project.
       - "description" (str): The description of the project.
    """
    await page.goto("/")
    projects = []
    project_elements = await page.query_selector_all('h2:has-text("Byte Blaze /")')
    for project_element in project_elements:
        name_element = await project_element.query_selector("a")
        name = await (await name_element.get_property("textContent")).json_value()
        description_selector = (
            f'//h2[normalize-space(text())="{name}"]/following-sibling::div'
        )
        description_elements = await page.query_selector_all(description_selector)
        description = (
            (
                await (
                    await description_elements[0].get_property("textContent")
                ).json_value()
            ).strip()
            if description_elements
            else "No description provided"
        )
        projects.append({"name": name, "description": description})
    return projects


async def find_repository_with_highest_issue_count(page):
    """
    [Function description]
    Analyzes the list of repositories on the current page to identify the repository
    with the highest number of issues.

    [Usage preconditions]
    - Ensure you are on a GitLab project dashboard page listing multiple repositories
      before invoking this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        A dictionary containing the following keys:
        - "repository_name" (str): The name of the repository with the highest issue count.
        - "issue_count" (int): The maximum number of issues in the repository.
    """
    await page.goto("/")
    repositories = await page.query_selector_all("h2.heading")
    highest_issue_count = 0
    repository_with_most_issues = ""
    for repo in repositories:
        repo_name_element = await repo.query_selector("a")
        repo_name = await repo_name_element.inner_text()
        issue_count_element = await repo.query_selector('a[href$="/-/issues"]')
        if issue_count_element:
            issue_count_text = await issue_count_element.inner_text()
            issue_count = int(issue_count_text)
            if issue_count > highest_issue_count:
                highest_issue_count = issue_count
                repository_with_most_issues = repo_name
    return {
        "repository_name": repository_with_most_issues,
        "issue_count": highest_issue_count,
    }


async def get_recently_updated_projects(page):
    """
    [Function description]
    Retrieves a list of projects updated within the last year from the GitLab dashboard.

    This function automates the traversal of a GitLab dashboard page displaying various projects.
    It identifies projects that have been updated within the past year and compiles their details.

    [Usage preconditions]
    - You need to be on a GitLab dashboard page displaying your projects when invoking this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries with each dictionary containing:
        - "name" (str): The name of the project.
        - "url" (str): The URL to the project's page.
        - "update_time" (str): The date/time when the project was last updated.
    """
    await page.goto("/")
    import datetime

    projects_info = []
    current_year = datetime.datetime.now().year
    project_selectors = await page.query_selector_all("main h2.heading")
    for selector in project_selectors:
        project_name = await (await selector.query_selector("a")).inner_text()
        project_url = await (await selector.query_selector("a")).get_attribute("href")
        update_time_element = await selector.query_selector("time")
        update_time_str = (
            await update_time_element.inner_text() if update_time_element else ""
        )
        update_time = (
            datetime.datetime.strptime(update_time_str, "%Y-%m-%d")
            if update_time_str
            else None
        )
        if update_time and current_year - update_time.year <= 1:
            projects_info.append(
                {
                    "name": project_name,
                    "url": project_url,
                    "update_time": update_time.isoformat() if update_time else "",
                }
            )
    return projects_info


async def extract_project_creation_options(page):
    """
    Extracts the available project creation options and their descriptions from the current webpage.

    This function automates the extraction of project creation options, which includes
    retrieving the option's title and description presented together on the page.

    [Usage preconditions]
    - Ensure that you are on the correct page where project creation options are listed.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of str
        A list containing strings, each representing a project creation option along
        with its description.
    """
    await page.goto("/projects/new")
    options_elements = await page.query_selector_all('main a[href^="#"]')
    options_list = []
    for element in options_elements:
        text = await element.inner_text()
        options_list.append(text)
    return options_list


async def get_most_starred_repositories(page):
    """
    [Function description]
    Identify and list the most starred repositories for each owner, sorting by star count.

    This function automates the extraction of repository details from the current page,
    including the owner's name, repository name, and the star count.
    It sorts repositories by their star counts for each owner.

    [Usage preconditions]
    - This API retrieves repository star information for the GitLab page **you are currently at**.
    - **You must already be on a GitLab repositories page before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "owner" (str): The name of the repository owner.
        - "repo_name" (str): The name of the repository.
        - "stars" (int): The number of stars the repository has.
    """
    await page.goto("/")
    repository_headings = await page.query_selector_all("main h2")
    repositories = []
    for heading in repository_headings:
        heading_text = await heading.text_content()
        if " / " in heading_text:
            owner, repo_name = heading_text.split(" / ", 1)
            starrers_link = await heading.query_selector(
                "xpath=following::a[href*='/-/starrers']"
            )
            if starrers_link:
                star_text = await starrers_link.text_content()
                stars = int(star_text.strip())
                repositories.append(
                    {
                        "owner": owner.strip(),
                        "repo_name": repo_name.strip(),
                        "stars": stars,
                    }
                )
    repositories.sort(key=lambda x: (x["owner"], -x["stars"]))
    return repositories


async def retrieve_all_my_repos(page):
    '''
    [Function description]
    Retrieve information about all repositories associated with my account from Gitlab.

    This function navigates to the main page of GitLab and extracts details of all repositories 
    associated with my account. It gathers information including:
    
    - Repository name
    - Visibility status (Public/Private)
    - My role in the repository
    - Number of stars, forks, merge requests, and issues
    - Last updated timestamp

    Args:
        page (Page): A Playwright `Page` instance that controls browser automation.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing details of all my repositories:
            - "name" (str): Repository name with namespace
            - "visibility" (str): Repository visibility status ('Public' or 'Private')
            - "role" (str): My role in the repository
            - "stars" (str): Number of stars
            - "forks" (str): Number of forks
            - "merge_requests" (str): Number of merge requests
            - "issues" (str): Number of issues
            - "last_updated" (str): Last updated timestamp
    '''
    await page.goto("/")
    repo_list = await page.query_selector_all(".project-row")
    repos_info = []
    for repo in repo_list:
        name_element = await repo.query_selector("a.text-plain.js-prefetch-document")
        name = await name_element.inner_text() if name_element else "N/A"
        visibility_element = await repo.query_selector("span.has-tooltip svg")
        visibility = "Private" if visibility_element and await visibility_element.get_attribute('data-testid') == "lock-icon" else "Public"
        role_element = await repo.query_selector('span[data-qa-selector="user_role_content"]')
        user_role = await role_element.inner_text() if role_element else "N/A"
        try:
            stars_element = await repo.query_selector("a.stars")
            stars = await stars_element.inner_text() if stars_element else "0"
            forks_element = await repo.query_selector("a.forks")
            forks = await forks_element.inner_text() if forks_element else "0"
            merge_requests_element = await repo.query_selector("a.merge-requests")
            merge_requests = await merge_requests_element.inner_text() if merge_requests_element else "0"
            issues_element = await repo.query_selector("a.issues")
            issues = await issues_element.inner_text() if issues_element else "0"
        except:
            stars = forks = merge_requests = issues = "0"
        updated_element = await repo.query_selector("time.js-timeago")
        last_updated = await updated_element.get_attribute("datetime") if updated_element else "N/A"
        repos_info.append({
            "name": name,
            "visibility": visibility,
            "role": user_role,
            "stars": stars.strip(),
            "forks": forks.strip(),
            "merge_requests": merge_requests.strip(),
            "issues": issues.strip(),
            "last_updated": last_updated.strip(),
        })
    return repos_info


async def extract_repos_with_open_issues(page):
    """
    Extract repositories with open issues and their respective issue counts.

    This function automates the extraction of repository names and their open issue counts
    from a dashboard page. It queries the page for all repositories listed therein and
    gathers information about each repository that has open issues.

    [Usage preconditions]
    - This API is intended to be called when you're already on the GitLab Dashboard page.
    - The page must be loaded with repositories and their issue counts visible.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "repository" (str): The name of the repository.
        - "open_issues" (int): The count of open issues in the repository.
    """
    await page.goto("/")
    repo_elements = await page.query_selector_all("h2 > a")
    issue_elements = await page.query_selector_all('a[href*="/issues"]')
    repo_data = []
    for repo_elem, issue_elem in zip(repo_elements, issue_elements):
        repo_name = await (await repo_elem.get_property("textContent")).json_value()
        issue_count_text = await (
            await issue_elem.get_property("textContent")
        ).json_value()
        issue_count = int(issue_count_text) if issue_count_text.isdigit() else 0
        if issue_count > 0:
            repo_data.append(
                {"repository": repo_name.strip(), "open_issues": issue_count}
            )
    return repo_data


async def retrieve_last_update_timings_for_all_projects(page):
    """
    [Function description]
    Gathers information about the last update timing for each project listed on the current GitLab dashboard page.

    This function automates the process of extracting the most recent update time for each project displayed
    on the GitLab dashboard page you are currently on. It is useful for tracking potentially stale projects
    and identifying projects that have been recently modified.

    [Usage preconditions]
    - This API retrieves the last update timing for projects visible on the GitLab dashboard page **you are currently on**.
    - **You must already be on a GitLab dashboard page listing multiple projects before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "project_name" (str): The name of the project.
        - "last_updated" (str): The last update time of the project.
    """
    await page.goto("/")
    project_update_times = []
    projects = await page.query_selector_all("div.project-item")
    for project in projects:
        project_name_elem = await project.query_selector("h2")
        last_updated_elem = await project.query_selector(".last-update-time")
        if project_name_elem and last_updated_elem:
            project_name = await project_name_elem.inner_text()
            last_updated = await last_updated_elem.inner_text()
            project_update_times.append(
                {
                    "project_name": project_name.strip(),
                    "last_updated": last_updated.strip(),
                }
            )
    return project_update_times


async def extract_new_project_setup_options(page):
    """
    [Function description]
    Extracts the available new project setup options on the GitLab page, such as
    'Create blank project', 'Create from template', and 'Import project'.

    This function automates the retrieval of project setup options by parsing
    the elements on the GitLab new project setup page for recognizable patterns
    associated with these options.

    [Usage preconditions]
    - You must already be on the GitLab 'New Project' setup page before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of str
        A list of strings, where each string represents a new project setup option available on the page.
    """
    await page.goto("/projects/new")
    options = []
    blank_project_link = await page.query_selector('a[href="#blank_project"]')
    if blank_project_link:
        blank_project_text = await blank_project_link.text_content()
        options.append(blank_project_text.strip())
    template_project_link = await page.query_selector('a[href="#create_from_template"]')
    if template_project_link:
        template_project_text = await template_project_link.text_content()
        options.append(template_project_text.strip())
    import_project_link = await page.query_selector('a[href="#import_project"]')
    if import_project_link:
        import_project_text = await import_project_link.text_content()
        options.append(import_project_text.strip())
    return options


async def extract_command_line_instructions(page):
    """
    Extract command-line instructions for project creation by interacting with the 'Show command' link on the current page.

    [Usage preconditions]
    - You must already be on a page that contains a 'Show command' link for project creation before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    str
        A string containing the command-line instructions extracted from the page.
    """
    await page.goto("/projects/new")
    await page.goto("/projects/new")
    show_command_link = await page.query_selector('main a:text-is("Show command")')
    if not show_command_link:
        raise ValueError(
            "'Show command' link not found. Please check if the page structure has changed."
        )
    await show_command_link.click()
    command_element = await page.query_selector("main pre")
    if not command_element:
        raise ValueError(
            "Command instructions element not found. Please check if the page structure has changed."
        )
    command_text = await command_element.text_content()
    return command_text


async def extract_quick_navigation_links(page):
    """
    [Function description]
    Extracts and lists quick navigation links available on the current dashboard page.

    This function automates the extraction of quick navigation links such as 'Issues',
    'Merge requests', and 'To-Do List' from the user's dashboard page.
    These links enable efficient navigation to different sections.

    [Usage preconditions]
    - You must already be on a GitLab dashboard page before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "text" (str): The text of the navigation link.
        - "url" (str): The URL associated with the navigation link.
    """
    await page.goto("/projects/new")
    links = []
    selectors = [
        'a:has-text("Issues")',
        'a:has-text("Merge requests")',
        'a:has-text("To-Do List")',
    ]
    for selector in selectors:
        element = await page.query_selector(selector)
        if element:
            text = await element.inner_text()
            url = await element.get_attribute("href")
            links.append({"text": text, "url": url})
    return links


async def navigate_to_personal_projects(page):
    """
    Navigate to the user's personal projects section on the GitLab dashboard.

    This function automates the action of clicking the 'Personal' link under the GitLab dashboard's main
    section, which redirects the user to their personal project listings.

    [Usage preconditions]
    - Ensure you are on the GitLab dashboard page with project categories listed.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Usage Log:
    - Navigating from the GitLab dashboard (/dashboard) to the personal projects section successfully.
    """
    await page.goto("/")
    await page.get_by_role("main").get_by_role("link", name="Personal").click()


async def extract_repository_info(page):
    """
    Extracts repository names, descriptions, owner information, and URLs from the GitLab dashboard.

    This function navigates through the GitLab dashboard page, extracts relevant details about each repository listed,
    and returns a comprehensive set of data for each project, including:

    - Repository name
    - Owner name
    - URL to the repository

    [Usage preconditions]
    - Must be on the dashboard page where multiple repositories are listed.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "repo_name" (str): The name of the repository.
        - "owner_name" (str): The name of the repository owner.
        - "url" (str): The URL to the repository.
    """
    await page.goto("/?personal=true&sort=name_asc")
    repositories = await page.query_selector_all("main h2")
    repo_info = []
    for repo in repositories:
        repo_text = await repo.inner_text()
        repo_link_elem = await repo.query_selector("a")
        repo_url = await repo_link_elem.get_attribute("href")
        owner_name, repo_name = repo_text.split(" / ")
        info = {"repo_name": repo_name, "owner_name": owner_name, "url": repo_url}
        repo_info.append(info)
    return repo_info


async def gather_repository_engagement_metrics(page):
    """
    [Function description]
    Gathers engagement metrics including star count, forks, merge requests, and issues for each repository listed on the current GitLab project dashboard.

    This function automates the extraction of engagement metrics from the current page
    of a GitLab project dashboard page. It navigates through each listed repository segment
    and gathers information about each repository including:

    - Star count
    - Fork count
    - Merge request count
    - Issue count

    [Usage preconditions]
    - This API retrieves engagement metrics for the repositories **on the current GitLab dashboard page**.
    - **You must already be on the GitLab project dashboard page before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "repository_name" (str): The name of the repository.
        - "stars" (int): The number of stars the repository has.
        - "forks" (int): The number of forks the repository has.
        - "merge_requests" (int): The number of merge requests for the repository.
        - "issues" (int): The number of issues for the repository.
    """
    await page.goto("/?personal=true&sort=name_asc")
    repositories_data = []
    repo_elements = await page.query_selector_all("h2 > a")
    for repo_element in repo_elements:
        temp_repo = await repo_element.inner_text()
        repo_name = temp_repo.split(" ")[-1]
        star_count_link = await page.query_selector(
            f'a[href$="/{repo_name}/-/starrers"]'
        )
        fork_count_link = await page.query_selector(f'a[href$="/{repo_name}/-/forks"]')
        merge_count_link = await page.query_selector(
            f'a[href$="/{repo_name}/-/merge_requests"]'
        )
        issue_count_link = await page.query_selector(
            f'a[href$="/{repo_name}/-/issues"]'
        )
        stars = int(
            await (await star_count_link.get_property("innerText")).json_value()
        )
        forks = int(
            await (await fork_count_link.get_property("innerText")).json_value()
        )
        merge_requests = int(
            await (await merge_count_link.get_property("innerText")).json_value()
        )
        issues = int(
            await (await issue_count_link.get_property("innerText")).json_value()
        )
        repositories_data.append(
            {
                "repository_name": repo_name,
                "stars": stars,
                "forks": forks,
                "merge_requests": merge_requests,
                "issues": issues,
            }
        )
    return repositories_data


async def list_repositories_by_star_count(page):
    """
    [Function description]
    Identifies and lists repositories in descending order based on their star count.

    This function automates the extraction of repository names and their star counts from the page,
    and sorts them in descending order based on the star count.

    [Usage preconditions]
    - This function should be called when you are already on a page listing repositories
      with their respective star counts displayed.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A sorted list of dictionaries where each dictionary represents a repository with:
        - "name" (str): The name of the repository.
        - "star_count" (int): The count of stars the repository has.
    """
    await page.goto("/?personal=true&sort=name_asc")
    await page.goto("/?personal=true&sort=name_asc")
    repo_elements = await page.query_selector_all("main h2")
    results = []
    for repo in repo_elements:
        name_element = await repo.query_selector("a")
        name = await name_element.text_content()
        star_element = await repo.locator(
            "xpath=following-sibling::a[contains(@href, '-/starrers')]"
        )
        star_count_text = await star_element.text_content()
        star_count = (
            int(star_count_text.strip()) if star_count_text.strip().isdigit() else 0
        )
        results.append({"name": name, "star_count": star_count})
    results.sort(key=lambda x: x["star_count"], reverse=True)
    return results


async def navigate_to_starred_projects(page):
    """
    Navigate to the starred projects page on GitLab from the dashboard.

    This function automates the process of clicking the 'Starred' link under the
    dashboard section of GitLab, which redirects the user to their starred project listings.

    Usage Log:
    - Successfully navigated to the starred projects page from the dashboard using the 'Starred' link.

    Args:
    page: A Playwright `Page` instance to control browser automation.

    Expected Outcome:
    - The function navigates to the 'Starred Projects' section on GitLab.
    """
    await page.goto("/")
    await page.get_by_role("link", name="Starred 3").click()


async def list_repositories_with_zero_forks(page):
    """
    [Function description]
    Retrieves a list of repositories that have zero forks on the GitLab dashboard page.

    This function automates the extraction of repository information from the current dashboard
    page on GitLab, specifically identifying those with no forks. It processes each repository
    entry and checks the fork count, collecting those with zero forks.

    [Usage preconditions]
    - This API lists repositories with zero forks on the dashboard page **you are currently at**.
    - **You must already be on a GitLab dashboard repository list page before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "name" (str): The name of the repository with zero forks.
        - "url" (str): The URL of the repository.
    """
    await page.goto("/dashboard/projects/starred")
    repository_elements = await page.query_selector_all("h2.heading a")
    repositories_with_zero_forks = []
    for repo in repository_elements:
        repo_name = await repo.inner_text()
        repo_url = await repo.get_attribute("href")
        fork_element = await page.query_selector(f'a[href="{repo_url}/-/forks"]')
        if fork_element:
            fork_count_text = await fork_element.inner_text()
            if fork_count_text.strip() == "0":
                repositories_with_zero_forks.append(
                    {"name": repo_name, "url": repo_url}
                )
    return repositories_with_zero_forks


async def find_old_repositories(page):
    """
    [Function description]
    Finds and retrieves repositories on the current GitLab dashboard that have not been updated for over a year.

    The function scans the dashboard for repositories, checks their last updated timestamps,
    and collects information about those which haven’t been updated for more than a year.

    [Usage preconditions]
    - You must be on the GitLab dashboard page containing the list of repositories.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries each containing:
        - "name" (str): The name of the repository.
        - "last_updated" (str): The last updated timestamp in ISO 8601 format.
    """
    await page.goto("/dashboard/projects/starred")
    import datetime
    from datetime import timezone

    old_repositories = []
    current_date = datetime.datetime.now(timezone.utc)
    repo_elements = await page.query_selector_all("h2 > a")
    repos_info = []
    for repo_element in repo_elements:
        repo_name = await repo_element.inner_text()
        repo_link = await repo_element.get_attribute("href")
        repos_info.append((repo_name, repo_link))
    for repo_name, repo_link in repos_info:
        await page.goto(repo_link)
        timestamp_element = await page.query_selector("time")
        if timestamp_element:
            last_updated_text = await timestamp_element.get_attribute("datetime")
            if last_updated_text:
                last_updated_date = datetime.datetime.fromisoformat(
                    last_updated_text
                ).replace(tzinfo=timezone.utc)
                difference = current_date - last_updated_date
                if difference.days > 365:
                    old_repositories.append(
                        {"name": repo_name, "last_updated": last_updated_text}
                    )
    return old_repositories


async def identify_repos_with_high_issues(page):
    """
    [Function description]
    Identifies repositories whose issue count exceeds 30 from the current GitLab page.

    This function automates the process of scanning through repositories listed on the current page,
    capturing their issue counts and determining which repositories have issue counts that exceed 30.

    [Usage preconditions]
    - You must be on a GitLab page listing repositories with issue counts for them.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of str
        A list of repository names (as displayed on the page) where the issue count exceeds 30.
    """
    await page.goto("/dashboard/projects/starred")
    repo_names_with_high_issues = []
    repo_elements = await page.query_selector_all("h2 > a")
    issue_elements = await page.query_selector_all('a[href*="/issues"]')
    for repo_elem, issue_elem in zip(repo_elements, issue_elements):
        repo_name = await repo_elem.text_content()
        issue_count_text = await issue_elem.text_content()
        issue_count = int(issue_count_text)
        if issue_count > 30:
            repo_names_with_high_issues.append(repo_name)
    return repo_names_with_high_issues


async def filter_projects_by_recent_update(page):
    """
    [Function description]
    Filters projects on the dashboard that have been updated within the last month.

    This function automates the retrieval of project update information from the current page
    and filters the projects modified in the last month, gathering their names and URLs.

    [Usage preconditions]
    - **You must already be on a GitLab project dashboard page before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The project name.
        - "url" (str): The project URL.
        - "updated" (str): The last updated date of the project.
    """
    await page.goto("/dashboard/projects/starred")
    import datetime
    from dateutil.parser import parse

    project_data = []
    current_date = datetime.datetime.now()
    project_elements = await page.query_selector_all("a.project-item-selector")
    for element in project_elements:
        project_name_elem = await element.query_selector("span.project-name")
        project_name = await project_name_elem.inner_text()
        project_url = await (await element.get_property("href")).json_value()
        updated_elem = await element.query_selector("span.project-updated")
        last_updated_text = await updated_elem.inner_text()
        last_updated_date = parse(last_updated_text)
        if current_date - datetime.timedelta(days=30) <= last_updated_date:
            project_data.append(
                {
                    "name": project_name,
                    "url": project_url,
                    "updated": last_updated_date.isoformat(),
                }
            )
    return project_data


async def retrieve_issue_resolution_statistics(page):
    """
    [Function description]
    Retrieves statistics of issue resolutions vs. open issues across repositories on the current page.

    This function automates the extraction of open issue counts and related merge request counts for each repository on the page. It calculates the ratio of resolved issues (considered as fulfilled merge requests) to open issues for each repository.

    [Usage preconditions]
    - The page must be on a GitLab dashboard or a similar page where repositories are listed with open issue and merge request counts visible.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "repository" (str): The name of the repository.
        - "open_issues" (int): The count of open issues in the repository.
        - "merge_requests" (int): The count of fulfilled merge requests in the repository.
        - "resolution_ratio" (float): The ratio of merge requests to open issues, indicating resolution effectiveness.
    """
    await page.goto("/dashboard/projects/starred")
    repositories = await page.query_selector_all("main h2")
    statistics = []
    for repo in repositories:
        repo_name_elem = await repo.query_selector("a")
        repo_name = await repo_name_elem.inner_text()
        open_issues_elem = await page.query_selector(
            f'a[href="{repo_name.strip()}/-/issues"]'
        )
        open_issues_count = (
            int(await open_issues_elem.inner_text()) if open_issues_elem else 0
        )
        merge_requests_elem = await page.query_selector(
            f'a[href="{repo_name.strip()}/-/merge_requests"]'
        )
        merge_requests_count = (
            int(await merge_requests_elem.inner_text()) if merge_requests_elem else 0
        )
        resolution_ratio = (
            merge_requests_count / open_issues_count
            if open_issues_count > 0
            else float("inf")
        )
        statistics.append(
            {
                "repository": repo_name.strip(),
                "open_issues": open_issues_count,
                "merge_requests": merge_requests_count,
                "resolution_ratio": resolution_ratio,
            }
        )
    return statistics


async def list_project_creation_methods(page):
    """
    [Function description]
    Lists all available project creation methods on the GitLab "New Project" page.

    This function collects information on the project creation methods available
    when starting a new project in GitLab. It extracts descriptions for each method
    and provides a comprehensive list of options available on the page.

    [Usage preconditions]
    - Ensure you are on the GitLab "New Project" page.
    - This function assumes you are navigating the GitLab UI where project creation options are displayed.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the project creation method.
        - "description" (str): The detailed description of what the project creation method entails.
    """
    await page.goto("/projects/new")
    project_creation_methods = []
    links = await page.query_selector_all("main a")
    for link in links:
        text = await link.inner_text()
        if "Create " in text:
            parts = text.split("Create ", 1)
            name = "Create " + parts[1].split()[0]
            description = (
                parts[1].split(" ", 1)[1] if len(parts[1].split(" ", 1)) > 1 else ""
            )
            project_creation_methods.append(
                {"name": name.strip(), "description": description.strip()}
            )
    return project_creation_methods


async def get_command_line_instructions_for_project_creation(page):
    """
    [Function description]
    Retrieves command-line instructions for project creation from the GitLab "New Project" page.

    This function automates the process of locating and interacting with the element
    that shows command-line instructions for project creation on the GitLab "New Project" page.
    It then collects the displayed command text.

    [Usage preconditions]
    - You must already be on the GitLab "New Project" page before calling this function.
    - The function expects the "Show command" option to be visible on the page.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    str
        The command-line instructions for project creation extracted from the page.
    """
    await page.goto("/projects/new")
    show_command_element = await page.query_selector('main a:has-text("Show command")')
    if show_command_element:
        await show_command_element.click()
        command_text_element = await page.query_selector(".command-text")
        if command_text_element:
            command_text = await command_text_element.inner_text()
            return command_text
    return


async def analyze_project_import_options(page):
    """
    Analyzes project import options available in GitLab and retrieves their descriptions and URLs.

    This function automates the process of extracting information about project import options
    from a GitLab page. It finds all the relevant links that describe different methods to import
    projects, including importing from external sources like GitHub, Bitbucket, etc.

    Usage preconditions:
    - You should already be on the "New Project" page on GitLab before calling this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains details about a project import option:
        - "description" (str): The descriptive text of the import option.
        - "url" (str): The hyperlink reference associated with the import option.
    """
    await page.goto("/projects/new")
    import_options = []
    import_links_selector = 'main a[href^="#import_project"]'
    import_links = await page.query_selector_all(import_links_selector)
    for link in import_links:
        description = await (await link.get_property("textContent")).json_value()
        url_property = await link.get_property("href")
        url = await url_property.json_value()
        import_options.append({"description": description.strip(), "url": url})
    return import_options


async def extract_repository_names_and_star_counts(page):
    """
    [Function description]
    Extracts all repository names and their star counts from the current webpage.

    This function automates the extraction of the names of repositories and their corresponding star counts from the
    webpage you are currently at. It navigates through the main content section of the page and gathers information
    related to each repository, including:

    - Repository name
    - Star count

    [Usage preconditions]
    - **You must already be on a webpage listing repositories** before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The repository name.
        - "stars" (int): The count of stars the repository has received.
    """
    await page.goto("/")
    repositories = []
    repo_headers = await page.query_selector_all("main h2.heading")
    for header in repo_headers:
        repo_name_link = await header.query_selector("a")
        repo_name = await (await repo_name_link).text_content().strip()
        star_link = await header.evaluate_handle(
            '(header) => header.nextElementSibling.querySelector("a")'
        )
        star_count_text = await (await star_link).text_content().strip()
        star_count = int(star_count_text)
        repositories.append({"name": repo_name, "stars": star_count})
    return repositories


async def identify_repos_with_zero_forks_issues(page):
    """
    Identifies repositories with zero forks and zero issues from the current GitLab dashboard.

    [Usage preconditions]
    - This function assumes that you are already on the GitLab projects dashboard page.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the repository.
        - "url" (str): The URL to access the repository.
    """
    await page.goto("/")
    zero_forks_issues_repos = []
    repository_elements = await page.query_selector_all("main heading.level-2")
    for repo in repository_elements:
        repo_name = await (await repo.query_selector("a")).inner_text()
        repo_url = await (await repo.query_selector("a")).get_attribute("href")
        forks_element = await page.query_selector(f'a[href="{repo_url}/-/forks"]')
        forks_count = int(await forks_element.inner_text())
        issues_element = await page.query_selector(f'a[href="{repo_url}/-/issues"]')
        issues_count = int(await issues_element.inner_text())
        if forks_count == 0 and issues_count == 0:
            zero_forks_issues_repos.append({"name": repo_name, "url": repo_url})
    return zero_forks_issues_repos


async def extract_repos_and_descriptions(page):
    """
    Extracts all repository names and their descriptions from the current GitLab dashboard page.

    [Function description]
    This function automates the process of extracting repository names and their descriptions from a GitLab user's dashboard.
    Specifically, it gathers information shown for each repository, including repository name and its description, as structured on the dashboard.

    [Usage preconditions]
    - You must already be on a GitLab dashboard page listing multiple repositories.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following key:
        - "name" (str): The name of the repository.
    """
    await page.goto("/?personal=true&sort=name_asc")
    repo_data = []
    repo_elements = await page.query_selector_all("h2 > a")
    for repo_element in repo_elements:
        repo_name = await repo_element.inner_text()
        repo_data.append({"name": repo_name})
    return repo_data


async def retrieve_project_update_times(page):
    """
    Retrieves update times for each project listed on the current GitLab dashboard page.

    This function fetches the project names and their last update times displayed on the current
    GitLab dashboard page. It returns a structured list of this information.

    [Usage preconditions]
    - You must be on a GitLab dashboard page with a list of project entries.

    Args:
    page : A Playwright `Page` instance to fetch information from the current browser page.

    Returns:
    list of dict
        A list of dictionaries where each dictionary represents a project with:
        - "project_name" (str): The name of the project.
        - "update_time" (str): The last update time of the project listed on the page.
    """
    await page.goto("/?personal=true&sort=name_asc")
    projects_info = []
    project_elements = await page.query_selector_all("h2.project-item-heading")
    for project_element in project_elements:
        project_name_element = await project_element.query_selector("a")
        project_name = await project_name_element.inner_text()
        update_time_element = await project_element.query_selector("time")
        update_time = await update_time_element.get_attribute("datetime")
        projects_info.append({"project_name": project_name, "update_time": update_time})
    return projects_info


async def list_projects_by_owner(page):
    """
    [Function description]
    Retrieves a list of projects owned by the currently viewed owner on a GitLab projects dashboard.

    This function automates the extraction of project details from a GitLab dashboard. It collects
    information about each project owned by the currently viewed owner, including:

    - Project name
    - Project URL

    [Usage preconditions]
    - This API retrieves project information from a user's GitLab dashboard.
    - **You must already be on the GitLab user's project dashboard page before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the project (including the owner).
        - "url" (str): The relative URL to the project page.
    """
    await page.goto("/?personal=true&sort=name_asc")
    projects = []
    project_elements = await page.query_selector_all("main .heading a")
    for project_element in project_elements:
        name = await (await project_element.get_property("innerText")).json_value()
        url = await (await project_element.get_property("href")).json_value()
        projects.append({"name": name, "url": url})
    return projects


async def extract_all_repository_information(page):
    """
    [Function description]
    Extracts comprehensive information from each repository listed on a GitLab dashboard or similar page.

    This function automates the extraction of detailed repository information including:
    - Repository name
    - Owner (role)
    - Description
    - URL
    - Engagement metrics: stars, forks, merge requests, and issues

    [Usage preconditions]
    - The Playwright Page object must be on a GitLab dashboard or equivalent page listing repositories.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the repository.
        - "owner" (str): The owner/role of the repository.
        - "description" (str): A short description of the repository.
        - "url" (str): The URL to the repository.
        - "stars" (int): The number of stars the repository has.
        - "forks" (int): The number of forks.
        - "merge_requests" (int): The number of open merge requests.
        - "issues" (int): The number of open issues.
    """
    await page.goto("/")
    repositories = []
    repo_selectors = await page.query_selector_all("main h2:has(a)")
    for repo in repo_selectors:
        name_element = await repo.query_selector("a")
        name = await (await name_element.get_property("innerText")).json_value()
        url = await (await name_element.get_property("href")).json_value()
        owner_element = await repo.query_selector("a > span")
        owner_role = (
            await (await owner_element.get_property("title")).json_value()
            if owner_element
            else "Unknown"
        )
        description_element = await repo.query_selector("p")
        description = (
            await (await description_element.get_property("innerText")).json_value()
            if description_element
            else "No description"
        )
        stars_element = await repo.query_selector('a[href$="/-/starrers"]')
        stars = (
            int(await (await stars_element.get_property("innerText")).json_value())
            if stars_element
            else 0
        )
        forks_element = await repo.query_selector('a[href$="/-/forks"]')
        forks = (
            int(await (await forks_element.get_property("innerText")).json_value())
            if forks_element
            else 0
        )
        merge_requests_element = await repo.query_selector(
            'a[href$="/-/merge_requests"]'
        )
        merge_requests = (
            int(
                await (
                    await merge_requests_element.get_property("innerText")
                ).json_value()
            )
            if merge_requests_element
            else 0
        )
        issues_element = await repo.query_selector('a[href$="/-/issues"]')
        issues = (
            int(await (await issues_element.get_property("innerText")).json_value())
            if issues_element
            else 0
        )
        repositories.append(
            {
                "name": name,
                "url": url,
                "owner": owner_role,
                "description": description,
                "stars": stars,
                "forks": forks,
                "merge_requests": merge_requests,
                "issues": issues,
            }
        )
    return repositories


async def list_active_repositories(page):
    """
    [Function description]
    Identifies the repositories updated within the last year.

    This function goes through the repositories on the current page and determines
    which ones have been updated within the last year. It helps to identify currently active projects.

    [Usage preconditions]
    - You must be on a page listing repositories before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "repository_name" (str): The name of the repository.
        - "last_updated" (str): The timestamp of the last update.
    """
    await page.goto("/?personal=true&sort=name_asc")
    active_repositories = []
    repo_elements = await page.query_selector_all("h2 a")
    from datetime import datetime, timedelta

    one_year_ago = datetime.utcnow() - timedelta(days=365)
    for repo_element in repo_elements:
        repo_name = await repo_element.text_content()
        repo_list_item = await repo_element.query_selector("..")
        last_updated_element = await repo_list_item.query_selector(
            "relative time.js-timeago"
        )
        last_updated_text = None
        if last_updated_element:
            last_updated_text = await last_updated_element.get_attribute("datetime")
        if last_updated_text:
            last_updated_date = datetime.fromisoformat(
                last_updated_text.replace("Z", "+00:00")
            )
            if last_updated_date >= one_year_ago:
                active_repositories.append(
                    {"repository_name": repo_name, "last_updated": last_updated_text}
                )
    return active_repositories


async def get_repos_with_high_issue_count(page, threshold):
    """
    [Function description]
    Identifies repositories with an issue count higher than a specified threshold on the current page.

    This function scans through repositories listed on the current GitLab dashboard page,
    checking the number of issues each repository has and returning those that exceed
    the given threshold, highlighting potential development or maintenance bottlenecks.

    [Usage preconditions]
    - You must be logged into your GitLab account and be on the dashboard project page
      before calling this function.

    Args:
    page : A Playwright `Page` instance for controlling browser automation.
    threshold : An integer representing the minimum number of issues a repository must have
                 to be included in the results.

    Returns:
    list of str
        A list of repository names that have more than the specified number of issues.
    """
    await page.goto("/?personal=true&sort=name_asc")
    repos_with_high_issues = []
    repo_elements = await page.query_selector_all("h2 > a")
    issue_links = await page.query_selector_all('a[href*="/-/issues"]')
    for repo_element, issue_link in zip(repo_elements, issue_links):
        repo_name = await repo_element.inner_text()
        issue_count_text = await issue_link.inner_text()
        issue_count = int(issue_count_text)
        if issue_count > threshold:
            repos_with_high_issues.append(repo_name)
    return repos_with_high_issues


async def list_forked_projects(page):
    """
    Identifies repositories that have been forked on a GitLab Dashboard page to analyze their popularity and collaboration metrics.

    This function automates the search for repositories that have been forked. It collects information on each repository including:
    - Repository name
    - Number of forks

    [Usage preconditions]
    - The page must be a GitLab repository dashboard list page, featuring a set of projects.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys for repositories with forks:
        - "name" (str): The name of the repository.
        - "forks" (int): The number of times the repository has been forked.
    """
    await page.goto("/")
    forked_projects = []
    repo_elements = await page.query_selector_all("div.project-container")
    for repo_element in repo_elements:
        name_handle = await repo_element.query_selector("h2 a")
        repo_name = await (await name_handle.inner_text()) if name_handle else None
        fork_link = await repo_element.query_selector('a[href$="/forks"]')
        forks_text = await (await fork_link.inner_text()) if fork_link else "0"
        forks_count = int(forks_text)
        if forks_count > 0:
            forked_projects.append({"name": repo_name, "forks": forks_count})
    return forked_projects


async def list_projects_with_open_merge_requests(page):
    """
    [Function description]
    Identifies and lists all projects that have open merge requests along with the count of these requests.

    This function automates the extraction of project names and the number of open merge requests
    from the dashboard page. It finds all projects with open requests and collects this information.

    [Usage preconditions]
    - You must already be on the GitLab dashboard page that lists projects.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the project.
        - "open_merge_requests" (int): The count of open merge requests.
    """
    await page.goto("/dashboard/projects/starred")
    projects = []
    project_elements = await page.query_selector_all("h2 > a")
    for project_name_element in project_elements:
        project_name = await project_name_element.inner_text()
        merge_request_link_xpath = "xpath=ancestor::div/following-sibling::a[contains(@href, '/merge_requests')]"
        merge_requests_link = await project_name_element.query_selector(
            merge_request_link_xpath
        )
        if merge_requests_link:
            merge_request_count_text = await merge_requests_link.inner_text()
            merge_request_count = int(merge_request_count_text.strip())
            if merge_request_count > 0:
                projects.append(
                    {"name": project_name, "open_merge_requests": merge_request_count}
                )
    return projects


async def extract_unmaintained_projects(page):
    """
    [Function description]
    Identifies projects that haven't been updated for more than a year from the current GitLab dashboard page.

    This function scans the projects listed on the dashboard and extracts the last updated date for each project. Projects that have not been updated for more than a year are identified as potentially unmaintained or deprecated.

    [Usage preconditions]
    - This function must be called from a Playwright `page` instance that is currently displaying a GitLab dashboard page listing projects.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "project_name" (str): The name of the project.
        - "last_updated" (str): The last updated date of the project.
    """
    await page.goto("/dashboard/projects/starred")
    from datetime import datetime, timedelta

    project_selectors = await page.query_selector_all("div.project-row")
    unmaintained_projects = []
    now = datetime.now()
    one_year_ago = now - timedelta(days=365)
    for project_selector in project_selectors:
        name_selector = await project_selector.query_selector("h2.project-name")
        last_updated_selector = await project_selector.query_selector(
            "time.last-updated"
        )
        project_name = await name_selector.inner_text() if name_selector else "Unknown"
        last_updated_str = (
            await last_updated_selector.inner_text()
            if last_updated_selector
            else "Unknown"
        )
        if last_updated_str != "Unknown":
            last_updated_date = datetime.strptime(last_updated_str, "%Y-%m-%d")
            if last_updated_date < one_year_ago:
                unmaintained_projects.append(
                    {"project_name": project_name, "last_updated": last_updated_str}
                )
    return unmaintained_projects


async def extract_project_descriptions(page):
    """
    [Function description]
    Compiles a summary of all project descriptions shown on the dashboard. This includes titles and URLs of each project.

    [Usage preconditions]
    - You must already be on a GitLab dashboard page displaying the projects.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "title" (str): The title of the project.
        - "url" (str): The relative URL of the project.
    """
    await page.goto("/dashboard/projects/starred")
    project_elements = await page.query_selector_all("h2 a")
    projects = []
    for project_element in project_elements:
        title = await project_element.inner_text()
        url = await project_element.get_attribute("href")
        projects.append({"title": title, "url": url})
    return projects


async def extract_project_info(page):
    """
    Extract all project names, descriptions, owners/roles, and their URLs from the dashboard page.

    This function automates the extraction of project overview information from a GitLab dashboard page,
    providing comprehensive details of each listed project including:

    - Project name
    - Project URL

    [Usage preconditions]
    - You must already be on a GitLab dashboard page listing multiple projects.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the project.
        - "url" (str): The URL to the project page.
    """
    await page.goto("/")
    projects = []
    project_elements = await page.query_selector_all("main .heading > a")
    for element in project_elements:
        name = await (await element.inner_text()).strip()
        url = await (await element.get_attribute("href"))
        projects.append({"name": name, "url": url})
    return projects



async def get_sorted_repositories_by_star(page):
    """
    [Function description]
    Identifies and lists repositories sorted by their star count to determine which are
    most popular and those with zero stars.

    The function navigates through the existing list of repositories on the page.
    It extracts the number of stars and the name of each repository, sorts them
    by star count, and identifies repositories with zero stars.

    [Usage preconditions]
    - **You must already be on a page that lists multiple repositories** with their star count visible.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    dict
        A dictionary containing the sorted repositories in two categories:
        - "most_popular": List of tuples for repositories sorted by descending star count.
        - "zero_stars": List of repository names with zero stars.
    """
    await page.goto("/")
    repos = await page.query_selector_all("main > heading")
    repo_data = []
    zero_star_repos = []
    for repo in repos:
        repo_name_element = await page.query_selector("a", within=repo)
        stars_element = await page.query_selector('a[href*="starrers"]', within=repo)
        repo_name = await repo_name_element.inner_text()
        stars_text = await stars_element.inner_text()
        stars_count = int(stars_text)
        if stars_count == 0:
            zero_star_repos.append(repo_name)
        else:
            repo_data.append((repo_name, stars_count))
    most_popular_repos = sorted(repo_data, key=lambda x: x[1], reverse=True)
    return {"most_popular": most_popular_repos, "zero_stars": zero_star_repos}


async def navigate_to_explore_page(page):
    """
    Navigate to the Explore page on GitLab.

    This function automates the process of navigating from the main dashboard to the 'Explore' page, where users can
    discover various projects and repositories available on GitLab. It locates the 'Explore' link within the main
    content section and performs a click action to navigate to the desired page.

    Usage Log:
    - Successfully navigated to the Explore page from the GitLab dashboard.

    Arguments:
    page: A Playwright page object representing the browser page.

    Expected Outcome:
    - The function successfully navigates to the 'Explore' section on GitLab.
    """
    await page.goto("/")
    await page.get_by_role("link", name="Explore").click()


async def get_repositories_by_star_count_descending(page):
    """
    [Function description]
    Retrieves and lists GitLab repositories with the highest number of stars in descending order from the explore page.

    This function navigates through the GitLab explore page, gathering information about each repository's star count.
    It then sorts the repositories based on star count in descending order.

    [Usage preconditions]
    - You must already be on the GitLab explore repositories page before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the repository.
        - "stars" (int): The number of stars the repository has.
    """
    await page.goto("/explore")
    repo_elements = await page.query_selector_all("h2 a")
    star_elements = await page.query_selector_all('a[href$="/-/starrers"]')
    repos = []
    for repo_elem, star_elem in zip(repo_elements, star_elements):
        repo_name_element = await repo_elem.get_property("innerText")
        repo_name = await repo_name_element.json_value()
        star_count_element = await star_elem.get_property("innerText")
        star_count = int(await star_count_element.json_value())
        repos.append({"name": repo_name.strip(), "stars": star_count})
    sorted_repos = sorted(repos, key=lambda x: x["stars"], reverse=True)
    return sorted_repos


async def get_repositories_with_most_open_issues(page):
    """
    Retrieves and sorts repository information based on the number of open issues from a GitLab Explore Projects page.

    This function extracts the names and open issue counts for each repository listed on the page and returns
    a list of the repositories sorted by their open issues count.

    [Usage preconditions]
    - The caller must already be on the Explore Projects page in GitLab.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "repo_name" (str): The name of the repository.
        - "open_issues" (int): The number of open issues for the repository.
        - "url" (str): URL of the issues page of the repository.
    """
    await page.goto("/explore")
    repo_data = []
    repo_elements = await page.query_selector_all("h2.heading a")
    for repo_element in repo_elements:
        repo_name = await (await repo_element.get_property("textContent")).json_value()
        issue_link = await page.query_selector(f"a[href*='{repo_name}']").next_sibling()
        open_issues_text = await (
            await issue_link.get_property("textContent")
        ).json_value()
        open_issues = int(open_issues_text)
        url = await (await issue_link.get_property("href")).json_value()
        repo_data.append(
            {"repo_name": repo_name.strip(), "open_issues": open_issues, "url": url}
        )
    repo_data.sort(key=lambda r: r["open_issues"], reverse=True)
    return repo_data


async def fetch_all_repositories_engagement_metrics(page):
    """
    [Function description]
    Retrieves a list of all repositories with their detailed engagement metrics including stars, forks, merge requests, and issues from the current page.

    This function automates the extraction of engagement metrics for each repository listed on the page.
    It collects data necessary for gauging repository activity and involvement based on relevant metrics.

    [Usage preconditions]
    - You must already be on a page that lists repositories (such as GitLab's explore page for projects) before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries containing the following keys for each repository:
        - "name" (str): The name of the repository.
        - "stars" (int): The number of stars for the repository.
        - "forks" (int): The number of forks.
        - "merge_requests" (int): The number of merge requests.
        - "issues" (int): The number of issues.
    """
    await page.goto("/explore")
    repo_elements = await page.query_selector_all("main h2.heading")
    repositories = []
    for repo_element in repo_elements:
        name_element = await repo_element.query_selector("a")
        name = await name_element.inner_text()
        starrers_element = await page.query_selector(
            f"a[href='{await name_element.get_attribute('href')}/-/starrers']"
        )
        stars = int(await starrers_element.inner_text())
        forks_element = await page.query_selector(
            f"a[href='{await name_element.get_attribute('href')}/-/forks']"
        )
        forks = int(await forks_element.inner_text())
        merge_requests_element = await page.query_selector(
            f"a[href='{await name_element.get_attribute('href')}/-/merge_requests']"
        )
        merge_requests = int(await merge_requests_element.inner_text())
        issues_element = await page.query_selector(
            f"a[href='{await name_element.get_attribute('href')}/-/issues']"
        )
        issues = int(await issues_element.inner_text())
        repository_info = {
            "name": name,
            "stars": stars,
            "forks": forks,
            "merge_requests": merge_requests,
            "issues": issues,
        }
        repositories.append(repository_info)
    return repositories


async def get_repositories_with_no_stars(page):
    """
    Identify and list repositories without any stars from the current GitLab Explore page.

    [Usage preconditions]
    - **You must already be on the GitLab Explore page listing various repositories.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list
        A list of repository names (str) that have no stars.
    """
    await page.goto("/explore")
    repositories_with_no_stars = []
    repo_elements = await page.query_selector_all("h2 a")
    for repo_element in repo_elements:
        repo_name = await repo_element.inner_text()
        star_url = await repo_element.evaluate("a => a.href + '/-starrers'")
        star_count_element = await page.query_selector(f'a[href="{star_url}"]')
        if star_count_element:
            star_count_text = await star_count_element.inner_text()
            if star_count_text.strip() == "0":
                repositories_with_no_stars.append(repo_name)
    return repositories_with_no_stars


async def extract_recently_updated_repositories(page):
    """
    Extracts repository links and names that have been updated within the last year.

    This function scrapes the current page to find repositories that were updated within
    the last year. It retrieves pertinent details for each, such as:

    - Repository name and link

    Usage preconditions:
    - The page is expected to be an explore or similar page listing multiple repositories
      with a last update timeframe visible.

    Args:
    page : A Playwright `Page` instance currently at an explore listing page.

    Returns:
    list of dict
        A list of dictionaries containing:
        - "name" (str): The name of the repository.
        - "link" (str): The link to the repository.
    """
    await page.goto("/explore")
    repositories = []
    repo_elements = await page.query_selector_all("div.project-row")
    for repo in repo_elements:
        last_updated_handle = await repo.query_selector("span.last-updated-time")
        if last_updated_handle:
            last_updated_text = await (
                await last_updated_handle.get_property("textContent")
            ).json_value()
            if "year" not in last_updated_text:
                repo_name_handle = await repo.query_selector("a.project-name")
                repo_link_handle = await repo.query_selector("a.project-link")
                repo_name = await (
                    await repo_name_handle.get_property("textContent")
                ).json_value()
                repo_link = await (
                    await repo_link_handle.get_property("href")
                ).json_value()
                repositories.append(
                    {"name": repo_name.strip(), "link": repo_link.strip()}
                )
    return repositories


async def collect_repo_engagement_metrics(page):
    """
    [Function description]
    Collects detailed engagement metrics for all repositories listed on
    the current GitLab explore page. This function extracts comprehensive
    engagement statistics, including stars, forks, merge requests, and issues,
    for each repository visible on the page.

    [Usage preconditions]
    - You must be on the GitLab explore page, where repositories are listed.
    - The page layout should present repositories along with their associated metrics.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the repository.
        - "stars" (int): Number of stars on the repository.
        - "forks" (int): Number of forks of the repository.
        - "merge_requests" (int): Number of merge requests on the repository.
        - "issues" (int): Number of issues of the repository.
    """
    await page.goto("/explore")
    repo_metrics = []
    repo_items = await page.query_selector_all("h2.project-full-name")
    for item in repo_items:
        repo_name = await (await item.query_selector("a")).inner_text()
        metrics = {}
        metrics["stars"] = await (
            await item.query_selector('a[href$="/starrers"]')
        ).inner_text()
        metrics["forks"] = await (
            await item.query_selector('a[href$="/forks"]')
        ).inner_text()
        metrics["merge_requests"] = await (
            await item.query_selector('a[href$="/merge_requests"]')
        ).inner_text()
        metrics["issues"] = await (
            await item.query_selector('a[href$="/issues"]')
        ).inner_text()
        metrics_dict = {
            "name": repo_name.strip(),
            "stars": int(metrics["stars"].strip()),
            "forks": int(metrics["forks"].strip()),
            "merge_requests": int(metrics["merge_requests"].strip()),
            "issues": int(metrics["issues"].strip()),
        }
        repo_metrics.append(metrics_dict)
    return repo_metrics


async def list_repositories_sorted_by_last_update(page):
    """
    Extracts and sorts all repositories based on their last update time to help users identify the most recently active projects.

    This function automates the extraction of repository information from the GitLab "Explore Projects" page and gathers
    each repository's last update time directly from the explore page. The repositories are then sorted by this timestamp.

    Usage preconditions:
    - The function requires a user to already be on the "Explore Projects" page of GitLab where the list of repositories is visible.

    Args:
    page : A Playwright `Page` instance that is currently on the "Explore Projects" page.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "name" (str): The name of the repository.
        - "url" (str): The URL to the repository.
        - "last_updated" (str): The last updated timestamp in ISO 8601 format.
    """
    await page.goto("/explore")
    repository_elements = await page.query_selector_all("div.project-row")
    repos_data = []
    for repo_elem in repository_elements:
        repo_link = await repo_elem.query_selector('h2 a[href^="/"]')
        repo_name = await repo_link.inner_text()
        repo_url = await (await repo_link.get_property("href")).json_value()
        last_updated_element = await repo_elem.query_selector("relative-time")
        if last_updated_element:
            last_updated = await (
                await last_updated_element.get_property("innerText")
            ).json_value()
        else:
            last_updated = ""
        repos_data.append(
            {"name": repo_name, "url": repo_url, "last_updated": last_updated}
        )
    sorted_repos = sorted(repos_data, key=lambda x: x["last_updated"], reverse=True)
    return sorted_repos


async def filter_repositories_by_keyword(page, keyword):
    """
    [Function description]
    Filters repositories by a specified keyword and retrieves their details.

    This function uses the search functionality available on the GitLab explore page to filter repositories
    based on the provided keyword. It collects essential details for each filtered repository, including:

    - Repository name
    - Repository URL
    - Number of stars
    - Number of forks
    - Number of merge requests
    - Number of issues

    [Usage preconditions]
    - **You must already be on the GitLab explore page that lists projects**.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.
    keyword :  The keyword (string) to filter repositories by.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the repository.
        - "url" (str): The URL of the repository.
        - "stars" (int): The number of stars.
        - "forks" (int): The number of forks.
        - "merge_requests" (int): The number of merge requests.
        - "issues" (int): The number of issues.
    """
    await page.goto("/explore")
    search_box = await page.query_selector('input[placeholder="Filter by name"]')
    await search_box.fill(keyword)
    await search_box.press("Enter")
    repositories_details = []
    repositories = await page.query_selector_all("h2 > a")
    for repo in repositories:
        name = await repo.inner_text()
        url = await repo.get_attribute("href")
        stars = await (
            await page.query_selector(f'a[href="{url}/-/starrers"]')
        ).inner_text()
        forks = await (
            await page.query_selector(f'a[href="{url}/-/forks"]')
        ).inner_text()
        merge_requests = await (
            await page.query_selector(f'a[href="{url}/-/merge_requests"]')
        ).inner_text()
        issues = await (
            await page.query_selector(f'a[href="{url}/-/issues"]')
        ).inner_text()
        repositories_details.append(
            {
                "name": name,
                "url": url,
                "stars": int(stars),
                "forks": int(forks),
                "merge_requests": int(merge_requests),
                "issues": int(issues),
            }
        )
    return repositories_details


async def get_byte_blaze_project_details(page):
    """
    [Function description]
    Extracts comprehensive details of all projects owned or maintained by 'Byte Blaze', including complete metrics such as stars, forks, merge requests, issues, and update times.

    [Usage preconditions]
    - The function assumes the user is already on the 'Byte Blaze' projects dashboard on GitLab.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys for every project:
        - "name" (str): The name of the project.
        - "stars" (str): The number of stars the project has.
        - "forks" (str): The number of forks the project has.
        - "merge_requests" (str): The number of merge requests in the project.
        - "issues" (str): The number of issues the project has.
    """
    await page.goto("/")
    projects = []
    project_elements = await page.query_selector_all("h2.heading a")
    for project_element in project_elements:
        project_name = await project_element.inner_text()
        project_url = await project_element.get_attribute("href")
        stars = await (
            await page.query_selector(f"a[href='{project_url}/-/starrers']")
        ).inner_text()
        forks = await (
            await page.query_selector(f"a[href='{project_url}/-/forks']")
        ).inner_text()
        merge_requests = await (
            await page.query_selector(f"a[href='{project_url}/-/merge_requests']")
        ).inner_text()
        issues = await (
            await page.query_selector(f"a[href='{project_url}/-/issues']")
        ).inner_text()
        projects.append(
            {
                "name": project_name.strip(),
                "stars": stars.strip(),
                "forks": forks.strip(),
                "merge_requests": merge_requests.strip(),
                "issues": issues.strip(),
            }
        )
    return projects


async def extract_repository_engagement_metrics(page):
    """
    [Function description]
    Extracts detailed engagement metrics for all repositories listed on the current page.

    This function automates the retrieval of engagement metrics for each repository on the page.
    It collects information such as the number of starrers, forks, merge requests, and issues
    for each project listed.

    [Usage preconditions]
    - The function scrapes metrics for all repositories available on the **current GitLab explore page**.
    - **You must already be on the GitLab explore page listing multiple repositories.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "repo_name" (str): The full repository name including the owner and project name.
        - "starrers" (int): The number of stars the repository has.
        - "forks" (int): The number of forks the repository has.
        - "merge_requests" (int): The number of merge requests for the repository.
        - "issues" (int): The number of issues in the repository.
    """
    await page.goto("/explore")
    repo_data_list = []
    repo_elements = await page.query_selector_all("h2 > a[href]")
    for repo_element in repo_elements:
        repo_name = await repo_element.text_content()
        repo_url = await repo_element.get_attribute("href")
        starrers_selector = f"{repo_url}/-/starrers"
        forks_selector = f"{repo_url}/-/forks"
        merge_requests_selector = f"{repo_url}/-/merge_requests"
        issues_selector = f"{repo_url}/-/issues"
        starrers_element = await page.query_selector(f'a[href="{starrers_selector}"]')
        forks_element = await page.query_selector(f'a[href="{forks_selector}"]')
        merge_requests_element = await page.query_selector(
            f'a[href="{merge_requests_selector}"]'
        )
        issues_element = await page.query_selector(f'a[href="{issues_selector}"]')
        starrers = int(await starrers_element.text_content()) if starrers_element else 0
        forks = int(await forks_element.text_content()) if forks_element else 0
        merge_requests = (
            int(await merge_requests_element.text_content())
            if merge_requests_element
            else 0
        )
        issues = int(await issues_element.text_content()) if issues_element else 0
        repo_data_list.append(
            {
                "repo_name": repo_name.strip(),
                "starrers": starrers,
                "forks": forks,
                "merge_requests": merge_requests,
                "issues": issues,
            }
        )
    return repo_data_list


async def extract_maintainer_projects(page):
    """
    [Function description]
    Extracts project names where the current user is listed as the maintainer.
    This function identifies all projects displayed on the current page under sections that can contain maintainer marks.
    It assumes the presence of a differentiable identity for maintainer projects that can be navigatively accessed.

    [Usage preconditions]
    - This API assumes you are already on a GitLab dashboard or projects page showing user-involved projects.
    - Projects should have an indicator mentioning maintainer roles that is accessible without further navigation.

    Args:
    page : A Playwright `Page` instance for browser interaction.

    Returns:
    list of str
        A list of project names where the user is listed as a maintainer.
    """
    await page.goto("/")
    maintainer_projects = []
    project_elements = await page.query_selector_all(
        ".project-section[data-qa='maintainer']"
    )
    if project_elements:
        for project_element in project_elements:
            project_name_element = await project_element.query_selector(".project-name")
            project_name = (
                await (await project_name_element.text_content())
                if project_name_element
                else None
            )
            if project_name:
                maintainer_projects.append(project_name)
    return maintainer_projects


async def navigate_to_explore_topics_page(page):
    """
    Navigate to the Explore Topics page directly from the GitLab main dashboard.

    This function automates the process of navigating from the main dashboard to the 'Explore Topics' page, where various topics associated with projects can be explored.
    It directly locates and clicks the 'Topics' link within the main section.

    Usage Log:
    - Successfully navigated to the Explore Topics page from the GitLab dashboard.

    Arguments:
    page: A Playwright page object representing the browser page.

    Expected Outcome:
    - The function successfully navigates to the 'Explore Topics' section on GitLab.
    """
    await page.goto("/")
    await page.get_by_role("link", name="Topics").click()


async def extract_project_topics(page):
    """
    [Function description]
    Extracts all project topics available on the "Topics" page of the GitLab instance.

    This function automates the extraction of project topics listed on the current GitLab Topics page.

    [Usage preconditions]
    - This API function assumes that you are already on the GitLab Topics page where project topics are listed.
    - Ensure that a Topics page is opened in the controlled browser before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of str
        A list of project topics (str) extracted from the Topics page.
    """
    await page.goto("/explore/projects/topics")
    topics_elements = await page.query_selector_all("div.topic-card .topic-title")
    topics = []
    for element in topics_elements:
        topic_text = await element.inner_text()
        topics.append(topic_text)
    return topics


async def search_projects_by_topic(page, topic_keyword):
    """
    [Function description]
    Searches for projects related to a specific topic keyword using the search functionality on the GitLab explore topics page.

    This function automates the process of searching for projects associated with a specific topic by entering the keyword into the provided search input and extracting relevant project details from the search results.

    [Usage preconditions]
    - You must already be on the GitLab explore topics page before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    topic_keyword (str): The topic keyword to search for associated projects.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains project details such as:
        - "name" (str): The project name.
        - "description" (str): The project description.
    """
    await page.goto("/explore/projects/topics")
    await page.goto("/explore/projects/topics")
    search_box_selector = 'input[placeholder="Filter by name"]'
    search_box = await page.query_selector(search_box_selector)
    await search_box.fill(topic_keyword)
    await page.wait_for_timeout(1000)
    results = []
    project_elements = await page.query_selector_all(".gl-project")
    for project_element in project_elements:
        name_element = await project_element.query_selector("span.project-name")
        name = await name_element.inner_text() if name_element else "Unknown"
        description_element = await project_element.query_selector(
            "p.project-description"
        )
        description = (
            await description_element.inner_text()
            if description_element
            else "No description provided"
        )
        results.append({"name": name, "description": description})
    return results


async def navigate_to_explore_projects(page):
    """
    Navigate to the Explore Projects section on GitLab.

    This function facilitates the process of navigating from the main dashboard to the
    'Explore Projects' page on GitLab, where users can find various projects to explore.
    It achieves this by locating the 'Explore' link within the main content section and
    performing a click action.

    Usage Log:
    - Successfully navigated to the Explore Projects section using the available navigation link.

    Args:
    page: A Playwright page object representing the browser page.

    Expected Outcome:
    - The browser page should successfully display the 'Explore Projects' section on GitLab post-navigation.
    """
    await page.goto("/")
    await page.get_by_role("link", name="Explore").click()


async def navigate_gitlab_project_sections(page):
    """
    [Function description]
    Navigates through the GitLab Project Discovery sections including 'Yours', 'Starred', 'Explore', and 'Topics'.

    This function automates navigation through different sections present in the Project Discovery area of GitLab
    to allow users to explore and browse various project categories. It sequentially accesses the sections by clicking
    on their respective links.

    [Usage preconditions]
    - **You must already be on the GitLab Project Discovery page** before calling this function.
    - Ensure that you have necessary permissions and the sections are visible on the page.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    None
    """
    await page.goto("/explore/projects/topics")
    await page.locator('text="Yours"').click()
    await page.locator('text="Starred"').click()
    await page.locator('text="Explore"').click()
    await page.locator('text="Topics"').click()


async def search_projects_by_name(page, project_name):
    """
    [Function description]
    Filter projects by name using the 'Filter by name' field on the GitLab page.

    This function automates searching for projects by entering a specific name
    into the "Filter by name" field available on the page. It allows quick access
    to your own, starred, or explored projects by name.

    [Usage preconditions]
    - Ensure you are on the page which contains the project filter element.
    - The page should contain a 'Filter by name' input field for searching.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    project_name (str): The name of the project you want to search for.

    Returns:
    None: This function does not return any data but filters the project list.
    """
    await page.goto("/explore/projects/topics")
    await page.goto("/explore/projects/topics")
    search_box = page.locator('input[placeholder="Filter by name"]')
    await search_box.fill(project_name)


async def explore_topics_contribution(page):
    """
    [Function description]
    Explores topics for project categorization and discovery from the current GitLab Topics page.

    This function automates the navigation through the available topics on the GitLab Topics page. It aims to retrieve
    topic names and any relevant associated data to analyze how these topics help in categorizing and discovering projects.

    [Usage preconditions]
    - This API retrieves and analyzes topics for categorization from the GitLab **Topics page**.
    - **You must already be on the GitLab Topics page before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "topic_name" (str): The name of the topic.
        - "description" (str): Description or metadata about the topic if available.
    """
    await page.goto("/explore/projects/topics")
    topics_elements = await page.query_selector_all(".topics-list-item")
    topics_info = []
    for topic in topics_elements:
        topic_name_element = await topic.query_selector(".topic-name")
        description_element = await topic.query_selector(".topic-description")
        topic_name = await topic_name_element.inner_text() if topic_name_element else ""
        description = (
            await description_element.inner_text() if description_element else ""
        )
        topics_info.append({"topic_name": topic_name, "description": description})
    return topics_info


async def navigate_to_starred_projects_page(page):
    """
    Navigate to the starred projects page on GitLab from the dashboard.

    This function automates the process of clicking the 'Starred' link under the
    dashboard section of GitLab, which redirects the user to their starred project listings.

    Usage Log:
    - Successfully navigated to the starred projects page from the dashboard using the 'Starred' link.

    Args:
    page: A Playwright `Page` instance to control browser automation.

    Expected Outcome:
    - The function navigates to the 'Starred Projects' section on GitLab.
    """
    await page.goto("/")
    await page.get_by_role("link", name="Starred").click()


async def extract_starred_projects_info(page):
    """
    [Function description]
    Extracts information about starred projects from the GitLab dashboard.

    This function automates the extraction of named information and engagement
    metrics from the currently displayed starred projects on the GitLab dashboard.
    It gathers details such as:

    - Project name
    - Owner name
    - Stars count
    - Forks count
    - Merge requests count
    - Issues count

    [Usage preconditions]
    - You must be on the GitLab dashboard page showing starred projects before calling this function.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the project.
        - "owner" (str): The owner of the project.
        - "stars" (str): Count of stars the project has.
        - "forks" (str): Count of forks.
        - "merge_requests" (str): Count of merge requests.
        - "issues" (str): Count of issues.
    """
    await page.goto("/dashboard/projects/starred")
    projects_info = []
    projects = await page.query_selector_all("main heading.level-2")
    for project in projects:
        project_name_link = await project.query_selector("a")
        project_name = await (
            await project_name_link.get_property("textContent")
        ).json_value()
        owner_name, project_name = map(str.strip, project_name.split("/", 1))
        metrics = {}
        metrics_selectors = {
            "stars": 'a[href$="/-/starrers"]',
            "forks": 'a[href$="/-/forks"]',
            "merge_requests": 'a[href$="/-/merge_requests"]',
            "issues": 'a[href$="/-/issues"]',
        }
        for metric_name, selector in metrics_selectors.items():
            metric_element = await project.query_selector(selector)
            if metric_element:
                metric_value = await (
                    await metric_element.get_property("textContent")
                ).json_value()
                metrics[metric_name] = metric_value
            else:
                metrics[metric_name] = "0"
        projects_info.append(
            {
                "name": project_name,
                "owner": owner_name,
                "stars": metrics.get("stars", "0"),
                "forks": metrics.get("forks", "0"),
                "merge_requests": metrics.get("merge_requests", "0"),
                "issues": metrics.get("issues", "0"),
            }
        )
    return projects_info


async def filter_and_retrieve_project_details(page, keyword):
    """
    [Function description]
    Filters projects based on a specific keyword using the 'Filter by name' search box
    and retrieves filtered project details such as name, owner, and engagement metrics like starrers, forks, merge requests, and issues.

    [Usage preconditions]
    - Ensure you are already on a GitLab dashboard or projects listing page that contains
    the 'Filter by name' search box.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    keyword : str
        The keyword to filter projects by name.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the project.
        - "owner" (str): The owner of the project.
        - "starrers" (int): The number of starrers.
        - "forks" (int): The number of forks.
        - "merge_requests" (int): The number of merge requests.
        - "issues" (int): The number of issues.
    """
    await page.goto("/dashboard/projects/starred")
    await page.fill('input[placeholder="Filter by name"]', keyword)
    project_sections = await page.query_selector_all("main h2.heading")
    projects = []
    for project_section in project_sections:
        name_link = await project_section.query_selector("a")
        name = await name_link.inner_text()
        owner = name.split(" / ")[0]
        starrers = int(
            await page.inner_text(f'h2:has-text("{name}") ~ a[href$="/starrers"]')
        )
        forks = int(await page.inner_text(f'h2:has-text("{name}") ~ a[href$="/forks"]'))
        merge_requests = int(
            await page.inner_text(f'h2:has-text("{name}") ~ a[href$="/merge_requests"]')
        )
        issues = int(
            await page.inner_text(f'h2:has-text("{name}") ~ a[href$="/issues"]')
        )
        projects.append(
            {
                "name": name,
                "owner": owner,
                "starrers": starrers,
                "forks": forks,
                "merge_requests": merge_requests,
                "issues": issues,
            }
        )
    return projects


async def get_projects_with_open_issues_over_30(page):
    """
    [Function description]
    Identifies projects that have more than 30 open issues.
    This function automates the extraction of projects and their open issues count, providing insights into which projects may have maintenance or development challenges.

    [Usage preconditions]
    - This API identifies projects with more than 30 open issues from the GitLab dashboard.
    - **You must already be on a GitLab dashboard page that lists the repositories before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "project_name" (str): The name of the project.
        - "open_issues" (int): The count of open issues.
    """
    await page.goto("/dashboard/projects/starred")
    projects_over_30_issues = []
    project_elements = await page.query_selector_all('div.main a[href*="/-/issues"]')
    for project_element in project_elements:
        project_name_element = await (
            await project_element.query_selector("previous-sibling::a")
        ).inner_text()
        issues_count_text = await project_element.inner_text()
        issues_count = int(issues_count_text)
        if issues_count > 30:
            projects_over_30_issues.append(
                {"project_name": project_name_element, "open_issues": issues_count}
            )
    return projects_over_30_issues


async def retrieve_starred_projects_info(page):
    """
    [Function description]
    Extracts details of all projects under the starred section on the current page.

    This function automates the extraction of project details from the starred projects section. It gathers information about each starred project, including:
    - Project name
    - Owner role
    - Star count
    - Fork count
    - Merge request count
    - Issue count

    [Usage preconditions]
    - **You must already be on the GitLab dashboard page with the starred projects section visible.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys for each starred project:
        - "name" (str): The name of the project.
        - "owner_role" (str): The role of the project owner.
        - "stars" (int): The number of stars.
        - "forks" (int): The number of forks.
        - "merge_requests" (int): The number of merge requests.
        - "issues" (int): The number of issues.
    """
    await page.goto("/dashboard/projects/starred")
    starred_section = await page.query_selector("main")
    project_headers = await starred_section.query_selector_all("h2")
    project_info = []
    for header in project_headers:
        project_link = await header.query_selector("a")
        name = await project_link.inner_text()
        owner_role = name.split(" / ")[0]
        stat_links = await header.evaluate_handle(
            'header => Array.from(header.parentNode.querySelectorAll("a")).slice(1)'
        )
        stats_text = await page.evaluate(
            "links => links.map(link => link.innerText)", stat_links
        )
        stats = list(map(int, filter(str.isdigit, stats_text)))
        stars, forks, merge_requests, issues = (stats + [0] * 4)[:4]
        project_info.append(
            {
                "name": name.strip(),
                "owner_role": owner_role.strip(),
                "stars": stars,
                "forks": forks,
                "merge_requests": merge_requests,
                "issues": issues,
            }
        )
    return project_info


async def extract_recently_updated_projects(page):
    """
    [Function description]
    Extracts details of projects that have been updated within the last year from the current dashboard page in GitLab.

    This function automates the identification of active projects based on their last update timestamps present on the dashboard page.
    It collects information about each project and checks if it was updated within a year from the current date.
    Information gathered:
    - Project name
    - Project URL
    - Last updated timestamp

    [Usage preconditions]
    - You need to be on the GitLab dashboard page displaying the projects list.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The project name.
        - "url" (str): The URL of the project on GitLab.
        - "last_updated" (str): The timestamp of the last update.
    """
    await page.goto("/dashboard/projects/starred")
    project_entries = await page.query_selector_all("h2")
    recent_projects = []
    from datetime import datetime, timedelta

    one_year_ago = datetime.now() - timedelta(days=365)
    for entry in project_entries:
        project_link_element = await entry.query_selector("a")
        last_updated_element = await entry.query_selector("time")
        if project_link_element and last_updated_element:
            project_name = await (
                await project_link_element.get_property("textContent")
            ).json_value()
            project_url = await (
                await project_link_element.get_property("href")
            ).json_value()
            last_updated_text = await (
                await last_updated_element.get_property("dateTime")
            ).json_value()
            last_updated_date = datetime.fromisoformat(last_updated_text)
            if last_updated_date > one_year_ago:
                recent_projects.append(
                    {
                        "name": project_name.strip(),
                        "url": project_url.strip(),
                        "last_updated": last_updated_text.strip(),
                    }
                )
    return recent_projects


async def search_projects_by_keyword(page, keyword):
    """
    [Function description]
    Searches projects by a keyword using the 'Filter by name' search box and retrieves filtered project details.

    [Usage preconditions]
    - You must be on a page with a 'Filter by name' search box for projects.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    keyword : A string keyword to search for projects by name.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains project details such as:
        - "name" (str): The name of the project.
        - "url" (str): URL leading to the project page.
    """
    await page.goto("/dashboard/projects/starred")
    search_box_locator = page.locator('input[placeholder="Filter by name"]')
    await search_box_locator.fill(keyword)
    project_elements = page.locator('main h2 a[href^="/"]')
    projects = []
    project_count = await project_elements.count()
    for i in range(project_count):
        project_element = project_elements.nth(i)
        project_name = await project_element.inner_text()
        project_url = await project_element.get_attribute("href")
        projects.append({"name": project_name, "url": project_url})
    return projects


async def extract_gitlab_dashboard_repository_details(page):
    """
    [Function description]
    Extracts detailed repository information from the GitLab dashboard page.
    This includes the repository's name, description, owner, URL, star count, fork count,
    merge requests, and issues for all repositories listed.

    [Usage preconditions]
    - This API function is designed to be used when you are already on the GitLab Dashboard page.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys for each repository:
        - "name" (str): The name of the repository.
        - "description" (str or None): The description of the repository.
        - "owner" (str): The owner's role or name of the repository.
        - "url" (str): The URL of the repository.
        - "stars" (int): The star count of the repository.
        - "forks" (int): The fork count of the repository.
        - "merge_requests" (int): The number of open merge requests.
        - "issues" (int): The number of open issues.
    """
    await page.goto("/dashboard/projects/starred")
    repos = await page.query_selector_all("h2:has(a)")
    repo_details = []
    for repo in repos:
        name_elem = await repo.query_selector("a")
        name = await name_elem.inner_text() if name_elem else ""
        parent_div = await repo.query_selector("xpath=ancestor::div[1]")
        description_elem = await parent_div.query_selector("p")
        description = await description_elem.inner_text() if description_elem else None
        owner = name.split("/")[0].strip()
        url = await name_elem.get_attribute("href") if name_elem else ""
        star_elem = await parent_div.query_selector("a[href*='starrers']")
        stars = int(await star_elem.inner_text()) if star_elem else 0
        fork_elem = await parent_div.query_selector("a[href*='forks']")
        forks = int(await fork_elem.inner_text()) if fork_elem else 0
        merge_requests_elem = await parent_div.query_selector(
            "a[href*='merge_requests']"
        )
        merge_requests = (
            int(await merge_requests_elem.inner_text()) if merge_requests_elem else 0
        )
        issues_elem = await parent_div.query_selector("a[href*='issues']")
        issues = int(await issues_elem.inner_text()) if issues_elem else 0
        repo_details.append(
            {
                "name": name,
                "description": description,
                "owner": owner,
                "url": url,
                "stars": stars,
                "forks": forks,
                "merge_requests": merge_requests,
                "issues": issues,
            }
        )
    return repo_details


async def identify_popular_repositories(page):
    """
    [Function description]
    Identifies and lists popular repositories based on their star counts in descending order from the current page.

    This function automates the process of extracting repository details from the current page
    and sorts them by the number of stars each repository has.
    It returns a list of repository names along with their star counts, sorted by star count.

    [Usage preconditions]
    - This API extracts and calculates popular repositories from the page **you are currently at**.
    - You must be on a page that lists repositories with their star counts.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "name" (str): The name of the repository.
        - "stars" (int): The number of stars the repository has.
    """
    await page.goto("/dashboard/projects/starred")
    repos = []
    repo_names_elements = await page.query_selector_all("h2 > a")
    repo_stars_elements = await page.query_selector_all('a[href$="/-/starrers"]')
    for name_element, stars_element in zip(repo_names_elements, repo_stars_elements):
        name = await name_element.inner_text()
        stars_text = await stars_element.inner_text()
        stars = int(stars_text.strip())
        repos.append({"name": name, "stars": stars})
    repos.sort(key=lambda repo: repo["stars"], reverse=True)
    return repos


async def get_sorted_repositories_by_open_issues(page):
    """
    [Function description]
    Identifies and sorts repositories by the number of open issues they have, listing the projects with the most open issues first.

    This function scrapes a GitLab projects page, where each project is associated with a number of open issues. It retrieves the names of the projects and the count of open issues, then sorts them in descending order by the number of issues.

    [Usage preconditions]
    - You must already be on a relevant GitLab projects list page before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A sorted list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the project.
        - "open_issues" (int): The number of open issues for the project.
    """
    await page.goto("/dashboard/projects/starred")
    project_elements = await page.query_selector_all(
        'a[data-qa-selector="project_item"]'
    )
    project_data = []
    for project in project_elements:
        name_element = await project.query_selector("h2 > a")
        name = await (await name_element.get_property("textContent")).json_value()
        issues_element = await project.query_selector('a[href$="/issues"]')
        issues_text = await (
            await issues_element.get_property("textContent")
        ).json_value()
        open_issues = int(issues_text.strip())
        project_data.append({"name": name.strip(), "open_issues": open_issues})
    sorted_projects = sorted(project_data, key=lambda x: x["open_issues"], reverse=True)
    return sorted_projects


async def navigate_to_personal_projects_page(page):
    """
    Navigate to the personal projects page on the GitLab dashboard.

    This function automates the interaction needed to click the 'Personal' link under the
    GitLab dashboard's main section, which redirects the user to their personal project listings.

    Usage Log:
    - Successfully navigated from the GitLab dashboard to the personal projects page by clicking the 'Personal' link.

    Arguments:
    page: A Playwright `Page` instance that controls browser automation.

    Expected Outcome:
    - The function navigates to the 'Personal Projects' section on GitLab.
    """
    await page.goto("/")
    await page.get_by_role("link", name="Personal").click()


async def identify_and_list_new_projects(page):
    """
    Identifies and lists newly created projects by checking for projects with no updates recorded in the past year but listed recently in personal projects.

    [Usage preconditions]
    - This API retrieves project information from the personal projects section on a page you are currently at.
    - You must already be on the page that lists personal projects before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the project.
        - "url" (str): The URL of the project.
    """
    await page.goto("/?personal=true&sort=name_asc")
    project_selectors = await page.query_selector_all('main div[heading][level="2"]')
    new_projects = []
    for project_selector in project_selectors:
        title_element = await project_selector.query_selector("link")
        title = await title_element.inner_text()
        url = await title_element.get_attribute("href")
        await page.goto(url)
        update_elements = await page.query_selector_all("time")
        has_recent_update = False
        for update_element in update_elements:
            update_time = await update_element.get_attribute("datetime")
        if not has_recent_update:
            new_projects.append({"name": title, "url": url})
    return new_projects


async def get_empty_repositories_info(page):
    """
    Extracts information on repositories with minimal or zero engagement metrics (zero starrers, forks, merge requests, and issues) from the current GitLab dashboard page.

    Usage preconditions:
    - The function must be called while on the GitLab project dashboard page.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary includes:
        - "name" (str): The name of the repository.
        - "starrers" (int): Number of starrers.
        - "forks" (int): Number of forks.
        - "merge_requests" (int): Number of merge requests.
        - "issues" (int): Number of issues.
    """
    await page.goto("/?personal=true&sort=name_asc")
    repositories = []
    repository_sections = await page.query_selector_all("main > heading.level-2")
    for section in repository_sections:
        name = await section.inner_text()
        metrics = section.evaluate(
            "section => Array.from(section.parentElement.querySelectorAll('a'), a => a.text)"
        )
        starrers, forks, merge_requests, issues = map(int, metrics)
        if starrers == 0 and forks == 0 and merge_requests == 0 and issues == 0:
            repositories.append(
                {
                    "name": name,
                    "starrers": starrers,
                    "forks": forks,
                    "merge_requests": merge_requests,
                    "issues": issues,
                }
            )
    return repositories


async def filter_projects_by_owner_Byte_Blaze(page):
    """
    [Function description]
    Filters and lists projects associated with the owner name 'Byte Blaze'.

    This function automates the filtering of projects based on a particular owner pattern 'Byte Blaze'. It examines multiple project entries on a page to document their involvement.

    [Usage preconditions]
    - You must be on a dashboard or page that displays multiple project listings with owner information.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list containing dictionaries with the project name and URL associated with 'Byte Blaze'.
    """
    await page.goto("/?personal=true&sort=name_asc")
    project_details = []
    project_selectors = 'h2:has-text("Byte Blaze") > a'
    project_elements = await page.query_selector_all(project_selectors)
    for project_element in project_elements:
        project_name = await project_element.inner_text()
        project_url = await project_element.get_attribute("href")
        project_details.append(
            {"name": project_name.strip(), "url": project_url.strip()}
        )
    return project_details


async def list_and_sort_repositories_by_stars(page):
    """
    [Function description]
    Identify and list all repositories by sorting them based on the star count in descending order.

    This function scrapes the current Explore Projects page on GitLab and retrieves information about each displayed repository, specifically:
    - Repository name
    - Number of stars

    The repositories are then sorted by their star count in descending order to highlight the most popular projects.

    [Usage preconditions]
    - Ensure you are currently on the GitLab Explore Projects page.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the repository.
        - "stars" (int): The star count of the repository.
    """
    await page.goto("/explore")
    repo_entries = await page.query_selector_all("h2.heading a")
    star_links = await page.query_selector_all('a[href*="/-/starrers"]')
    repositories = []
    for index, repo_entry in enumerate(repo_entries):
        repo_name = await repo_entry.inner_text()
        star_count_text = await star_links[index].inner_text()
        star_count = int(star_count_text)
        repositories.append({"name": repo_name, "stars": star_count})
    sorted_repositories = sorted(repositories, key=lambda x: x["stars"], reverse=True)
    return sorted_repositories


async def find_zero_engagement_repositories(page):
    """
    [Function description]
    Identify repositories on the current GitLab explore page that have zero stars, forks, and issues.

    This function automates the extraction of repository engagement details such as stars, forks, and issues.
    It then identifies and returns repositories that have no stars, no forks, and no issues, i.e., zero engagement.

    [Usage preconditions]
    - The page must be a GitLab project exploration list where multiple repositories' engagements can be extracted.
    - **You must already be on the GitLab explore page that lists repositories.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The full name of the repository (namespace + project name).
        - "url" (str): The URL to the repository's page.
    """
    await page.goto("/explore")
    repositories = []
    repo_elements = await page.query_selector_all("main > h2 > a")
    for repo_element in repo_elements:
        repo_name = await repo_element.inner_text()
        repo_url = await repo_element.get_attribute("href")
        stars_selector = f'a[href="{repo_url}/-/starrers"]'
        forks_selector = f'a[href="{repo_url}/-/forks"]'
        issues_selector = f'a[href="{repo_url}/-/issues"]'
        stars_element = await page.query_selector(stars_selector)
        forks_element = await page.query_selector(forks_selector)
        issues_element = await page.query_selector(issues_selector)
        if stars_element and forks_element and issues_element:
            stars_text = await stars_element.inner_text()
            forks_text = await forks_element.inner_text()
            issues_text = await issues_element.inner_text()
            stars = int(stars_text.strip()) if stars_text.strip().isdigit() else 0
            forks = int(forks_text.strip()) if forks_text.strip().isdigit() else 0
            issues = int(issues_text.strip()) if issues_text.strip().isdigit() else 0
            if stars == 0 and forks == 0 and issues == 0:
                repositories.append({"name": repo_name.strip(), "url": repo_url})
    return repositories


async def navigate_to_project_details_page(page, project_name):
    """
    Navigate to the Project Details page based on the provided project name.

    This function automates the process of locating and clicking the project link corresponding to the given project name,
    thereby navigating to its details page.

    Usage Log:
    - Successfully navigated to the details page of 'Byte Blaze / a11y-syntax-highlighting' from the GitLab dashboard.

    Args:
    page: A Playwright `Page` instance that controls browser automation.
    project_name: A string representing the name of the project to navigate to.

    Expected Outcome:
    - The function navigates to the specified project's details page.
    """
    await page.goto("/")
    await page.get_by_role("link", name=project_name).click()


async def extract_repository_metrics(page):
    """
    [Function description]
    Extracts a comprehensive list of all repositories displayed on the current page with
    their respective starrers, forks, merge requests, and issues. This holistic view helps
    users gauge project engagement metrics.

    [Usage preconditions]
    - The API can be utilized on pages that are structured like a repository exploration
      section on GitLab, listing various repositories.
    - The user must be on the page listing several repositories.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "name" (str): The name of the repository.
        - "url" (str): The hyperlink to the repository.
        - "starrers" (str): The number of starrers.
        - "forks" (str): The number of forks.
        - "merge_requests" (str): The number of merge requests.
        - "issues" (str): The number of issues.
    """
    await page.goto("/explore")
    repositories = []
    repo_elements = await page.query_selector_all("h2.heading")
    for repo_element in repo_elements:
        name_element = await repo_element.query_selector("a")
        name = await (await name_element.get_property("textContent")).json_value()
        url = await (await name_element.get_property("href")).json_value()
        metrics = {}
        metrics["name"] = name.strip()
        metrics["url"] = url
        starrers_element = await repo_element.query_selector(
            "xpath=./following-sibling::a[1]"
        )
        forks_element = await repo_element.query_selector(
            "xpath=./following-sibling::a[2]"
        )
        merge_requests_element = await repo_element.query_selector(
            "xpath=./following-sibling::a[3]"
        )
        issues_element = await repo_element.query_selector(
            "xpath=./following-sibling::a[4]"
        )
        starrers = await (
            await starrers_element.get_property("textContent")
        ).json_value()
        forks = await (await forks_element.get_property("textContent")).json_value()
        merge_requests = await (
            await merge_requests_element.get_property("textContent")
        ).json_value()
        issues = await (await issues_element.get_property("textContent")).json_value()
        metrics["starrers"] = starrers.strip()
        metrics["forks"] = forks.strip()
        metrics["merge_requests"] = merge_requests.strip()
        metrics["issues"] = issues.strip()
        repositories.append(metrics)
    return repositories


async def find_high_engagement_zero_forks_repos(page):
    """
    [Function description]
    Identifies and lists repositories with high engagement but zero forks.
    This function automates the extraction and filtering of repositories based
    on their engagement level (stars, merge requests, issues) and zero forks.
    It examines repositories on the explore page and returns those with no forks
    but have other engagement markers.

    [Usage preconditions]
    - You must already be on the GitLab "Explore" projects page before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries containing the details of each repository matching the criteria:
        - "name" (str): Name of the repository.
        - "stars" (int): Number of starrers.
        - "merge_requests" (int): Number of merge requests.
        - "issues" (int): Number of issues.
    """
    await page.goto("/explore")
    repos_with_engagement = []
    repo_entries = await page.query_selector_all("main div:has(h2)")
    for repo in repo_entries:
        name_elem = await repo.query_selector("h2 > a")
        if name_elem:
            name = await name_elem.inner_text()
            stars_elem = await repo.query_selector('a[href*="/starrers"]')
            forks_elem = await repo.query_selector('a[href*="/-/forks"]')
            merges_elem = await repo.query_selector('a[href*="/-/merge_requests"]')
            issues_elem = await repo.query_selector('a[href*="/-/issues"]')
            stars_count = int(await stars_elem.inner_text()) if stars_elem else 0
            forks_count = int(await forks_elem.inner_text()) if forks_elem else 0
            merges_count = int(await merges_elem.inner_text()) if merges_elem else 0
            issues_count = int(await issues_elem.inner_text()) if issues_elem else 0
            if forks_count == 0 and stars_count + merges_count + issues_count > 0:
                repos_with_engagement.append(
                    {
                        "name": name,
                        "stars": stars_count,
                        "merge_requests": merges_count,
                        "issues": issues_count,
                    }
                )
    return repos_with_engagement


async def retrieve_projects_with_zero_stars(page):
    """
    [Function description]
    Retrieves details of all projects on the current projects explore page, specifically focusing on those with zero stars.

    The function extracts project names and their star count, filtering out projects that have zero stars, highlighting them as areas for community engagement or discovery issues.

    [Usage preconditions]
    - This API retrieves project details for projects listed **on the current explore projects page**.
    - **You must already be on an explore projects page before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "project_name" (str): The name of the project.
        - "star_count" (int): The star count of the project, where count is zero.
    """
    await page.goto("/explore")
    projects_with_zero_stars = []
    project_elements = await page.query_selector_all("main > h2.heading")
    for project_element in project_elements:
        project_link = await project_element.query_selector("a")
        project_name = await (
            await project_link.get_property("textContent")
        ).json_value()
        star_link = await project_element.query_selector("a + a")
        star_count_text = await (
            await star_link.get_property("textContent")
        ).json_value()
        star_count = int(star_count_text.strip())
        if star_count == 0:
            projects_with_zero_stars.append(
                {"project_name": project_name.strip(), "star_count": star_count}
            )
    return projects_with_zero_stars


async def extract_file_commit_info(page):
    """
    [Function description]
    Extracts and lists all the files in a GitLab repository along with their respective last commit messages and update times.

    This function automates navigation through a GitLab repository file list and gathers details of each file's most recent commit
    message and the last update timestamp.

    [Usage preconditions]
    - This API retrieves file and commit information for the current GitLab repository page.
    - **You must already be on a GitLab project repository directory page before calling this function.**

    Args:
    page : A Playwright `Page` instance controlling the automation for this operation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "file_name" (str): The name of the file or directory.
        - "last_commit" (str): The message of the last commit.
        - "last_update" (str): The last update timestamp as a relative time description.

    """
    await page.goto("/byteblaze/a11y-webring.club")
    file_details = []
    rows = await page.query_selector_all(
        'table:has-text("Files, directories, and submodules") tr'
    )
    for row in rows[1:]:
        file_cell = await row.query_selector("td:nth-child(1)")
        commit_cell = await row.query_selector("td:nth-child(2)")
        update_cell = await row.query_selector("td:nth-child(3)")
        if file_cell and commit_cell and update_cell:
            file_name = await file_cell.inner_text()
            last_commit = await commit_cell.inner_text()
            last_update = await update_cell.inner_text()
            file_details.append(
                {
                    "file_name": file_name,
                    "last_commit": last_commit,
                    "last_update": last_update,
                }
            )
    return file_details


def is_recent_update(update_time):
    from datetime import datetime, timedelta

    update_datetime = datetime.strptime(update_time, "%Y-%m-%d")
    six_months_ago = datetime.now() - timedelta(days=6 * 30)
    return update_datetime >= six_months_ago


async def find_low_activity_projects(page):
    """
    [Function description]
    Identifies personal projects with less than 3 stars, forks, merge requests, and issues.

    This function automates the identification and extraction of the personal projects
    from the 'Projects' page on GitLab that have minimal activity based on criteria:
    - Stars: Less than 3
    - Forks: Less than 3
    - Merge requests: Less than 3
    - Issues: Less than 3

    [Usage preconditions]
    - You should already be on the 'Projects' page of GitLab where your list of personal projects is visible.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries, each containing 'name' (str) of the project that meets the criteria.
    """
    await page.goto("/?personal=true&sort=name_asc")
    projects = []
    project_elements = await page.query_selector_all(".project-card")
    for project in project_elements:
        project_name_elem = await project.query_selector("h2 > a")
        project_name = await project_name_elem.text_content()
        starrers_elem = await project.query_selector(".starrers-link")
        starrers_count = int(await starrers_elem.text_content())
        forks_elem = await project.query_selector(".forks-link")
        forks_count = int(await forks_elem.text_content())
        merge_requests_elem = await project.query_selector(".merge-requests-link")
        merge_requests_count = int(await merge_requests_elem.text_content())
        issues_elem = await project.query_selector(".issues-link")
        issues_count = int(await issues_elem.text_content())
        if all(
            count < 3
            for count in [
                starrers_count,
                forks_count,
                merge_requests_count,
                issues_count,
            ]
        ):
            projects.append({"name": project_name})
    return projects


async def filter_personal_projects_by_stars(page, min_stars):
    """
    [Function description]
    Filters and lists personal projects on the dashboard with more than a specified number of stars.

    This function scans personal projects on the GitLab dashboard and filters them based on a given
    minimum number of star ratings. Projects that meet or exceed this threshold will have their names
    and star counts compiled into a list of dictionaries.

    [Usage preconditions]
    - You must be already logged in and on the personal projects dashboard page on GitLab.

    Args:
    page : A Playwright `Page` instance that controls browser automation.
    min_stars : The minimum number of stars a project must have to be included in the result list.

    Returns:
    list of dict
        A list of dictionaries each containing the project name and number of stars for projects
        exceeding the specified threshold.
    """
    await page.goto("/?personal=true&sort=name_asc")
    project_list = []
    project_elements = await page.query_selector_all("h2:has-text('/ Byte Blaze /')")
    for project_element in project_elements:
        project_name = await project_element.inner_text()
        star_count_element = await project_element.evaluate_handle(
            "el => el.nextElementSibling.nextElementSibling"
        )
        star_count_text = await star_count_element.inner_text()
        star_count = int(star_count_text)
        if star_count >= min_stars:
            project_list.append({"name": project_name.strip(), "stars": star_count})
    return project_list


async def extract_repository_update_timelines(page):
    """
    [Function description]
    Extracts update timelines for all repositories listed on the current exploration page.

    This function automates the extraction of update details for each repository listed on a GitLab exploration page.
    It collects information including starrers, forks, merge requests, and issues for each repository.

    [Usage preconditions]
    - This function should be called when you are on an exploration page listing multiple repositories.
    - The page structure should contain sections for each repository with specific update links.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): Repository name and owner.
        - "starrers" (int): The number of starrers.
        - "forks" (int): The number of forks.
        - "merge_requests" (int): The number of merge requests.
        - "issues" (int): The number of issues.
    """
    await page.goto("/explore")
    repository_data = []
    repos = await page.query_selector_all("main > h2.heading")
    for repo in repos:
        temp_repo = {}
        repo_heading = await repo.query_selector("a")
        repo_name = await repo_heading.inner_text()
        temp_repo["name"] = repo_name
        starrers_link = await repo.query_selector("a[href$='-starrers']")
        starrers_text = await starrers_link.inner_text()
        temp_repo["starrers"] = int(starrers_text)
        forks_link = await repo.query_selector("a[href$='-forks']")
        forks_text = await forks_link.inner_text()
        temp_repo["forks"] = int(forks_text)
        merge_requests_link = await repo.query_selector("a[href$='-merge_requests']")
        merges_text = await merge_requests_link.inner_text()
        temp_repo["merge_requests"] = int(merges_text)
        issues_link = await repo.query_selector("a[href$='-issues']")
        issues_text = await issues_link.inner_text()
        temp_repo["issues"] = int(issues_text)
        repository_data.append(temp_repo)
    return repository_data


async def get_repositories_with_high_engagement(page):
    """
    [Function description]
    Extracts repository information including owner and engagement metrics.

    This function gathers comprehensive metrics information for each repository listed
    on the current page. It identifies repositories by ownership (e.g., Owner, Maintainer)
    and compiles their engagement metrics including:
    - Stars count
    - Forks count
    - Merge requests count
    - Issues count

    [Usage preconditions]
    - Ensure you are on a page listing repositories with their engagement metrics.

    Args:
    page : A Playwright `Page` instance for browser automation.

    Returns:
    list of dict
        A list of dictionaries with each containing:
        - "owner" (str): The owner of the repository.
        - "repo_name" (str): The name of the repository.
        - "stars" (int): The number of starrers.
        - "forks" (int): The number of forks.
        - "merge_requests" (int): The number of merge requests.
        - "issues" (int): The number of issues.
    """
    await page.goto("/explore")
    repos_with_metrics = []
    repo_elements = await page.query_selector_all("h2 > a")
    for repo_element in repo_elements:
        owner_and_repo = await (
            await repo_element.get_property("textContent")
        ).json_value()
        if " / " in owner_and_repo:
            owner, repo_name = map(str.strip, owner_and_repo.split(" / "))
            stars_count = await page.evaluate(
                "el => el.textContent",
                await page.query_selector(f'a[href="/{owner}/{repo_name}/-/starrers"]'),
            )
            forks_count = await page.evaluate(
                "el => el.textContent",
                await page.query_selector(f'a[href="/{owner}/{repo_name}/-/forks"]'),
            )
            merge_requests_count = await page.evaluate(
                "el => el.textContent",
                await page.query_selector(
                    f'a[href="/{owner}/{repo_name}/-/merge_requests"]'
                ),
            )
            issues_count = await page.evaluate(
                "el => el.textContent",
                await page.query_selector(f'a[href="/{owner}/{repo_name}/-/issues"]'),
            )
            repo_metrics = {
                "owner": owner,
                "repo_name": repo_name,
                "stars": int(stars_count.strip()),
                "forks": int(forks_count.strip()),
                "merge_requests": int(merge_requests_count.strip()),
                "issues": int(issues_count.strip()),
            }
            repos_with_metrics.append(repo_metrics)
    return repos_with_metrics


async def list_gitlab_repositories(page):
    """
    [Function description]
    Lists repositories from the Explore Projects section of GitLab with zero interaction.

    This function automates the extraction of repository details from the Explore Projects page
    of GitLab, gathering information about each repository presented on the current page, including:

    - Repository name
    - Count of starrers
    - Count of forks
    - Count of merge requests
    - Count of issues

    [Usage preconditions]
    - This API lists repository information on GitLab's Explore Projects page **you are currently at**.
    - **You must already be on the GitLab Explore Projects page for the repositories before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The repository name.
        - "starrers" (int): The count of starrers.
        - "forks" (int): The count of forks.
        - "merge_requests" (int): The count of merge requests.
        - "issues" (int): The count of issues.
    """
    await page.goto("/explore")
    repositories = []
    repo_elements = await page.query_selector_all("h2")
    for elem in repo_elements:
        repo_name_elem = await elem.query_selector("a")
        repo_name = await repo_name_elem.inner_text()
        starrers_link_elem = await elem.query_selector('a[href$="/-/starrers"]')
        forks_link_elem = await elem.query_selector('a[href$="/-/forks"]')
        merge_requests_link_elem = await elem.query_selector(
            'a[href$="/-/merge_requests"]'
        )
        issues_link_elem = await elem.query_selector('a[href$="/-/issues"]')
        starrers_count = (
            await starrers_link_elem.inner_text() if starrers_link_elem else "0"
        )
        forks_count = await forks_link_elem.inner_text() if forks_link_elem else "0"
        merge_requests_count = (
            await merge_requests_link_elem.inner_text()
            if merge_requests_link_elem
            else "0"
        )
        issues_count = await issues_link_elem.inner_text() if issues_link_elem else "0"
        repository_info = {
            "name": repo_name.strip(),
            "starrers": int(starrers_count.strip()),
            "forks": int(forks_count.strip()),
            "merge_requests": int(merge_requests_count.strip()),
            "issues": int(issues_count.strip()),
        }
        repositories.append(repository_info)
    return repositories


async def extract_high_activity_repos(page):
    """
    Extracts information on repositories with high merge requests and issue counts.

    This function scans through the current page listing of projects and identifies those with
    significant development activity. It specifically looks for projects with a high number of
    merge requests and issues, and extracts detailed information about these projects for analysis.

    [Usage preconditions]
    - **You must already be on a GitLab project listing page before calling this function.**

    Args:
    page : Playwright `Page` instance to control browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the repository.
        - "merge_requests" (int): Count of merge requests.
        - "issues" (int): Count of issues.
    """
    await page.goto("/dashboard/projects/starred")
    high_activity_repos = []
    repo_names = await page.query_selector_all("main h2.heading a")
    merge_requests_links = await page.query_selector_all(
        'main a[href*="merge_requests"]'
    )
    issues_links = await page.query_selector_all('main a[href*="issues"]')
    for name_elem, mr_elem, issue_elem in zip(
        repo_names, merge_requests_links, issues_links
    ):
        name = await name_elem.inner_text()
        merge_requests_text = await mr_elem.inner_text()
        issues_text = await issue_elem.inner_text()
        merge_requests_count = int(merge_requests_text)
        issues_count = int(issues_text)
        if merge_requests_count > 5 and issues_count > 5:
            high_activity_repos.append(
                {
                    "name": name,
                    "merge_requests": merge_requests_count,
                    "issues": issues_count,
                }
            )
    return high_activity_repos


async def extract_unmerged_pull_requests(page):
    """
    Extracts the number of unmerged pull requests for Byte Blaze projects to analyze potential backlogs.

    [Usage preconditions]
    - This API retrieves unmerged pull request information for Byte Blaze projects displayed on your current dashboard page.
    - **Make sure you are on the dashboard page where Byte Blaze project links are displayed before calling this function.**

    Args:
    page :  A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "project_name" (str): The name of the Byte Blaze project.
        - "unmerged_pull_requests" (int): The count of unmerged pull requests for the project.
    """
    await page.goto("/dashboard/projects/starred")
    project_info = []
    project_selectors = [
        (
            "Byte Blaze / accessible-html-content-patterns",
            'a[href="/byteblaze/accessible-html-content-patterns/-/merge_requests"]',
        ),
        (
            "Byte Blaze / empathy-prompts",
            'a[href="/byteblaze/empathy-prompts/-/merge_requests"]',
        ),
    ]
    for project_name, selector in project_selectors:
        element = await page.query_selector(selector)
        text_content = await element.text_content()
        project_info.append(
            {"project_name": project_name, "unmerged_pull_requests": int(text_content)}
        )
    return project_info


async def list_recently_updated_repositories(page):
    """
    [Function description]
    Lists repositories updated within the last year to identify active repositories.

    This function automates the process of collecting information about repositories and filtering them based on their update status over the last year.

    [Usage preconditions]
    - This API assumes you are on a dashboard that lists repositories.

    Args:
    page: A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries containing information about repositories updated in the last year.
        Each dictionary includes:
        - "name" (str): The name of the repository.
        - "last_updated" (str): Last update timestamp.
    """
    await page.goto("/dashboard/projects/starred")
    repository_elements = await page.query_selector_all("div.project-item")
    active_repositories = []
    for element in repository_elements:
        name_element = await element.query_selector("h2")
        last_updated_element = await element.query_selector(".project-last-updated")
        name = await name_element.inner_text() if name_element else "Unknown"
        last_updated_text = (
            await last_updated_element.inner_text()
            if last_updated_element
            else "Unknown"
        )
        if "Updated on" in last_updated_text:
            timestamp_str = last_updated_text.split("Updated on ")[1]
            last_updated = datetime.strptime(timestamp_str, "%Y-%m-%d")
            if datetime.now() - last_updated < timedelta(days=365):
                active_repositories.append(
                    {"name": name, "last_updated": timestamp_str}
                )
    return active_repositories


async def retrieve_starred_project_info(page):
    """
    [Function description]
    Extracts engagement metrics information for all starred projects.

    This function retrieves information including the number of stars, forks, merge requests, and issues
    for each of the starred projects listed on the current page.

    [Usage preconditions]
    - You must currently be on the GitLab dashboard page where the starred projects are listed.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries for each project containing:
        - "name" (str): The project name.
        - "stars" (int): Number of stars.
        - "forks" (int): Number of forks.
        - "merge_requests" (int): Number of merge requests.
        - "issues" (int): Number of issues.
    """
    await page.goto("/dashboard/projects/starred")
    project_info = []
    project_blocks = await page.query_selector_all("div.starred section a.heading")
    for project_block in project_blocks:
        project_name = await (await project_block.query_selector("h2")).inner_text()
        stars_link = await page.query_selector(f'a[href^="/{project_name}/-/starrers"]')
        stars_count = int(await stars_link.inner_text())
        forks_link = await page.query_selector(f'a[href^="/{project_name}/-/forks"]')
        forks_count = int(await forks_link.inner_text())
        merge_requests_link = await page.query_selector(
            f'a[href^="/{project_name}/-/merge_requests"]'
        )
        merge_requests_count = int(await merge_requests_link.inner_text())
        issues_link = await page.query_selector(f'a[href^="/{project_name}/-/issues"]')
        issues_count = int(await issues_link.inner_text())
        project_info.append(
            {
                "name": project_name,
                "stars": stars_count,
                "forks": forks_count,
                "merge_requests": merge_requests_count,
                "issues": issues_count,
            }
        )
    return project_info


async def get_projects_sorted_by_last_update(page):
    """
    [Function description]
    Retrieves projects from a general project dashboard, sorting them by their last update date in descending order.

    This function automates the extraction of project details from the current page.
    It gathers information about each project specifically the last update time and
    sorts these projects based on the last update in descending order.

    [Usage preconditions]
    - Requires access to a project dashboard page showing projects with update timestamps.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A sorted list of dictionaries where each dictionary contains project information:
        - "name" (str): The name of the project.
        - "last_updated" (str): The last updated timestamp in ISO 8601 format.
        - "link" (str): The relative URL to the project.
    """
    await page.goto("/dashboard/projects/starred")
    project_elements = await page.query_selector_all("main h2 > a")
    projects_info = []
    for project_element in project_elements:
        project_name = await (
            await project_element.get_property("innerText")
        ).json_value()
        project_link = await (await project_element.get_property("href")).json_value()
        last_updated_selector = "div.project-last-updated"
        last_updated_element = await page.query_selector(
            f'{last_updated_selector} [href="{project_link}"]'
        )
        if last_updated_element:
            last_updated_text = await (
                await last_updated_element.get_property("innerText")
            ).json_value()
        else:
            last_updated_text = None
        projects_info.append(
            {
                "name": project_name,
                "last_updated": last_updated_text,
                "link": project_link,
            }
        )
    sorted_projects = sorted(
        projects_info,
        key=lambda x: x["last_updated"] if x["last_updated"] else "",
        reverse=True,
    )
    return sorted_projects


async def extract_projects_by_user_role(page):
    """
    Extracts projects and differentiates them based on the user's role (Maintainer vs Owner).

    This function navigates through the projects listed on the GitLab dashboard and identifies
    the user's role in each project. It separates the projects where the user is a maintainer
    from those where the user is the owner.

    Usage preconditions:
    - You must already be on your GitLab dashboard that lists accessible projects.

    Args:
    page : A Playwright `Page` instance that controls the browser automation.

    Returns:
    dict
        A dictionary with two keys: "Maintainer" and "Owner". Each key contains a list of project titles
        in which the user has the corresponding role.
    """
    await page.goto("/dashboard/projects/starred")
    projects = {"Maintainer": [], "Owner": []}
    project_selectors = await page.query_selector_all("a[data-qa-project-name]")
    for project_selector in project_selectors:
        title = await (await project_selector.get_property("textContent")).json_value()
        role_tag = (
            await (await project_selector.query_selector("[data-qa-role-tag]"))
            .get_property("textContent")
            .json_value()
        )
        if role_tag == "Owner":
            projects["Owner"].append(title.strip())
        elif role_tag == "Maintainer":
            projects["Maintainer"].append(title.strip())
    return projects


async def extract_project_metrics(page):
    """
    Extracts detailed metrics from all projects listed on the current GitLab Explore page.

    This function automates the retrieval of various metrics for projects on the GitLab Explore page,
    including stars, forks, merge requests, and issues, allowing for a comprehensive project assessment.

    [Usage preconditions]
    - You must be on the GitLab Explore page listing several projects.

    Args:
    page: A Playwright `Page` instance that controls the automation session.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys for a project:
        - "name" (str): The name of the project.
        - "url" (str): The project URL.
        - "stars" (int): Count of stars on the project.
        - "forks" (int): Count of forks the project has.
        - "merge_requests" (int): Count of open merge requests.
        - "issues" (int): Count of open issues.
    """
    await page.goto("/explore")
    project_data = []
    projects = await page.query_selector_all("h2 a")
    for project in projects:
        name = (await project.text_content()).strip()
        url = await project.get_attribute("href")
        stars_selector = f'a[href="{url}/-/starrers"]'
        forks_selector = f'a[href="{url}/-/forks"]'
        mrs_selector = f'a[href="{url}/-/merge_requests"]'
        issues_selector = f'a[href="{url}/-/issues"]'
        stars_elem = await page.query_selector(stars_selector)
        forks_elem = await page.query_selector(forks_selector)
        mrs_elem = await page.query_selector(mrs_selector)
        issues_elem = await page.query_selector(issues_selector)
        stars = int((await stars_elem.text_content()).strip()) if stars_elem else 0
        forks = int((await forks_elem.text_content()).strip()) if forks_elem else 0
        merge_requests = int((await mrs_elem.text_content()).strip()) if mrs_elem else 0
        issues = int((await issues_elem.text_content()).strip()) if issues_elem else 0
        project_data.append(
            {
                "name": name,
                "url": url,
                "stars": stars,
                "forks": forks,
                "merge_requests": merge_requests,
                "issues": issues,
            }
        )
    return project_data


async def get_popular_projects(page):
    """
    [Function description]
    Identify and sort projects based on the number of stars to determine which projects are most popular.

    The function extracts each project's name and the count of stars it has, from the current page. It gathers the
    relevant information of each project, sorts the projects by their star count in descending order, and
    returns the sorted list of projects.

    [Usage preconditions]
    - This API assumes that you are on the GitLab projects list page where multiple projects are listed
      with their respective star counts.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "project_name" (str): The name of the project.
        - "star_count" (int): The number of stars the project has.
    """
    await page.goto("/")
    project_elements = await page.query_selector_all("main h2")
    projects = []
    for project_element in project_elements:
        project_name_element = await project_element.query_selector("a")
        project_name = await project_name_element.inner_text()
        sibling = await project_element.evaluate_handle(
            "elem => elem.nextElementSibling"
        )
        star_count_link = await sibling.query_selector("a[href$='/-/starrers']")
        if star_count_link:
            star_count = await star_count_link.inner_text()
            try:
                star_count = int(star_count)
            except ValueError:
                star_count = 0
        else:
            star_count = 0
        projects.append({"project_name": project_name, "star_count": star_count})
    projects.sort(key=lambda x: x["star_count"], reverse=True)
    return projects


async def list_zero_engagement_projects(page):
    """
    [Function description]
    Identify projects with zero stars, forks, merge requests, and issues from the dashboard.

    This function automates the extraction of project details from the dashboard and checks for projects
    that have zero engagement. It identifies projects that have zero stars, forks, merge requests, and issues.

    [Usage preconditions]
    - Ensure that you are already on the projects dashboard page before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the project with zero engagement.
        - "url" (str): The URL to access the project.
    """
    await page.goto("/")
    projects_zero_engagement = []
    project_headings = await page.query_selector_all("main > heading.level-2")
    for project_heading in project_headings:
        project_name_element = await project_heading.query_selector("a")
        if project_name_element:
            project_name = await project_name_element.inner_text()
            project_url = await project_name_element.get_attribute("href")
            engagement_selectors = {
                "stars": '~ + a[href$="starrers"]',
                "forks": '~ + a[href$="forks"]',
                "merge_requests": '~ + a[href$="merge_requests"]',
                "issues": '~ + a[href$="issues"]',
            }
            stars = await (
                await project_heading.query_selector(engagement_selectors["stars"])
            ).inner_text()
            forks = await (
                await project_heading.query_selector(engagement_selectors["forks"])
            ).inner_text()
            merge_requests = await (
                await project_heading.query_selector(
                    engagement_selectors["merge_requests"]
                )
            ).inner_text()
            issues = await (
                await project_heading.query_selector(engagement_selectors["issues"])
            ).inner_text()
            if (
                stars == "0"
                and forks == "0"
                and merge_requests == "0"
                and issues == "0"
            ):
                projects_zero_engagement.append(
                    {"name": project_name, "url": project_url}
                )
    return projects_zero_engagement


async def get_repository_metrics(page):
    """
    [Function description]
    Extracts detailed engagement metrics for each project listed on the GitLab dashboard.

    This function navigates through the GitLab dashboard page to gather comprehensive
    information about each repository, including:
    - Repository name
    - Star count
    - Fork count
    - Merge request count
    - Issue count

    [Usage preconditions]
    - The API retrieves engagement metrics for repositories currently listed on the GitLab dashboard.
    - **You must already be on a GitLab dashboard page containing repository listings before calling this function.**

    Args:
    page :  A Playwright `Page` instance that automates browser actions.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The repository name.
        - "stars" (int): The number of stars.
        - "forks" (int): The number of forks.
        - "merge_requests" (int): The number of merge requests.
        - "issues" (int): The number of issues.
    """
    await page.goto("/")
    repo_elements = await page.query_selector_all("h2")
    repositories = []
    for repo_element in repo_elements:
        name_element = await repo_element.query_selector("a")
        name = (await name_element.inner_text()).strip()
        stars_element = await page.query_selector(
            f'h2:has-text("{name}") + a[href*="/-/starrers"]'
        )
        stars = int(await stars_element.inner_text()) if stars_element else 0
        forks_element = await page.query_selector(
            f'h2:has-text("{name}") + a[href*="/-/forks"]'
        )
        forks = int(await forks_element.inner_text()) if forks_element else 0
        merge_requests_element = await page.query_selector(
            f'h2:has-text("{name}") + a[href*="/-/merge_requests"]'
        )
        merge_requests = (
            int(await merge_requests_element.inner_text())
            if merge_requests_element
            else 0
        )
        issues_element = await page.query_selector(
            f'h2:has-text("{name}") + a[href*="/-/issues"]'
        )
        issues = int(await issues_element.inner_text()) if issues_element else 0
        repositories.append(
            {
                "name": name,
                "stars": stars,
                "forks": forks,
                "merge_requests": merge_requests,
                "issues": issues,
            }
        )
    return repositories


async def rank_projects_by_popularity(page):
    """
    [Function description]
    Ranks projects by popularity based on the number of stars displayed on the GitLab Dashboard.

    This function automates the extraction of project details from the current page
    of the GitLab Dashboard, ranks them based on star count, and returns the result.

    [Usage preconditions]
    - You must already be on the GitLab Dashboard page containing project lists before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following keys:
        - "name" (str): The name of the project.
        - "stars" (int): The number of stars received by the project.
    """
    await page.goto("/")
    projects = []
    project_elements = await page.query_selector_all("h2")
    for element in project_elements:
        name_element = await element.query_selector("a")
        star_element = await element.query_selector("+ a[href$='/-/starrers']")
        project_name = await name_element.inner_text() if name_element else ""
        star_count = int(await star_element.inner_text()) if star_element else 0
        projects.append({"name": project_name, "stars": star_count})
    ranked_projects = sorted(projects, key=lambda x: x["stars"], reverse=True)
    return ranked_projects


async def identify_zero_engagement_projects(page):
    """
    [Function description]
    Identifies projects with zero engagement on the current GitLab dashboard page.

    This function scans the project listings on a GitLab dashboard and retrieves those projects
    that have zero stars, zero forks, zero merge requests, and zero issues, indicating no engagement.

    [Usage preconditions]
    - You must already be on a GitLab dashboard page listing multiple projects before calling this function.

    Args:
    page : A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "name" (str): The name of the project.
        - "url" (str): The URL to the project's page.
    """
    await page.goto("/")
    zero_engagement_projects = []
    project_elements = await page.query_selector_all('heading[level="2"]')
    for element in project_elements:
        name = await (await element.query_selector("a")).inner_text()
        url = await (await element.query_selector("a")).get_attribute("href")
        stars_element = await page.query_selector(f'a[href="{url}/-starrers"]')
        forks_element = await page.query_selector(f'a[href="{url}/-forks"]')
        merge_requests_element = await page.query_selector(
            f'a[href="{url}/-merge_requests"]'
        )
        issues_element = await page.query_selector(f'a[href="{url}/-issues"]')
        stars_count = await stars_element.inner_text()
        forks_count = await forks_element.inner_text()
        merge_requests_count = await merge_requests_element.inner_text()
        issues_count = await issues_element.inner_text()
        if (
            stars_count == "0"
            and forks_count == "0"
            and merge_requests_count == "0"
            and issues_count == "0"
        ):
            zero_engagement_projects.append({"name": name, "url": url})
    return zero_engagement_projects


async def navigate_to_explore_projects_page(page):
    """
    Navigate to the Explore Projects page on GitLab.

    This function automates the process of clicking the 'Explore' link on the GitLab dashboard,
    bringing the user to the page where various repositories and projects can be explored.

    Usage Log:
    - Called from the GitLab dashboard and successfully navigated to the Explore Projects page.

    Args:
    page : A Playwright `Page` instance representing the browser page.

    Expected Outcome:
    - The function navigates to the 'Explore Projects' page on GitLab.
    """
    await page.goto("/")
    await page.get_by_role("link", name="Explore").click()


async def extract_projects_with_zero_engagement(page):
    """
    [Function description]
    Extracts projects with zero engagement from the explore page on GitLab.

    This function automates the extraction of project information from the webpage,
    filtering projects that have zero stars, zero forks, zero merge requests, and zero issues.

    [Usage preconditions]
    - This function retrieves projects with zero engagement from the **explore page**.
    - **You must already be on the GitLab explore page of the projects before calling this function.**

    Args:
    page : A Playwright `Page` instance that controls browser automation.


    Returns:
    list of dict
        A list of dictionaries where each dictionary contains the following key:
        - "name" (str): The name of the project with zero engagement.
    """
    await page.goto("/explore")
    zero_engagement_projects = []
    project_headings = await page.query_selector_all("h2.heading")
    for project_heading in project_headings:
        project_link = await project_heading.query_selector("a")
        project_name = await project_link.inner_text()
        starrers_count = await (
            await page.query_selector(
                f'a[href$="/{project_name}-/starrers"]'
            ).inner_text()
        )
        forks_count = await (
            await page.query_selector(f'a[href$="/{project_name}-/forks"]').inner_text()
        )
        merge_requests_count = await (
            await page.query_selector(
                f'a[href$="/{project_name}-/merge_requests"]'
            ).inner_text()
        )
        issues_count = await (
            await page.query_selector(
                f'a[href$="/{project_name}-/issues"]'
            ).inner_text()
        )
        if (
            starrers_count == "0"
            and forks_count == "0"
            and merge_requests_count == "0"
            and issues_count == "0"
        ):
            zero_engagement_projects.append({"name": project_name})
    return zero_engagement_projects


async def fetch_projects_by_star_count(page):
    """
    Find Most Popular Projects by Star Count.

    This function gathers a list of GitLab projects on the current page of GitLab Explore,
    sorted by the number of stars each project has. It retrieves the project name and the
    count of stars and ranks the projects from most to least stars, aiding in identifying
    popular or trending projects.

    [Usage preconditions]
    - You must be on the GitLab Explore projects page before calling this function.

    Args:
    page :  A Playwright `Page` instance that controls browser automation.

    Returns:
    list of dict
        A list of dictionaries where each dictionary contains:
        - "name" (str): The name of the project.
        - "stars" (int): The number of stars the project has received.
    """
    await page.goto("/explore")
    project_elements = await page.query_selector_all("main > h2")
    project_star_links = await page.query_selector_all('main a[href*="starrers"]')
    projects = []
    for project_elem, star_link in zip(project_elements, project_star_links):
        project_name = await (await project_elem.query_selector("a")).inner_text()
        star_count = int(await (await star_link).inner_text())
        projects.append({"name": project_name, "stars": star_count})
    projects_sorted = sorted(projects, key=lambda x: x["stars"], reverse=True)
    return projects_sorted
