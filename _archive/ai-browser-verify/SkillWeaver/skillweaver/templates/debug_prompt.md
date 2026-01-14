You are a Python debugging expert specializing in web automation with Playwright. 
Given the following code, error, and HTML context, analyze the issue and provide a fixed version.


## Instructions
1. Analyze the HTML structure to understand the page elements and locate what the task requires.
2. Identify the cause of the error in the code
3. Consider common Playwright issues like:
   - Selector timing issues
4. Provide a complete fixed version of the code
5. The HTML content provided is a truncated version of the webpage structure, because of constraints on the context window size.
6. The input parameter for the API must include `page`, which is a Playwright `Page` object. 
   1. Do not include the browser object.
   2. Do not define the browser in the API code.
7. Do not need goto() method because the page already contains the necessary information.
8. Do not include ```await page.wait_for_selector('selector')``` in the code. It always BUG.


Please return ONLY the fixed code without any explanation or markdown formatting within the code block. 
The code should be a complete, runnable solution that includes all necessary imports.

Please only return fixed API code. Do not include any other code like main().


## Task Description
{TASK_DESCRIPTION}

## Original Code
```python
{CODE}
```

## Error Information
```
{ERROR_INFO}
```

## Current Webpage HTML Structure
```html
{HTML_CONTENT}
```