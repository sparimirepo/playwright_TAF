
from utils.logging.logger_utils import log_step
from utils.CommonUtilities import CommonUtilities
from playwright.sync_api import Page, expect

class AdminPage(CommonUtilities):
    def __init__(self, page: Page):
        super().__init__(page)  # keeps CommonUtilities methods
        self.page = page
        self.form_iframe = self.page.frame_locator("iframe[src*='edit-cei-user']")

    def validate_admin_page_header(self):
        log_step("Validating Administration Page Header")
        self.assert_element_visible("role",{"role": "heading", "name": "Administration"},"Admin Page Header")


    def validate_admin_page_header(self):
        print("Validating Administration Page Header")
        header = self.page.get_by_role("heading", name="Administration")
        assert header.is_visible(), "Administration header is not visible"
        print("Successfully validated Administration Page Header")

    def navigate_to_user_management_page(self):
        print("Navigating to User Management Page")
        self.page.locator('a.rw-Card-fullLink[href*="user-management/cei-users"]').click()
        self.page.wait_for_load_state("networkidle")

    def click_on_add_user(self):
        add_user_button = self.page.locator('button[title="Add User"]')
        add_user_button.wait_for(state="visible", timeout=15000)
        add_user_button.wait_for(state="attached", timeout=15000)
        expect(add_user_button).to_be_enabled(timeout=15000)
        add_user_button.click(force=True)
        drawer_iframe = self.page.locator("iframe[src*='edit-cei-user']")
        drawer_iframe.wait_for(state="visible", timeout=20000)

    def fill_email(self, email):
        email_input = self.page.frame_locator("iframe[src*='edit-cei-user']").locator("#P70_EMAIL_input")
        email_input.wait_for(state="visible", timeout=20000)
        email_input.fill('')              # Clear field first
        email_input.fill(email)           # Fill instantly to avoid repeated auto-search triggers
        email_input.evaluate("el => el.blur()")  # Trigger blur event
        expect(email_input).to_have_value(email, timeout=5000)
        self.page.wait_for_timeout(500)  # Optional short wait for UI updates after auto-search

    def wait_until_email_filled_correctly(self, email):
        email_input = self.page.frame_locator("iframe[src*='edit-cei-user']").locator("#P70_EMAIL_input")
        expect(email_input).to_have_value(email, timeout=5000)

    def fill_username(self, username):
        username_input = self.form_iframe.locator('input[name="P70_USER_NAME"]')
        username_input.wait_for(state="visible", timeout=20000)
        username_input.fill('')           # Clear before typing
        username_input.fill(username)     # Fill instantly
        username_input.evaluate("el => el.blur()")
        self.page.wait_for_timeout(150)
        expect(username_input).to_have_value(username, timeout=5000)

    def wait_until_username_filled_correctly(self, username):
        username_input = self.form_iframe.locator('input[name="P70_USER_NAME"]')
        expect(username_input).to_have_value(username, timeout=5000)

    def fill_first_name(self, first_name):
        first_name_input = self.form_iframe.get_by_label("First Name")
        first_name_input.wait_for(state="visible", timeout=20000)
        first_name_input.fill('')
        first_name_input.fill(first_name)
        first_name_input.evaluate("el => el.blur()")
        self.page.wait_for_timeout(150)
        expect(first_name_input).to_have_value(first_name, timeout=5000)

    def wait_until_first_name_filled_correctly(self, first_name):
        first_name_input = self.form_iframe.get_by_label("First Name")
        expect(first_name_input).to_have_value(first_name, timeout=5000)

    def fill_family_name(self, family_name):
        family_name_input = self.form_iframe.get_by_label("Family Name")
        family_name_input.wait_for(state="visible", timeout=20000)
        family_name_input.fill('')
        family_name_input.fill(family_name)
        family_name_input.evaluate("el => el.blur()")
        self.page.wait_for_timeout(150)
        expect(family_name_input).to_have_value(family_name, timeout=5000)

    def wait_until_family_name_filled_correctly(self, family_name):
        family_name_input = self.form_iframe.get_by_label("Family Name")
        expect(family_name_input).to_have_value(family_name, timeout=5000)

    def fill_phone(self, phone):
        phone_input = self.form_iframe.get_by_label("Phone Number")
        phone_input.wait_for(state="visible", timeout=20000)
        phone_input.fill('')
        phone_input.fill(phone)
        phone_input.evaluate("el => el.blur()")
        self.page.wait_for_timeout(150)
        expect(phone_input).to_have_value(phone, timeout=5000)

    def wait_until_phone_filled_correctly(self, phone):
        phone_input = self.form_iframe.get_by_label("Phone Number")
        expect(phone_input).to_have_value(phone, timeout=5000)

    def click_next_button(self):
        next_button = self.form_iframe.get_by_role("button", name="Next")
        next_button.wait_for(state="visible", timeout=20000)
        next_button.click()

    def select_role(self, role_value):
        select = self.form_iframe.locator('#P75_ROLE')
        select.wait_for(state="visible", timeout=20000)
        select.select_option(role_value)

    def check_data_sources(self, data_sources):
        for value in data_sources:
            checkbox = self.form_iframe.locator(
                f'input[type="checkbox"][name="P75_DATA_SOURCE"][aria-label="{value}"]'
            )
            checkbox.wait_for(state="visible", timeout=20000)
            checkbox.check()

    def click_save_button(self):
        save_button = self.form_iframe.get_by_role("button", name="Save")
        save_button.wait_for(state="visible", timeout=20000)
        save_button.click()

    def wait_for_drawer_to_close(self):
        # Wait until the iframe for the drawer is detached or hidden
        drawer_iframe_locator = self.page.locator("iframe[src*='edit-cei-user']")
        drawer_iframe_locator.wait_for(state="detached", timeout=15000)
        # Alternatively, if 'detached' does not work, wait for hidden:
        # drawer_iframe_locator.wait_for(state="hidden", timeout=15000)
