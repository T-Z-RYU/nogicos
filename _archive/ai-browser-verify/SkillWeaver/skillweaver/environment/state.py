import json
from dataclasses import dataclass
from typing import Literal, Optional
from urllib.parse import urlparse, urlunparse
import PIL.Image
from playwright.async_api import Locator, Page
from typing_extensions import TypedDict
from skillweaver.environment.a11y import (
    AXTree,
    filter_out_of_view_nodes,
    serialize_accessibility_tree,
)


def get_base_url(url: str):
    # Parse the URL into components and contruct new URL without the path, query, and fragment parts
    parsed_url = urlparse(url)
    return urlunparse((parsed_url.scheme, parsed_url.netloc, "", "", "", ""))


class DialogState(TypedDict):
    type: Literal["alert", "confirm", "prompt", "beforeunload"]
    message: Optional[str]


@dataclass
class State:
    id: str
    url: str
    title: str
    timestamp: float
    screenshot: PIL.Image.Image
    dom: dict
    dialog: Optional[DialogState]
    accessibility_tree: AXTree

    @property
    def relative_url(self):
        after_protocol = self.url[self.url.index("://") + 3 :]
        return after_protocol[after_protocol.index("/") :]

    def get_axtree_mcq(self, page: Page) -> tuple[str, dict[str, tuple[int, Locator]]]:
        string, choices = serialize_accessibility_tree(
            filter_out_of_view_nodes(self.accessibility_tree),  # type: ignore
            add_mcq=True,
            root_locator=page.get_by_role("document"),
            base_url=get_base_url(self.url),
        )
        assert all(locator for _id, locator in choices.values())
        return string, choices  # type: ignore

    def get_axtree_string(self):
        string, _ = serialize_accessibility_tree(
            filter_out_of_view_nodes(self.accessibility_tree),  # type: ignore
            base_url=get_base_url(self.url),
        )
        return string

    def save(self, out_dir: str, prefix: str):
        self.screenshot.save(f"{out_dir}/{prefix}_screenshot.png")

        with open(f"{out_dir}/{prefix}_dom.json", "w") as f:
            json.dump(self.dom, f)

        with open(f"{out_dir}/{prefix}_ax_v2.json", "w") as f:
            json.dump(self.accessibility_tree, f)

        with open(f"{out_dir}/{prefix}_misc.json", "w") as f:
            misc_data = {
                "id": self.id,
                "url": self.url,
                "title": self.title,
                "dialog": self.dialog,
                "timestamp": self.timestamp,
            }

            json.dump(misc_data, f)

    @classmethod
    def load(cls, out_dir: str, prefix: str, weak=False):
        if weak:
            screenshot = None
        else:
            screenshot = PIL.Image.open(f"{out_dir}/{prefix}_screenshot.png")

        with open(f"{out_dir}/{prefix}_dom.json") as f:
            dom = json.load(f)

        with open(f"{out_dir}/{prefix}_ax_v2.json") as f:
            accessibility_tree: AXTree = json.load(f)

        with open(f"{out_dir}/{prefix}_misc.json") as f:
            misc_data = json.load(f)

        return State(
            id=misc_data["id"],
            url=misc_data["url"],
            title=misc_data["title"],
            timestamp=misc_data["timestamp"],
            dialog=misc_data["dialog"],
            screenshot=screenshot,  # type: ignore
            dom=dom,
            accessibility_tree=accessibility_tree,
        )
