import ast
import sys

# Python 3.9+ has ast.unparse built-in
if sys.version_info >= (3, 9):
    def ast_to_source(node):
        return ast.unparse(node)
else:
    import astor
    def ast_to_source(node):
        return astor.to_source(node)

from typing_extensions import OrderedDict


def _schemify_annotation(annotation: ast.expr) -> dict:
    # Disallow `param: dict` annotations.
    if isinstance(annotation, ast.Name):
        mapping = {
            "str": {"type": "string"},
            "int": {"type": "number"},
            "float": {"type": "number"},
            "bool": {"type": "boolean"},
            # "dict": {"type": "object"},
            "list": {"type": "array", "items": {"type": "string"}},
        }
        if annotation.id in mapping:
            return mapping[annotation.id]

    elif isinstance(annotation, ast.Subscript):
        assert isinstance(annotation.value, ast.Name)
        if annotation.value.id.lower() == "list":
            return {
                "type": "array",
                "items": _schemify_annotation(annotation.slice),
            }
        elif annotation.value.id.lower() == "union":
            return {"anyOf": [_schemify_annotation(el) for el in annotation.slice.elts]}  # type: ignore
        elif annotation.value.id.lower() == "literal":
            return {
                "type": "string",
                "enum": [el.value for el in annotation.slice.elts],  # type: ignore
            }
        # elif annotation.value.id.lower() == "dict":
        #     return {"type": "object"}

    raise ValueError(f"Unsupported annotation: {ast_to_source(annotation)}")


def generate_schema(
    func: ast.AsyncFunctionDef | ast.FunctionDef,
) -> OrderedDict[str, dict]:
    """
    Given a Python Abstract Syntax Tree for a function declaration, generate a dictionary of argname -> JSON schema.
    """

    # Remove the `page` parameter, because it is provided by us.
    if len(func.args.args) > 0 and func.args.args[0].arg == "page":
        include_args = func.args.args[1:]
    else:
        include_args = func.args.args

    return OrderedDict(
        (
            arg.arg,
            (
                _schemify_annotation(arg.annotation)
                if arg.annotation
                else {"type": "string"}
            ),
        )
        for arg in include_args
    )
