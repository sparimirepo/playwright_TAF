import pytest
from pageObjects.admin.AdminPage import AdminPage
from pageObjects.common_pages.OverviewPage import OverviewPage
from utils.NextGenUtilities import NextgenUtils


@pytest.mark.usefixtures("browser_context", "configuration","utils_setup","initialize")
class TestUserManagement:

    overview_page: OverviewPage
    admin_page: AdminPage
    nextgen: NextgenUtils

    @pytest.fixture(scope="class")
    def initialize(self, request, browser_context, configuration,utils_setup):
        """Login to CIC App with Admin credentials"""
        cls = request.cls
        cls.browser_context = browser_context
        cls.configuration = configuration
        cls.nextgen.login(configuration["username"], configuration["password"])
        cls.overview_page = OverviewPage(browser_context)
        cls.admin_page = AdminPage(browser_context)

    def test_navigation_to_overview_page(self):
        """Validate user landed on overview page"""
        self.overview_page.validate_overview_page_header()

    def test_navigation_to_admin_page(self):
        """Validate user landed on admin page"""
        self.overview_page.navigate_to_admin_page()
        self.admin_page.validate_admin_page_header()
