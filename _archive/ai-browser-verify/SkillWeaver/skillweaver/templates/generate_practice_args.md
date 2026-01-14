You are a 'web agent' who is learning how to use a website. You have an untested automation called {name} with the signature:

```python3
{signature}
```

Because this is untested, you want to test it right now. Generate some reasonable parameters based on the page.
For example, find_cheapest_flight(page, from: str, to: str) => {{"from": "New York City", "to": "Los Angeles"}}.
Don't use the `page` parameter, as we will provide that for you. Test new args, if it looks like existing ones
have already been tested.

The current website accessibility tree is:
<ax_tree>
{ax_tree}
</ax_tree>
