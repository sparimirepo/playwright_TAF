from playwright.sync_api import Page, expect

from utils.CommonUtilities import CommonUtilities
from utils.NextGenUtilities import NextgenUtils
from utils.logging.logger_utils import log_step, capture_and_log_failure


class SafetyPage:
    safety_header = "h1"

    def __init__(self, page: Page):
        self.page = page
        CommonUtilities.__init__(self, page)
        NextgenUtils.__init__(self, page)

    def validate_safety_page_header(self):
        log_step("Validating Safety Page Header")
        header = self.page.get_by_role("heading", name="Safety")
        # assert header.is_visible(), "Safety header is not visible"
        try:
            expect(header).to_be_visible()
        except AssertionError:
            capture_and_log_failure(self.page, step_name="Checking Safety Module Title")
            raise AssertionError("Checking Safety Module Title failed")
        log_step("Successfully validated Safety Page Header")

    def verify_safety_header(self):
        expected_text = "Safety1234"
        try:
            expect(self.page.locator(self.safety_header)).to_have_text(expected_text)
        except Exception:
            capture_and_log_failure(self.page, step_name="Checking Safety Module Title..!")
            raise AssertionError("Safety Header Text validation failed")
