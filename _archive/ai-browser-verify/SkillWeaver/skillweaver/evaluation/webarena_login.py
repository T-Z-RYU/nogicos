"""Script to automatically login each website"""

import asyncio
import json
import os
import subprocess
import sys
import uuid

from skillweaver.evaluation.webarena_config import ACCOUNTS
from skillweaver.environment import make_browser
from playwright.async_api import async_playwright

HEADLESS = True
SLOW_MO = 0
SHOPPING_ADMIN = "ec2-18-118-35-60.us-east-2.compute.amazonaws.com:7780/admin"


# We can do this cheaply on WebArena. May want to improve for live websites.
# `comb` is a dictionary of website name -> host.
# example `comb``: {"shopping": "127.0.0.1:8003"}
async def webarena_renew_comb(comb: dict[str, str], path: str):
    comb = {k: v[7:] if v.startswith("http://") else v for k, v in comb.items()}

    # Returns the filename.
    async with async_playwright() as p:
        browser = await make_browser(
            p,
            "http://" + list(comb.values())[0],
            headless=HEADLESS,
            navigation_timeout=30000,
            timeout=30000,
        )
        page = browser.active_page

        for key, host in comb.items():
            if key == "shopping":
                username = ACCOUNTS["shopping"]["username"]
                password = ACCOUNTS["shopping"]["password"]
                print(f"Logging into {key} at {host}")
                print(f"user: {username}, pass: {password}")
                await page.goto(f"http://{host}/customer/account/login/")
                await page.get_by_label("Email", exact=True).fill(username)
                await page.get_by_label("Password", exact=True).fill(password)
                await page.get_by_role("button", name="Sign In").click()
                # Wait for the request to finish.
                await page.wait_for_load_state("networkidle")

            if key == "reddit":
                username = ACCOUNTS["reddit"]["username"]
                password = ACCOUNTS["reddit"]["password"]
                print(f"Logging into {key} at {host}")
                print(f"user: {username}, pass: {password}")
                await page.goto(f"http://{host}/login")
                await page.get_by_label("Username").fill(username)
                await page.get_by_label("Password").fill(password)
                await page.get_by_role("button", name="Log in").click()
                # Wait for the request to finish.
                await page.wait_for_load_state("networkidle")

            if key == "shopping_admin":
                username = ACCOUNTS["shopping_admin"]["username"]
                password = ACCOUNTS["shopping_admin"]["password"]
                print(f"Logging into {key} at {host}")
                print(f"user: {username}, pass: {password}")
                await page.goto(f"http://{host}/admin")
                await page.get_by_placeholder("user name").fill(username)
                await page.get_by_placeholder("password").fill(password)
                await page.get_by_role("button", name="Sign in").click()
                # Wait for the request to finish.
                await page.wait_for_load_state("networkidle")

            if key == "gitlab":
                username = ACCOUNTS["gitlab"]["username"]
                password = ACCOUNTS["gitlab"]["password"]
                print(f"Logging into {key} at {host}")
                print(f"user: {username}, pass: {password}")
                await page.goto(f"http://{host}/users/sign_in")
                await page.get_by_test_id("username-field").click()
                await page.get_by_test_id("username-field").fill(username)
                await page.get_by_test_id("username-field").press("Tab")
                await page.get_by_test_id("password-field").fill(password)
                await page.get_by_test_id("sign-in-button").click()
                # Wait for the request to finish.
                # await page.wait_for_load_state("load")
                await asyncio.sleep(5)

        await browser.context.storage_state(path=path)
        await browser.close()

    os._exit(0)


def login_subprocess(comb: dict[str, str]):
    auth_dir = os.path.dirname(__file__) + "/.auth"
    if not os.path.exists(auth_dir):
        os.makedirs(auth_dir)
    auth_path = os.path.abspath(f"{auth_dir}/{uuid.uuid4().hex}.json")
    print("=====auth_path", auth_path)

    command = [
        "python3",
        "-m",
        "skillweaver.evaluation.webarena_login",
        json.dumps({"comb": comb, "path": auth_path}),
    ]
    print("=====command", command)
    subprocess.run(command)
    if not os.path.exists(auth_path):
        return None
    else:
        return auth_path


async def login_subprocess_async(comb: dict[str, str]):
    from asyncio.subprocess import create_subprocess_exec

    auth_dir = os.path.dirname(__file__) + "/.auth"
    if not os.path.exists(auth_dir):
        os.makedirs(auth_dir)
    auth_path = os.path.abspath(f"{auth_dir}/{uuid.uuid4().hex}.json")
    proc = await create_subprocess_exec(
        "python3",
        "-m",
        "skillweaver.evaluation.webarena_login",
        json.dumps({"comb": comb, "path": auth_path}),
    )
    await proc.communicate()
    if not os.path.exists(auth_path):
        return None
    else:
        return auth_path


async def test_shopping_admin():
    """Test function for shopping_admin login"""
    comb = {"shopping_admin": SHOPPING_ADMIN}
    auth_dir = os.path.dirname(__file__) + "/.auth"
    if not os.path.exists(auth_dir):
        os.makedirs(auth_dir)
    auth_path = os.path.abspath(f"{auth_dir}/{uuid.uuid4().hex}.json")

    print(f"Starting shopping_admin login test...")
    print(f"Testing URL: {SHOPPING_ADMIN}")
    await webarena_renew_comb(comb, auth_path)


if __name__ == "__main__":
    # asyncio.run(test_shopping_admin())
    data = json.loads(sys.argv[1])
    asyncio.run(webarena_renew_comb(data["comb"], data["path"]))
