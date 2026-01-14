import ast
import sys

# Python 3.9+ has ast.unparse built-in, use astor as fallback for older versions
if sys.version_info >= (3, 9):
    def ast_to_source(node):
        return ast.unparse(node)
else:
    import astor
    def ast_to_source(node):
        return astor.to_source(node)

from skillweaver.knowledge_base.generate_schema import generate_schema
from skillweaver.knowledge_base.type_checking import find_type_errors


def _is_correct_syntax(code: str) -> list[str]:
    try:
        ast.parse(code)
        return []
    except SyntaxError as e:
        return ["SyntaxError: " + str(e)]


def _check_params(fn: ast.AsyncFunctionDef) -> list[str]:
    if len(fn.args.args) == 0 or fn.args.args[0].arg != "page":
        return [f"{fn.name}: The first parameter of your function must be `page`."]

    violations: list[str] = []

    try:
        generate_schema(fn)
    except ValueError as e:
        violations.append(
            f"{fn.name}: Only `str`, `int`, `float`, `bool`, and `list[...]` annotations are permitted. Received invalid annotation: {e}"
        )

    for p in fn.args.args:
        if p.arg.endswith("_id"):
            violations.append(
                f"{fn.name}, argument {p.arg}: Parameter names should not end with `_id`. This is too 'under-the-hood' - prefer to use information that is readily available to the human user."
            )

    return violations


def check_code(code: str, context: str) -> list[str]:
    """
    Returns a list of strings describing errors in the code.
    """

    if syntax_violations_ := _is_correct_syntax(code):
        return syntax_violations_

    violations: list[str] = []

    tree = ast.parse(code)

    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            violations.append(
                "You must check for errors proactively (i.e. using await locator.count(), etc.). You cannot just create a global try/catch block to avoid your code breaking. You should clearly describe in the function documentation what initial UI state the website should be in before calling."
            )
        elif isinstance(node, ast.While):
            violations.append(
                "You should not use `while` loops in your code. This is because `while` loops can easily lead to infinite loops, which can be difficult to debug."
            )

    for s in tree.body:
        if isinstance(s, ast.FunctionDef):
            violations.append("Only `async` functions are permitted: " + s.name)

        elif isinstance(s, ast.AsyncFunctionDef):
            if param_violations_ := _check_params(s):
                violations.extend(param_violations_)

            if s.name == "act":
                violations.append(
                    "Please rename your function to something other than `act`. `act` is a reserved function name."
                )

            # make sure there is a docstring
            if not ast.get_docstring(s):
                violations.append(
                    f"Please include a docstring for your function `{s.name}`."
                )
            else:
                non_docstring_statements = s.body[1:]
                if len(non_docstring_statements) == 0:
                    violations.append("Empty function definition: " + s.name)
                # else:
                #     # require an await page.goto as the first command
                #     src = astor.to_source(non_docstring_statements[0])
                #     if not src.startswith('await page.goto("/') and not src.startswith(
                #         "await page.goto('/"
                #     ):
                #         violations.append(
                #             "The first command in your function should be `await page.goto(url)`, to ensure that the browser is in the correct state. Make sure that you use relative URLs."
                #         )

            source = ast_to_source(s)
            if "await page.goto(" not in source:
                violations.append(
                    f"Please include an `await page.goto(url)` command as the first command in your function `{s.name}`. This ensures that the browser is in the correct state."
                )

        else:
            violations.append(
                "Only `async` function definitions are permitted in your response. If you need to import something, place it *inside* the function body."
            )

    if ".locator(" in code or ".query_selector(" in code:
        violations.append(
            "Please use Accessibility Tree-centric selectors, like `page.get_by_role()`, `.nth()`, instead of the CSS-style selectors used in `.locator()`."
        )

    # Static analysis for type errors.
    relevant_violations = find_type_errors(code, context)
    for message, rule, start_line, end_line in relevant_violations:
        violations.append(f"Type error: {message} ({rule}) at {start_line}:{end_line}")

    for a in ["click", "type", "fill", "hover", "wait_for_selector"]:
        if "page." + a in code:
            if a == "wait_for_selector":
                violations.append(
                    f"Please use `<locator>.wait_for()` instead of page.wait_for_`selector(selector)`."
                )
            else:
                violations.append(
                    f"Please use `<locator>.{a}()` instead of `page.{a}(selector)`."
                )

    return violations
