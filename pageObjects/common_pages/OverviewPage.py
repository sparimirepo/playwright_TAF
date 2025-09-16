from utils.CommonUtilities import CommonUtilities
from utils.NextGenUtilities import NextgenUtils
from utils.logging.logger_utils import log_step

class OverviewPage(CommonUtilities, NextgenUtils):

    admin_module_tile = "//li[@data-id='Administration']//a"
    safety_module_tile = "//li[@data-id='Safety']//a"

    def __init__(self, page):
        CommonUtilities.__init__(self, page)
        NextgenUtils.__init__(self, page)

    def validate_overview_page_header(self):
        self.assert_element_visible("role", {"role": "heading", "name": "Overview"}, "Overview Page Header")

    def navigate_to_admin_page(self):
        log_step("Navigating to Administration Page")
        self.click_element("xpath",self.admin_module_tile,"Administration Page")
        self.page.wait_for_load_state("networkidle")

    def navigate_to_safety_page(self):
        log_step("Navigating to Safety Page")
        self.click_element("xpath",self.safety_module_tile,"Safety Page")
        self.page.wait_for_load_state("networkidle")
