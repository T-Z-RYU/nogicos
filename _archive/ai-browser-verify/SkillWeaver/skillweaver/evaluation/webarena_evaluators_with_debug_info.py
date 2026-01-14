"""base class for evaluation"""

# answer string match
import asyncio
import collections
import html
import json
import time
import urllib.parse
from pathlib import Path

from nltk.tokenize import word_tokenize
from playwright.async_api import CDPSession, Page
from typing_extensions import TypedDict

from skillweaver.environment import State
from skillweaver.evaluation.webarena_config import _resolve_start_url
from skillweaver.evaluation.webarena_helper_functions import (
    PseudoPage, gitlab_get_project_member_role, llm_fuzzy_match, llm_ua_match,
    reddit_get_post_url, shopping_get_latest_order_url,
    shopping_get_sku_latest_review_author,
    shopping_get_sku_latest_review_rating)

Trajectory = tuple[list[State], list[dict]]


class CheckResult(TypedDict):
    success: bool
    reason: str


class Outcome(TypedDict):
    score: float
    checks: list[CheckResult]


class Evaluator(object):
    def __init__(self, eval_tag: str = "") -> None:
        self.eval_tag = eval_tag

    async def __call__(
        self,
        trajectory: Trajectory,
        config_file: Path | str,
        page: Page,
        client: CDPSession,
    ) -> Outcome:
        raise NotImplementedError


class StringEvaluator(Evaluator):
    """Check whether the answer is correct with:
    exact match: the answer is exactly the same as the reference answer
    must include: each phrase in the reference answer must be included in the answer
    fuzzy match: the answer is similar to the reference answer, using LLM judge
    """

    @staticmethod
    def clean_answer(answer: str) -> str:
        answer = answer.strip()
        if answer.startswith("'") and answer.endswith("'"):
            answer = answer[1:-1]
        elif answer.startswith('"') and answer.endswith('"'):
            answer = answer[1:-1]
        return answer.lower()

    @staticmethod
    def exact_match(ref: str, pred: str) -> float:
        return float(
            StringEvaluator.clean_answer(pred) == StringEvaluator.clean_answer(ref)
        )

    @staticmethod
    def must_include(ref: str, pred: str, tokenize: bool = False) -> float:
        clean_ref = StringEvaluator.clean_answer(ref)
        clean_pred = StringEvaluator.clean_answer(pred)
        # tokenize the answer if the ref is a single word
        # prevent false positive (e.g, 0)
        if tokenize and len(clean_ref) == 1 and len(word_tokenize(clean_ref)) == 1:
            tok_pred = word_tokenize(clean_pred)
            return float(clean_ref in tok_pred)
        else:
            return float(clean_ref in clean_pred)

    @staticmethod
    def fuzzy_match(ref: str, pred: str, intent: str) -> float:
        return llm_fuzzy_match(pred, ref, intent)

    @staticmethod
    def ua_match(ref: str, pred: str, intent: str) -> float:
        return llm_ua_match(pred, ref, intent)

    async def __call__(
        self,
        trajectory: Trajectory,
        config_file: Path | str,
        page: Page | None = None,
        client: CDPSession | None = None,
    ) -> Outcome:
        with open(config_file, "r") as f:
            configs = json.load(f)

        states, actions = trajectory

        if actions[-1].get("terminate_with_result"):
            pred = self.clean_answer(actions[-1]["terminate_with_result"])
        elif actions[-1].get("name") == "terminate":
            pred = self.clean_answer(actions[-1]["args"]["result"])
        else:
            # Was likely truncated.
            return {
                "score": 0,
                "checks": [
                    {
                        "reason": "Last action was non-terminal (likely truncated)",
                        "success": False,
                    }
                ],
            }

        score = 1.0

        checks = []
        for approach, value in configs["eval"]["reference_answers"].items():
            match approach:
                case "exact_match":
                    if not self.exact_match(ref=value, pred=pred):
                        score = 0
                        checks.append(
                            {
                                "success": False,
                                "reason": f"Exact match failed between ref={repr(value)} and pred={repr(pred)}",
                            }
                        )

                case "must_include":
                    assert isinstance(value, list)
                    for must_value in value:
                        if not self.must_include(
                            ref=must_value,
                            pred=pred,
                            tokenize=(len(value) == 1),
                        ):
                            score = 0
                            checks.append(
                                {
                                    "success": False,
                                    "reason": f"Must include failed between ref={repr(must_value)} (of {repr(value)}) and pred={repr(pred)}",
                                }
                            )
                case "fuzzy_match":
                    intent = configs["intent"]
                    if value == "N/A":
                        # if the instruction only asks the model to generate N/A when encountering an unachievable task
                        # without more concrete reasons
                        score *= self.exact_match(ref=value, pred=pred)
                        # if the instruction also asks the model to generate the reason why the task is unachievable
                        # this should be the default as it will prevent false positive N/A`
                        if score != 1:
                            score = bool(
                                self.ua_match(
                                    intent=intent,
                                    ref=configs["eval"]["string_note"],
                                    pred=pred,
                                )
                            )
                            checks.append(
                                {
                                    "success": score,
                                    "reason": f"ua_match for intent={repr(intent)}, ref={repr(configs['eval']['string_note'])}, pred={repr(pred)}",
                                }
                            )
                    else:
                        assert isinstance(value, list)
                        for reference in value:
                            if not self.fuzzy_match(
                                ref=reference, pred=pred, intent=intent
                            ):
                                score = 0
                                checks.append(
                                    {
                                        "success": False,
                                        "reason": f"fuzzy_match for ref={repr(reference)}, pred={repr(pred)}, intent={repr(intent)}",
                                    }
                                )
        return {"score": score, "checks": checks}


def clean_url(url: str) -> str:
    url = str(url)
    url = url.rstrip("/")
    return url


def parse_url(url: str) -> tuple[str, dict[str, list[str]]]:
    """Parse a URL into its base, path, and query components."""
    parsed_url = urllib.parse.urlparse(url)
    base_path = parsed_url.netloc + parsed_url.path
    query = urllib.parse.parse_qs(parsed_url.query)
    return base_path, query


def parse_urls(
    urls: list[str],
) -> tuple[list[str], dict[str, set[str]]]:
    """Parse a list of URLs."""
    base_paths = []
    queries = collections.defaultdict(set)
    for url in urls:
        base_path, query = parse_url(url)
        base_paths.append(base_path)
        for k, v in query.items():
            queries[k].update(v)
    return base_paths, queries


class URLEvaluator(Evaluator):
    """Check URL matching"""

    async def __call__(
        self,
        trajectory: Trajectory,
        config_file: Path | str,
        page: Page,
        client: CDPSession | None = None,
    ) -> Outcome:
        with open(config_file, "r") as f:
            configs = json.load(f)

        states, actions = trajectory
        checks: list[CheckResult] = []

        url = states[-1].url
        pred = clean_url(url)
        ref_urls = configs["eval"]["reference_url"].split(" |OR| ")
        ref_urls = [_resolve_start_url(url) for url in ref_urls]
        ref_urls = [clean_url(url) for url in ref_urls]
        matching_rule = configs["eval"].get("url_note", "GOLD in PRED")
        if matching_rule == "GOLD in PRED":
            ref_base_paths, ref_queries = parse_urls(ref_urls)
            pred_base_paths, pred_query = parse_url(pred)

            base_score = float(
                any(
                    [
                        ref_base_path in pred_base_paths
                        for ref_base_path in ref_base_paths
                    ]
                )
            )
            checks.append(
                {
                    "success": bool(base_score),
                    "reason": f"pred_base_paths={repr(pred_base_paths)} and ref_base_paths={repr(ref_base_paths)} "
                    + ("intersect" if base_score else "don't intersect"),
                }
            )
            query_score = 1.0
            for k, possible_values in ref_queries.items():
                query_score *= float(
                    any(
                        possible_ref_value in pred_query.get(k, [])
                        for possible_ref_value in possible_values
                    )
                )
            if len(ref_queries) > 0:
                checks.append(
                    {
                        "success": bool(query_score),
                        "reason": (
                            "query parameter check failed",
                            "query parameter check succeeded",
                        )[int(query_score)],
                    }
                )
            score = base_score * query_score

        else:
            raise ValueError(f"Unknown matching rule: {matching_rule}")

        return {"score": score, "checks": checks}


class HTMLContentEvaluator(Evaluator):
    """Check whether the contents appear in the page"""

    async def __call__(
        self,
        trajectory: Trajectory,
        config_file: Path | str,
        page: Page,
        client: CDPSession | None = None,
    ) -> Outcome:
        with open(config_file, "r") as f:
            configs = json.load(f)

        targets = configs["eval"]["program_html"]

        score = 1.0
        checks: list[CheckResult] = []
        for target in targets:
            target_url: str = target["url"]  # which url to check
            if target_url.startswith("func"):
                func = target_url.split("func:")[1]
                func = func.replace("__last_url__", page.url)
                target_url = eval(func)

            locator: str = target["locator"]  # js element locator

            # navigate to that url
            if target_url != "last":
                target_url = _resolve_start_url(target_url)
                await page.goto(target_url)
                await page.wait_for_load_state("load")
                await asyncio.sleep(3)  # TODO [shuyanzh]: fix this hard-coded sleep

            # empty, use the full page
            if not locator.strip():
                selected_element = await page.content()
            # use JS to select the element
            elif locator.startswith("document.") or locator.startswith("[...document."):
                if "prep_actions" in target:
                    try:
                        for prep_action in target["prep_actions"]:
                            await page.evaluate(f"() => {prep_action}")
                    except Exception:
                        pass
                try:
                    selected_element = str(await page.evaluate(f"() => {locator}"))
                    if not selected_element:
                        selected_element = ""
                except Exception:
                    # the page is wrong, return empty
                    selected_element = ""
            # run program to call API
            elif locator.startswith("func:"):  # a helper function
                func = locator.split("func:")[1]
                func = func.replace("__page__", "page")
                selected_element = eval(func)
            else:
                raise ValueError(f"Unknown locator: {locator}")

            selected_element = html.unescape(selected_element)

            if "exact_match" in target["required_contents"]:
                required_contents = target["required_contents"]["exact_match"]
                cur_score = StringEvaluator.exact_match(
                    ref=required_contents, pred=selected_element
                )
                if not cur_score:
                    score = 0
                    checks.append(
                        {
                            "success": False,
                            "reason": f"Exact match failed between ref={repr(required_contents)} and pred={repr(selected_element)}",
                        }
                    )

                score *= float(cur_score)
                # print(f"[exact match] {cur_score}, selected element: {selected_element}, required contents: {required_contents}")
            elif "must_include" in target["required_contents"]:
                required_contents = target["required_contents"]["must_include"]
                assert isinstance(required_contents, list)
                for content in required_contents:
                    content_or = content.split(" |OR| ")
                    cur_score = any(
                        [
                            StringEvaluator.must_include(
                                ref=content,
                                pred=selected_element,
                                tokenize=False,
                            )
                            for content in content_or
                        ]
                    )
                    if not cur_score:
                        score = 0
                        checks.append(
                            {
                                "success": False,
                                "reason": f"Must include failed between ref={repr(content)} (of {repr(content_or)}) and pred={repr(selected_element)}",
                            }
                        )

                    score *= float(cur_score)
                    # print(f"[must include] {cur_score}, selected element: {selected_element}, required contents: {content_or}")
            else:
                raise ValueError(
                    f"Unknown required_contents: {target['required_contents'].keys()}"
                )
        return {"score": score, "checks": checks}


class EvaluatorComb:
    def __init__(self, evaluators: list[Evaluator]) -> None:
        self.evaluators = evaluators

    async def __call__(
        self,
        trajectory: Trajectory,
        config_file: Path | str,
        page: Page,
        client: CDPSession,
    ) -> Outcome:
        score = 1.0
        checks = []
        for evaluator in self.evaluators:
            result = await evaluator(trajectory, config_file, page, client)
            score *= result["score"]
            checks += result["checks"]
        return {"score": score, "checks": checks}


def evaluator_router(config_file: Path | str) -> EvaluatorComb:
    """Router to get the evaluator class"""
    with open(config_file, "r") as f:
        configs = json.load(f)

    eval_types = configs["eval"]["eval_types"]
    evaluators: list[Evaluator] = []
    for eval_type in eval_types:
        match eval_type:
            case "string_match":
                evaluators.append(StringEvaluator())
            case "url_match":
                evaluators.append(URLEvaluator())
            case "program_html":
                evaluators.append(HTMLContentEvaluator())
            case _:
                raise ValueError(f"eval_type {eval_type} is not supported")

    return EvaluatorComb(evaluators)
