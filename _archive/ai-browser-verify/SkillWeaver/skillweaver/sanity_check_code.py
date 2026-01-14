import ast

from skillweaver.knowledge_base.knowledge_base import KnowledgeBase
from skillweaver.knowledge_base.type_checking import find_type_errors


def sanity_check_codegen_code(
    code: str,
    disabled_function_names: list[str],
    knowledge_base: KnowledgeBase,
    as_reference_only: bool,
):
    errors: list[str] = []
    try:
        # Syntax check.
        tree = ast.parse(code)
        for f in tree.body:
            if isinstance(f, ast.AsyncFunctionDef):
                if f.name != "act":
                    raise SyntaxError("Function name must be 'act'")
                elif len(f.args.args) != 1 or f.args.args[0].arg != "page":
                    raise SyntaxError(
                        "Function must take exactly one argument: `page`."
                    )

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in disabled_function_names:
                        errors.append(
                            f"Function `{node.func.id}` is disabled. Please use another function."
                        )
                        break
    except SyntaxError as e:
        errors.append(f"Syntax error: {e.args[0]}")
        return errors

    for f in ["click", "fill", "type"]:
        if "page." + f in code:
            errors.append(
                f"Please use the `page.get_by_...().{f}()` functions instead of the `page.{f}(selector)` functions."
            )
            break

    type_errors = find_type_errors(
        code,
        context=f"import asyncio, re\n{knowledge_base.code if not as_reference_only else ''}",
    )
    for message, rule, start_line, end_line in type_errors:
        errors.append(f"Type error: {message} ({rule}) at line {start_line}")

    if len(type_errors) > 0 and as_reference_only:
        errors.append(
            "Note that you cannot truly *use* any of the functions in the context! You must only *refer* to them."
        )

    if ".locator(" in code or ".query_selector" in code:
        errors.append(
            "Please use Accessibility Tree-centric selectors, like `page.get_by_role()`, `.nth()`, instead of the CSS-style selectors like `.locator()` or `.query_selector()`."
        )
        return errors

    return errors


if __name__ == "__main__":
    test_code = f"""
async def act(page):
    await update_bio('I am a robot.')
    """
    context = f"""
import asyncio, os

{open("./skillweaver/oracles/beyond_browsing/bb_reddit_code.py").read()} 
"""
    # result = typecheck_generated_api(test_code, context)

    errors = sanity_check_codegen_code(
        test_code,
        disabled_function_names=[],
        knowledge_base=KnowledgeBase(code=context),
        as_reference_only=False,
    )

    print(errors)
