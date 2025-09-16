import pytest
from pageObjects.common_pages.OverviewPage import OverviewPage
from pageObjects.safety.SafetyPage import SafetyPage
from utils.NextGenUtilities import NextgenUtils


@pytest.mark.usefixtures("browser_context", "configuration","utils_setup","initialize")
class TestSafety:

    overview_page: OverviewPage
    safety_page: SafetyPage
    nextgen: NextgenUtils

    @pytest.fixture(scope="class")
    def initialize(self, request, browser_context, configuration, utils_setup):
        """Login to CIC App with Admin credentials"""
        cls = request.cls
        cls.browser_context = browser_context
        cls.configuration = configuration

        cls.nextgen.login(configuration["username"], configuration["password"])
        cls.overview_page = OverviewPage(browser_context)
        cls.safety_page = SafetyPage(browser_context)

    def test_navigation_to_overview_page(self):
        """Validate user landed on overview page"""
        self.overview_page.validate_overview_page_header()

    def test_navigation_to_safety_page(self):
        """Validate user landed on safety page"""
        self.overview_page.navigate_to_safety_page()
        self.safety_page.validate_safety_page_header()
