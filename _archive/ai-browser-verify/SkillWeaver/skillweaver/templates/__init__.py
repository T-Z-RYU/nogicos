import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from skillweaver.knowledge_base.knowledge_base import Function

base = os.path.abspath(os.path.dirname(__file__))

file = lambda x: open(base + "/" + x, encoding="utf-8").read()
kb_procedural_update_base = file("kb_procedural_update_base.md")
kb_procedural_update_single = file("kb_procedural_update_single.md")
kb_procedural_update_multiple = file("kb_procedural_update_multiple.md")
codegen_prompt_template = file("codegen.md")
propose_skill_template = file("propose_skill.md")
generate_practice_args_template = file("generate_practice_args.md")
axtree_intro = file("axtree_intro.md")
predict_relevant_functions = file("predict_relevant_functions.md")
cua_system_prompt = file("cua_system_prompt.md")


# Just for nice typing
def codegen_templ(
    ax_tree: str,
    procedural_knowledge: str,
    previous_actions: str,
    task: str,
    title: str,
    url: str,
    is_first_step: bool,
    is_eval_task: bool,
    as_reference_only: bool,
):
    return codegen_prompt_template.format(
        ax_tree=ax_tree,
        axtree_intro=axtree_intro,
        # semantic_knowledge=semantic_knowledge,
        function_usage_instructions=(
            "You also have this library of Python functions available to you. Think carefully about whether you think these can be used in your code. If you conclude that you can use a function, then simply call it. These functions are all available as global variables."
            if not as_reference_only
            else "You have practiced the below functions. Note that they are only available for reference. You cannot 'call' them, but you should refer to them when generating code."
        ),
        functions=procedural_knowledge,
        title_repr=repr(title),
        url_repr=repr(url),
        previous_actions=previous_actions,
        task=task,
        step_specific_instructions=(
            "Because you are on the first step, please use your existing knowledge of the website to create an overall plan for how to achieve the task."
            if is_first_step
            else ""
        ),
        additional_instructions=(
            "The task is guaranteed to be possible to complete in an exact sense. Additionally, during each step, explicitly reason about the utility of each of the Python functions defined in the knowledge base with respect to the task at hand. When you are done, provide your final answer as a single result: for example, if asked for a number, simply return the number alone. If asked for the name of something, return only the name, and no additional text. Don't add any extra text to `terminate_with_result` beyond your answer. Do not overcomplicate the task; do what it asks for, and nothing more."
            if is_eval_task
            else ""
        )
        + "\n\nDo not interact with the Advanced Reporting tab if you are using Magento Admin.",
    )


def kb_procedural_update_single_templ(
    procedural_knowledge: str,
    semantic_knowledge: str,
    action_history: str,
    intended_task: str,
    feedback: str = "",
):
    return kb_procedural_update_single.format(
        kb_procedural_update_base=kb_procedural_update_base,
        procedural_knowledge=procedural_knowledge,
        semantic_knowledge=semantic_knowledge,
        action_history=action_history,
        intended_task=intended_task,
        feedback=feedback,
    ) + (
        f"\n\nFeedback for whether you got the right answer:\n<feedback>\n{feedback}\n</feedback>"
        if feedback
        else ""
    )


def kb_procedural_update_multiple_templ(
    procedural_knowledge: str,
    semantic_knowledge: str,
    previous_trials: str,
    intended_task: str,
    feedback: str = "",
):
    return kb_procedural_update_multiple.format(
        kb_procedural_update_base=kb_procedural_update_base,
        procedural_knowledge=procedural_knowledge,
        semantic_knowledge=semantic_knowledge,
        previous_trials=previous_trials,
        intended_task=intended_task,
    ) + (
        f"\n\nFeedback for whether you got the right answer:\n<feedback>\n{feedback}\n</feedback>"
        if feedback
        else ""
    )


def propose_skill_templ(
    procedural_knowledge: str,
    semantic_knowledge: str,
    ax_tree: str,
    is_live_website: bool,
):
    safety_instructions = """
Discard any skills that involve:
 - the creation of user accounts
 - publication/submission of content
 - reservation of time slots, tickets, event slots, or other scarce resources
 - submission of support requests or feedback
 - interaction with promotional material
 - in general, anything that could impact other users of the website

Then write the list of skills that satisfy these criteria.
""".strip()

    return propose_skill_template.format(
        procedural_knowledge=procedural_knowledge,
        semantic_knowledge=semantic_knowledge,
        safety_instructions=safety_instructions if is_live_website else "",
        ax_tree=ax_tree,
    )


def generate_practice_args(name: str, signature: str, ax_tree: str):
    return generate_practice_args_template.format(
        name=name, signature=signature, ax_tree=ax_tree
    )


def predict_relevant_functions_templ(function_space: list["Function"], task: str):
    from skillweaver.knowledge_base.knowledge_base import format_function_as_pretty_string

    return predict_relevant_functions.format(
        function_space="\n\n".join(
            format_function_as_pretty_string(f) for f in function_space
        ),
        repr_task=repr(task),
    )
