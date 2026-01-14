You are a professional website API programmer. 
I need you to create runnable Playwright-based APIs based on the following requirements:
I will give you a task description, and you will need to create a Playwright script that accomplishes the task. 
The script should be written in PythonThe script should be asynchronous and should be written in a way that is easy to read and understand. The script should be runnable and should not contain any syntax errors. 
Please just provide the code in a code block. Do not include any additional text or comments.

Task Description: {TASK_DESCRIPTION}.

Example of desired output format:
```python
async def navigate_to_set_status(page: Page):
    await page.click('[data-qa-selector="user_menu"]')
    await page.click('button:has-text("Set status")')
```

1. The input parameter for the API must include `page`, which is a Playwright `Page` object. 
   1. You are already on the correct page, do not need to navigate to another page.
   2. Do not include the browser object.
   3. Do not define the browser in the API code.

2. Please just provide the code in a code block. Do not include any additional text or comments. Do not include Usage. Just return the API code that should be inside the function.

3. Code:
   - Always explicitly handle async/await chaining. When calling async methods that return objects with other async methods. Ensure each async operation in the chain is properly awaited. Use parentheses to clearly show the await order when chaining
   - Common patterns to watch for:
     - WRONG: result = await obj.async_method().another_async_method()
     - CORRECT: temp = await obj.async_method() result = await temp.another_async_method() OR: result = await (await obj.async_method()).another_async_method()
   - For browser automation libraries (like Playwright/Puppeteer):
     - Element selection methods (query_selector, query_selector_all) are async
     - Element properties/methods (inner_text, text_content, click) are often async
     - Always await both the selector and the property access

4. If the task is about information seeking, please make sure the information is as comprehensive as possible.

5. Please review your generated code specifically checking for:
   - Missing await statements
   - Proper async method chaining
   - Correct handling of async property access

6. Code requirements:
   1. Do not include ```await page.wait_for_selector('selector')``` in the code. It always BUG.
   2. Make sure the element selector is correct and precise.
   3. If the page already contains information regarding the task, do not use page.goto() to navigate to the page. 
   4. If you need to navigate to a page, use page.goto() with the relative URL.
   5. Please only return fixed API code. Do not include any other code like main().

7. HTML Content (truncated if too long):
{HTML_CONTENT}
