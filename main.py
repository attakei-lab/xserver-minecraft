from __future__ import annotations

import time
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

from playwright.sync_api import sync_playwright

if TYPE_CHECKING:
    from playwright.sync_api import Page


class Settings(TypedDict):
    username: str
    password: str
    server: str


here = Path(__file__).parent
config_toml = here.joinpath("config.toml")


def login(page: Page, settings: Settings) -> Page:
    page.goto("https://secure.xserver.ne.jp/xapanel/login/xmgame")
    # Login
    form = page.locator("#login_area")
    form.locator("#memberid").fill(settings["username"])
    form.locator("#user_password").fill(settings["password"])
    form.locator("input[type='submit']").click()
    # Select server
    page.locator(
        f"a[href='/xapanel/xmgame/jumpvps/?id={settings['serverid']}']"
    ).click()
    return page


def try_extend(page: Page) -> bool:
    page.get_by_text("アップグレード・期限延長", exact=True).click()
    msg = page.locator(".freePlanMessage")
    if msg.count() > 0 and "期限の延長は行えません" in msg[0].text_content():
        print("SKIP extend")
        return False
    page.get_by_text("期限を延長する", exact=True).click()
    page.get_by_text("確認画面に進む", exact=True).click()
    page.get_by_text("期限を延長する", exact=True).click()
    print("DONE extend")
    return True


def main():
    settings = tomllib.loads(config_toml.read_text())["account"]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page = login(page, settings)
        try_extend(page)
        time.sleep(5)
        browser.close()


if __name__ == "__main__":
    main()
