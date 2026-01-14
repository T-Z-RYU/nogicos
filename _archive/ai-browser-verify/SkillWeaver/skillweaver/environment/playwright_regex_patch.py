import re
from re import Pattern
import playwright._impl._str_utils
def escape_regex_for_selector(text: Pattern) -> str:
    # Even number of backslashes followed by the quote -> insert a backslash.
    return (
        "/"
        + re.sub(r'(^|[^\\])(\\\\)*(["\'`])', r"\1\2\\\3", text.pattern)
        .replace(">>", "\\>\\>")
        .replace("/", "\\u002F")
        + "/"
        + playwright._impl._str_utils.escape_regex_flags(text)
    )


def apply():
    playwright._impl._str_utils.escape_regex_for_selector = escape_regex_for_selector
