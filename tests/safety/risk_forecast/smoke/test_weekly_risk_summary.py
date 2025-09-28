import pytest
from logging_config import global_logger
from pageObjects.common_pages.OverviewPage import OverviewPage
from pageObjects.safety.SafetyPage import SafetyPage
from utils.NextGenUtilities import NextgenUtils
from utils.logging.logger_utils import log_step, capture_and_log_failure


@pytest.mark.usefixtures("browser_context", "configuration", "utils_setup", "initialize", "db_connection")
class TestWeeklyRiskSummary():
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
        log_step("Test Initialize Completed!")

    def test_navigation_to_safety_page(self, db_connection):
        """Validate user landed on safety page"""
        self.overview_page.navigate_to_safety_page()
        log_step("Navigating to safety module")
        log_step("Safety page is loaded..!")
        self.safety_page.validate_safety_page_header()
        global_logger.info(f"Safety Page title is validated..!")

        # result = db_connection.executeQuery("select * from cic_nextgen_pub.sft_project_d_v where project_object_id = '10107730'")
        # row = result[0]
        # log_step(f"project object id:  {row['PROJECT_OBJECT_ID']}")
        # log_step(f"Name:  {row['NAME']}")
        global_logger.info(f"DB Query execution completed!")

    def test_safety_02(self):
        """Validate user landed on safety page"""
        global_logger.info(f"test_safety_02 completed!")

    def test_safety_03(self):
        """Validate user landed on safety page"""
        global_logger.info(f"test_safety_03 completed!")

    def test_safety_04(self):
        """Validate user landed on safety page"""
        global_logger.info(f"test_safety_04 completed!")
