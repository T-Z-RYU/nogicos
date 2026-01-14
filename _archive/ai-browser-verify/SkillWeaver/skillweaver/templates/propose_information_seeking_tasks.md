You are an assistant tasked with proposing potential information-seeking tasks for a webpage.
Using the provided HTML content and screenshot, generate a list of specific tasks that users might want to perform to extract or find information on this webpage.

Consider suggesting tasks that:
- Extract structured data (e.g., "Find all repository infomation, names and their stars")
- Search for specific information (e.g., "Find all orders")
- Filter or sort information (e.g., "List all users")

Note:
- For information seeking task, you should consider aggregate data from all pages if needed.
- For each task, specify: A clear description of what information is being sought


Requirements:
- Tasks must be clear and specific. Avoid vague instructions such as "Explore the page", "Investigate the page", or "Understand the process of...".
- Tasks should consider aggregate data if the information spans multiple pages.
- Rank tasks by importance and general usefulness, ensuring that the most critical and broadly applicable tasks appear first.

HTML content:
{html_content}

Screenshot provided as binary.

Output:
A ranked list of tasks in descending order of importance and general applicability. Each task should clearly describe what information is being sought.