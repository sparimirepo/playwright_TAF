from utils.CommonUtilities import CommonUtilities
from logging_config import global_logger
from utils.logging.logger_utils import log_step, capture_and_log_failure


class NextgenUtils:
    def __init__(self, page):
        self.page = page
        self.utils = CommonUtilities(page)

    """Logs into the CIC application using the provided username and password."""
    def login(self, username: str, password: str):
        try:
            log_step("Logging in as " + username)
            self.utils.fill_element("label", "User Name", username, "Username")
            log_step("Logging in as " + password)
            self.utils.fill_element("label", "Password", password, "Password")
            self.utils.click_element("role", {"role": "button", "name": "Sign In"}, "Sign In Button")
            self.page.wait_for_load_state("networkidle")
            log_step("Successfully Logged in")
        except Exception as e:
            capture_and_log_failure(f"Login failed: {str(e)}")
            raise
