from playwright.sync_api import Page

class RiskForecastPage(Page):
    def __init__(self, page: Page):
        self.page = page;
        self.userName = page.locator("");
        self.userPassword = page.locator("");