import ast
import asyncio
import json
import re
import sys
from typing import Literal

# Python 3.9+ has ast.unparse built-in
if sys.version_info >= (3, 9):
    def ast_to_source(node):
        return ast.unparse(node)
else:
    import astor
    def ast_to_source(node):
        return astor.to_source(node)

import black
import numpy as np
import openai
from aioconsole import aprint
from openai.types.chat import ChatCompletionToolParam
from openai.types.responses import FunctionToolParam
from typing_extensions import OrderedDict, TypedDict

from skillweaver.knowledge_base.code_verification import check_code
from skillweaver.knowledge_base.generate_schema import generate_schema
from skillweaver.lm import LM
from skillweaver.templates import (
    kb_procedural_update_single_templ,
    predict_relevant_functions_templ,
)
from skillweaver.util import J


class Function(TypedDict):
    name: str
    args: OrderedDict[str, dict]
    docstring: str
    source: str
    is_synchronous: bool


def get_json_schema_from_function(function: Function):
    # Identify arguments in the docstring, so we can directly attach the argument docs to the OpenAI spec.
    in_args = False
    arg_infos = {}
    for line in function["docstring"].split("\n"):
        line = line.strip()
        if line.strip() == "Arguments:":
            in_args = True

        if in_args and line.startswith("- "):
            match_result = re.match(
                r"(- )?\`?(?P<argname>\w+)\`?: (?P<argdesc>.+)", line
            )
            if match_result is not None:
                arg_infos[match_result.group("argname")] = match_result.group("argdesc")
            else:
                in_args = False

    return {
        "type": "object",
        "properties": {
            arg: {
                **function["args"][arg],
                # Add the "description" key directly into the arg.
                **(
                    {"description": truncate_string_if_too_long(arg_infos[arg])}
                    if arg in arg_infos
                    else {}
                ),
            }
            for arg in function["args"].keys()
        },
        "required": list(function["args"].keys()),
        "additionalProperties": False,
    }


def count_interactions(fn: Function):
    # return num of clicks, types, fills, hovers, select_options
    # at some point we should incorporate interaction counts for subfunctions (ie composite actions)
    src = fn["source"]
    count = 0
    for a in ["click", "type", "fill", "hover", "select_option"]:
        count += src.count(f".{a}(")

    return count


def _get_function_signature_string(fn: Function):
    # Return the function up until the closing parenthesis.
    return fn["source"][: fn["source"].index(")") + 1]


def _get_unindented_docstring(fn: Function):
    # Unindent docstring.
    docstring_lines = fn["docstring"].strip().split("\n")
    base_indent = 0
    if len(docstring_lines) > 1:
        base_indent = len(docstring_lines[1]) - len(docstring_lines[1].lstrip())

    docstring_unindented = "\n".join(
        [docstring_lines[0], *[line[base_indent:] for line in docstring_lines[1:]]]
    )
    return docstring_unindented


def format_function_as_pretty_string(fn: Function):
    return f"# Skill: {_get_function_signature_string(fn)}\n{_get_unindented_docstring(fn)}\n\n"


def truncate_string_if_too_long(s: str, max_length=1000):
    if len(s) > max_length:
        return s[: max_length - 3] + "..."

    return s


_embed_cache = {}


async def embed(string: str):
    if string in _embed_cache:
        return _embed_cache[string]

    oai = openai.AsyncOpenAI()
    result = await oai.embeddings.create(input=string, model="text-embedding-3-small")
    embed = np.array(result.data[0].embedding)
    _embed_cache[string] = embed
    return embed


def get_openai_responses_tool_param(function: Function) -> FunctionToolParam:
    return {
        "name": function["name"],
        # TODO: We can omit arguments from the docstring if we already attach descriptions to each element.
        "description": truncate_string_if_too_long(function["docstring"]),
        "strict": True,
        "parameters": get_json_schema_from_function(function),
        "type": "function",
    }


def get_openai_chat_tool_param(function: Function) -> ChatCompletionToolParam:
    return {
        "function": {
            "name": function["name"],
            # TODO: We can omit arguments from the docstring if we already attach descriptions to each element.
            "description": truncate_string_if_too_long(function["docstring"]),
            "strict": True,
            "parameters": get_json_schema_from_function(function),
        },
        "type": "function",
    }


class KnowledgeBase:
    def __init__(
        self,
        code: str = "",
        metadata: dict | None = None,
        semantic_knowledge="",
    ):
        self.metadata = metadata or {"functions": {}, "global_version": 0}
        self.code = code
        self.semantic_knowledge = semantic_knowledge
        self.lock = asyncio.Lock()
        self.hide_unverified = False

    def mark_all_as_tested(self):
        for f in self.metadata["functions"]:
            fn = self.metadata["functions"][f]
            fn["test_count"] = 1
            fn["version"] = 1
            fn["references"] = ["mark_all_as_tested"]
            fn["events"] = [
                {"type": "mark_all_as_tested", "reference": "mark_all_as_tested"}
            ]

    def copy(self) -> "KnowledgeBase":
        kb = KnowledgeBase(
            code=self.code,
            metadata=self.metadata,
            semantic_knowledge=self.semantic_knowledge,
        )
        kb.hide_unverified = self.hide_unverified
        return kb

    def _apply(self, code_update: str, reference: str):
        existing_tree = ast.parse(self.code)
        new_tree = ast.parse(code_update)
        is_function_def = lambda node: isinstance(node, ast.FunctionDef) or isinstance(
            node, ast.AsyncFunctionDef
        )
        existing_functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {
            node.name: node for node in existing_tree.body if is_function_def(node)  # type: ignore
        }
        updated_functions = existing_functions.copy()

        for node in new_tree.body:
            if is_function_def(node):
                assert isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                # Update the source.
                updated_functions[node.name] = node
                if node.name not in self.metadata["functions"]:
                    # Update the version number and success counts.
                    self.metadata["functions"][node.name] = {
                        "version": 0,
                        "test_count": 0,
                        "references": [reference],
                        "events": [{"type": "update", "reference": reference}],
                    }
                else:
                    self.metadata["functions"][node.name]["version"] += 1
                    self.metadata["functions"][node.name]["test_count"] = 0
                    self.metadata["functions"][node.name]["references"].append(
                        reference
                    )
                    self.metadata["functions"][node.name]["events"].append(
                        {"type": "update", "reference": reference}
                    )

        merged_tree = ast.Module(body=list(updated_functions.values()), type_ignores=[])
        merged_code = ast_to_source(merged_tree)
        merged_code = black.format_str(merged_code, mode=black.FileMode())

        self.code = merged_code

    def increment_test_count(self, function_name: str, reference: str):
        self.metadata["global_version"] += 1
        self.metadata["functions"][function_name]["test_count"] += 1
        self.metadata["functions"][function_name]["references"].append(reference)
        self.metadata["functions"][function_name]["events"].append(
            {"type": "exception_free_test", "reference": reference}
        )

    async def get_most_relevant_functions_via_embedding_similarity(
        self, task_string: str
    ) -> list[Function]:
        fns = self.get_functions()
        if len(fns) < 5:
            return fns

        function_embeddings = np.array(
            await asyncio.gather(
                *[
                    embed(
                        (
                            "A Python function with the name "
                            + f["name"]
                            + "\n\n"
                            + f["docstring"]
                        ).strip()
                    )
                    for f in fns
                ]
            )
        )
        task_embedding = await embed(task_string)
        scores = np.dot(function_embeddings, task_embedding)
        # choose top 5 scores
        top5 = np.argsort(scores)[-5:]
        best_matches = [fns[i] for i in top5]
        return best_matches

    def rate_practice_utility(self, fn: Function):
        return (
            count_interactions(fn) - self.metadata["functions"][fn["name"]]["version"]
        )

    async def update(
        self,
        lm: LM,
        task: dict,
        trajectory_string: str,
        reference: str,
        feedback: str = "",
        additional_used_functions: list[str] = [],
    ):
        self.metadata["global_version"] += 1

        task_string = json.dumps(task)

        semantic_update_diagnostics = None

        # Filter to verified code!! (e.g. code that has been unit-tested)
        # We also include any functions that were called during the episode.
        filtered_code = "\n\n".join(
            [
                f["source"]
                for f in self.get_functions()
                if self.is_tested(f["name"])
                or (task["type"] == "test" and task["function_name"] == f["name"])
                or f["name"] in additional_used_functions
            ]
        )

        instructions = kb_procedural_update_single_templ(
            procedural_knowledge=filtered_code,
            semantic_knowledge=self.semantic_knowledge,
            action_history=trajectory_string,
            intended_task=task_string,
            feedback=feedback,
        )

        procedures_update_diagnostics = {
            "attempts": [],
            "successful": True,
            "instructions": instructions,
        }

        while len(procedures_update_diagnostics["attempts"]) < 10:
            if len(procedures_update_diagnostics["attempts"]) > 0:
                await aprint("Retrying...")
                await aprint("Violations were:")
                for v in procedures_update_diagnostics["attempts"][-1]["violations"]:
                    await aprint(" - " + v)

            retry_messages = []
            for i, attempt_ in enumerate(procedures_update_diagnostics["attempts"]):
                retry_messages.append(
                    {
                        "role": "user",
                        "content": f"During attempt {i + 1} of completion, your code violated some checks. Your code:\n\n<code>\n{attempt_['code']}\n</code>\n\nViolations:\n<violations>{attempt_['violations']}</violations>",
                    }
                )
            prompt_msgs = [
                {
                    "role": "system",
                    "content": "You are an excellent Python developer who writes Playwright automations.",
                },
                {
                    "role": "user",
                    "content": instructions,
                },
                *retry_messages,
            ]
            response = await lm(
                prompt_msgs,
                json_schema=J.cot_schema("python_code"),
                key="update_knowledge_base",
            )
            updated_code: str = response["python_code"]
            updated_code = (
                updated_code.replace("```python3", "")
                .replace("```python", "")
                .replace("```", "")
                .strip()
            )
            procedures_update_diagnostics["attempts"].append(
                {
                    "code": updated_code,
                    "violations": [],
                    "cot": response["step_by_step_reasoning"],
                }
            )

            await aprint("Resulting code:")
            await aprint(updated_code)

            # Check for violations.
            violations = check_code(updated_code, "import asyncio\n" + self.code)
            if len(violations) > 0:
                procedures_update_diagnostics["attempts"][-1]["violations"].extend(
                    violations
                )
                continue
            else:
                break

        self._apply(updated_code, reference)

        return {
            "procedures": procedures_update_diagnostics,
            "semantics": semantic_update_diagnostics,
        }

    def save(self, prefix_path: str):
        with open(prefix_path + "_code.py", "w") as f:
            f.write(self.code)

        with open(prefix_path + "_metadata.json", "w") as f:
            json.dump(self.metadata, f, indent=2)

        with open(prefix_path + "_semantic_knowledge.txt", "w") as f:
            f.write(self.semantic_knowledge)

    def is_tested(self, function_name: str) -> bool:
        return function_name in self.metadata["functions"] and (
            self.metadata["functions"][function_name]["test_count"] > 0
        )

    def get_functions(self, force_return_all=False) -> list[Function]:
        tree = ast.parse(self.code)
        functions = [
            f
            for f in tree.body
            if isinstance(f, (ast.AsyncFunctionDef, ast.FunctionDef))
            and (force_return_all or not self.hide_unverified or self.is_tested(f.name))
        ]
        lines = self.code.split("\n")
        return [
            {
                "name": f.name,
                "args": generate_schema(f),
                "docstring": ast.get_docstring(f) or "",
                "source": "\n".join(lines[f.lineno - 1 : f.end_lineno]),
                "is_synchronous": isinstance(f, ast.FunctionDef),
            }
            for f in functions
        ]

    def get_untested_functions(self) -> list[Function]:
        return [f for f in self.get_functions() if not self.is_tested(f["name"])]

    def get_tools_for_openai(self) -> list[ChatCompletionToolParam]:
        return [
            get_openai_chat_tool_param(function) for function in self.get_functions()
        ]

    def get_tools_for_openai_responses(self) -> list[FunctionToolParam]:
        return [
            get_openai_responses_tool_param(function)
            for function in self.get_functions()
        ]

    def get_functions_string(
        self,
        format: Literal["code", "pretty"] = "code",
        only_verified: bool = False,
        extra_functions: list[str] = [],
    ):
        fns = [
            f
            for f in self.get_functions()
            if f["name"] in extra_functions
            or (not only_verified or self.is_tested(f["name"]))
        ]
        return fns, "\n\n".join(
            [
                f["source"] if format == "code" else format_function_as_pretty_string(f)
                for f in fns
            ]
        )

    async def retrieve(self, task: str, lm: LM) -> tuple[list[Function], str, str]:
        skills = self.get_functions()

        if len(skills) == 0:
            return [], "", "<no skills available>"

        response = await lm(
            [
                {
                    "role": "user",
                    "content": predict_relevant_functions_templ(
                        function_space=skills, task=task
                    ),
                }
            ],
            json_schema=J.struct(
                step_by_step_reasoning=J.string(),
                relevant_function_names=J.list_of(J.struct(name=J.string())),
            ),
        )
        fns_string = ""
        valid_functions = []
        for function_name_struct in response["relevant_function_names"]:
            function_name = function_name_struct["name"]
            if "(" in function_name:
                function_name = function_name[: function_name.index("(")]
            function = next((f for f in skills if f["name"] == function_name), None)
            if function is not None:
                fns_string += format_function_as_pretty_string(function)
                valid_functions.append(function)
            else:
                await aprint(
                    f"Warning: function returned from the retrieval step was not found in knowledge base: {function_name}"
                )

        return (valid_functions, fns_string, response["step_by_step_reasoning"])

    def get_browser_use_controller(self, function_names: list[str], debug=False):
        """
        Create a controller for interfacing with Browser-Use.

        For example,

        ```python
        from skillweaver.knowledge_base import load_knowledge_base
        from skillweaver.lm import LM
        from browser_use import Agent

        lm = LM('gpt-4o')
        kb = load_knowledge_base("path/to/knowledge_base")
        task = ...
        (functions, _, _) = kb.retrieve(task, lm)
        controller = kb.get_browser_use_controller(functions)
        agent = Agent(
            task=task,
            controller=controller,
        )
        ```

        NOTE: Exception tracking cannot be done with Browser Use controller.
        If used in a subprocess, this function must be instantiated after
        containers have been created and environment variables have been set
        appropriately.
        """

        # Perform import inside function in case people don't want to install browser-use.
        from browser_use import Controller

        # Functions that were parsed using the abstract syntax tree.
        parsed_functions = {
            function["name"]: function
            for function in self.get_functions(force_return_all=True)
        }
        assert all(
            function_name in parsed_functions for function_name in function_names
        ), "All function names must be present in the knowledge base."

        controller = Controller()

        # Capture functions
        CAPTURE_CODE_SNIPPET = f"""
for function_name in {function_names}:
    functions[function_name] = locals()[function_name]
"""

        IMPORTS = "import asyncio, re"

        CODE = f"""
{IMPORTS}

{self.code}

{CAPTURE_CODE_SNIPPET}     
"""

        # Extract pointers to the function objects
        function_objects = {}
        exec(CODE, globals(), {"functions": function_objects})

        # Identify function parameters.
        function_docs = {
            function_name: _get_unindented_docstring(function)
            for function_name, function in parsed_functions.items()
        }

        # Set up a sandbox code block for the functions to be added.
        sandbox_code = ""
        for function_name, function in parsed_functions.items():
            if function_name not in function_names:
                continue
            
            function_ast = ast.parse(function["source"]).body[0]
            assert isinstance(function_ast, (ast.FunctionDef, ast.AsyncFunctionDef))

            for arg in function_ast.args.args:
                if arg.arg == "page":
                    # Rename first 'page' parameter to 'browser' (which is what browser-use expects)
                    arg.annotation = None
                    arg.arg = "browser"
                else:
                    # Add 'str' annotations to unannotated arguments.
                    if arg.annotation is None:
                        arg.annotation = ast.Name(id="str")

            modified_signature_function_source = ast_to_source(function_ast)
            modified_signature_string = modified_signature_function_source[
                : modified_signature_function_source.index(")") + 1
            ]

            if not isinstance(function_ast, ast.AsyncFunctionDef):
                modified_signature_string = "async " + modified_signature_string
            maybe_await = "await " if not function["is_synchronous"] else ""
            sandbox_code += f"""

@controller.action(function_docs['{function_name}'])
{modified_signature_string}:
    global function_objects
    page = await browser.get_current_page()
    arguments = {{k: v for k, v in locals().items() if k not in ['page', 'browser']}}
    return {maybe_await} function_objects['{function_name}'](page, **arguments)

            """

        if debug:
            with open("sandbox_code.py", "w") as f:
                f.write(sandbox_code)

            print(function_objects.keys())

        exec(
            sandbox_code,
            {
                **globals(),
                "function_objects": function_objects,
                "function_docs": function_docs,
                "controller": controller,
            },
        )

        return controller


def load_knowledge_base(prefix_path: str, discard_references=False):
    with open(prefix_path + "_code.py") as f:
        code = f.read()

    try:
        with open(prefix_path + "_metadata.json") as f:
            metadata = json.load(f)
    except FileNotFoundError:
        metadata = {
            "functions": {
                f.name: {"version": 0, "test_count": 0, "references": []}
                for f in ast.parse(code).body
                if isinstance(f, ast.AsyncFunctionDef) and f.name != "main"
            }
        }

    try:
        with open(prefix_path + "_semantic_knowledge.txt") as f:
            semantic_knowledge = f.read()
    except FileNotFoundError:
        semantic_knowledge = ""

    kb = KnowledgeBase(code, metadata, semantic_knowledge)

    if discard_references:
        for fn_name in kb.metadata["functions"].keys():
            kb.metadata["functions"][fn_name]["references"] = []

    return kb
