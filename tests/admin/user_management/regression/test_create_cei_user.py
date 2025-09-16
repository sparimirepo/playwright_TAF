import pytest
from conftest import db_connection
from pageObjects.admin.AdminPage import AdminPage
from pageObjects.common_pages.OverviewPage import OverviewPage
from utils.NextGenUtilities import NextgenUtils
from utils.DB_Validators import validate_data_in_db
from utils.YAML_Loader import YamlLoader
from utils.Test_Decorators import section_name


@pytest.mark.usefixtures("browser_context", "configuration", "utils_setup", "initialize", "db_connection")
class TestCreateCeiUser:

    overview_page: OverviewPage
    admin_page: AdminPage
    nextgen: NextgenUtils

    @pytest.fixture(scope="class")
    def initialize(self, request, browser_context, configuration, utils_setup):
        cls = request.cls
        cls.browser_context = browser_context
        cls.configuration = configuration
        cls.nextgen = NextgenUtils(browser_context)
        cls.nextgen.login(configuration["username"], configuration["password"])
        cls.overview_page = OverviewPage(browser_context)
        cls.admin_page = AdminPage(browser_context)


    @section_name("create_cei_only_user_form")
    def test_create_cei_only_user(self, user_form, db_connection, sql_validation_query, request):
        # Get the current test iteration index
        test_index = request.node.callspec.indices.get('user_form', 0)

        # For the first user, navigate fully; for others, skip navigation
        if test_index == 0:
            self.overview_page.navigate_to_admin_page()
            self.admin_page.navigate_to_user_management_page()

        # Ensure "Add User" button is visible before each use (crucial for stability)
        self.admin_page.page.wait_for_selector('button[title="Add User"]', timeout=10000)

        # Click "Add User" to open the user creation drawer / iframe every time
        self.admin_page.click_on_add_user()

        # Log loaded user form data
        print("Loaded user form data from YAML:")
        for key, value in user_form.items():
                print(f"  {key}: {value}")

        # Fill form fields inside the user creation drawer iframe
        self.admin_page.fill_email(user_form['Email'])
        self.admin_page.fill_username(user_form['UserName'])
        self.admin_page.fill_first_name(user_form['FirstName'])
        self.admin_page.fill_family_name(user_form['FamilyName'])
        self.admin_page.fill_phone(user_form['PhoneNumber'])
        self.admin_page.click_next_button()
        self.admin_page.select_role(user_form['Role'])
        self.admin_page.check_data_sources(user_form['DataSource'])

        # Submit user form
        self.admin_page.click_save_button()

        # Wait for the drawer iframe to close before next iteration or test end
        self.admin_page.wait_for_drawer_to_close()

        self.admin_page.page.wait_for_timeout(1000) 


        # Skip DB validation if no SQL query is provided
        if sql_validation_query is None:
            pytest.skip(f"No SQL validation query provided for {self.__class__.__name__}")

        # Skip DB validation if DB connection not configured
        if db_connection is None:
            print("DB connection not configured; skipping DB validation.")
            pytest.skip("DB connection not configured; skipping DB validation.")

        expected_columns = ['Email', 'UserName', 'FirstName', 'FamilyName', 'PhoneNumber', 'Role', 'DataSource']

        # Perform DB validation for this created user
        validate_data_in_db(db_connection, user_form, sql_validation_query, expected_columns)
