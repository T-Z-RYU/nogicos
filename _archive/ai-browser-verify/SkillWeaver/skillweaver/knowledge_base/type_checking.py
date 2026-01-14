# -*- coding: utf-8 -*-
import json
import os
import re
import shutil
import subprocess
import tempfile

# check pyright 
PYRIGHT_AVAILABLE = shutil.which("pyright") is not None

def _typecheck_file(file: str):
    if not PYRIGHT_AVAILABLE:
        # pyright returnresult
        return {"generalDiagnostics": []}
    
    try:
        proc = subprocess.run(
            ["pyright", "--outputjson", file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
        data = proc.stdout.decode("utf-8").strip()
        return json.loads(data)
    except FileNotFoundError:
        # pyright 
        return {"generalDiagnostics": []}
    except subprocess.TimeoutExpired:
        # timeout
        return {"generalDiagnostics": []}
    except Exception as e:
        with open(file) as f:
            content = f.read()
        print("failed to check type safety of", content)
        return {"generalDiagnostics": []}


def _typecheck_string(code: str):
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(code)
        f.close()
        out = _typecheck_file(f.name)
        os.unlink(f.name)

    return (out, f.name)


def _add_page_type_annotations(code: str):
    """
    If the first argument is just 'page' instead of 'page: Page', add the type annotation.
    """

    return re.sub(
        "async def ([a-zA-Z0-9_]+)\\(page(,|\\))", "async def \\1(page: Page\\2", code
    )


def find_type_errors(code: str, context: str):
    """
    Special case where the first argument of each function should be `page: Page`.
    """
    # Static type analysis.
    # add the `Page` type annotation.
    before = "from playwright.async_api import Page\n\n" + context + "\n\n"
    filter_start_line = len(before.split("\n"))
    type_checking_code = before + _add_page_type_annotations(code)

    relevant_violations: list[tuple[str, str, int, int]] = []
    if len(code.strip()) == 0:
        return relevant_violations
    type_check_result, tmpfile_name = _typecheck_string(type_checking_code)
    for violation in type_check_result["generalDiagnostics"]:
        if violation["severity"] in ["error", "warning"]:
            message = violation["message"]
            rule = violation.get("rule", "unknown")
            start_line = violation["range"]["start"]["line"]
            end_line = violation["range"]["end"]["line"]
            if start_line >= filter_start_line:
                relevant_violations.append(
                    (
                        message,
                        rule,
                        start_line - filter_start_line,
                        end_line - filter_start_line,
                    )
                )

    if "while True" in code or "while (True)" in code:
        relevant_violations.append(
            (
                "Infinite loop detected. Do not use 'while True' or any other kind of infinite loop.",
                "infiniteLoop",
                -1,
                -1,
            )
        )

    return relevant_violations
