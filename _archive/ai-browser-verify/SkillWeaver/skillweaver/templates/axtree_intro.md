Consider the following Accessibility Tree.
The accessibility tree is formatted like this:
[role] ["name"] [properties] {{
    [child1]
}};
[role] ["name"] [properties]; // no children

Here is an example:
<example>

article "Willy Wonka's Chocolate Factory Opens Its Gates" {{
    link "Share";
}};

article "Hogwarts Begins Accepting Applicants for Class of 2029" {{
    link "Share";
}};

... to select the first link, you can do (because name = case-insensitive substring match unless exact=True is supplied):

```python3
first_link = page.get_by_role("article", name="Willy Wonka").get_by_role("link", name="Share")
```
</example>

Here is another example:
<example>
article {{
    header "How can I install CUDA on Ubuntu 22?";
    link "Share";
}};

article {{
    header "How do I install Docker?";
    link "Share";
}};


... to select the first link, you can do:

```python3
page.get_by_role("article").filter(has=page.get_by_role("header", "How can I install CUDA")).get_by_role("link", name="Share")
```

Here, the .filter() is necessary to ensure that we select the correct `article`. This is especially important in cases where the parent
element doesn't include relevant criteria for identifying a child element.
</example>
