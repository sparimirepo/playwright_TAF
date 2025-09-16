import os

from playwright.sync_api import TimeoutError
from playwright.sync_api import expect
from utils.logging.logger_utils import log_step, capture_and_log_failure


class CommonUtilities:

    def __init__(self, page):
        self.page = page

    """Resolves a Playwright locator object based on the locator type and value."""
    def get_locator(self, locator_type: str, locator_value):

        locator_type = locator_type.lower().strip()

        match locator_type:
            case "id":
                return self.page.locator(f"#{locator_value}")
            case "css":
                return self.page.locator(locator_value)
            case "xpath":
                return self.page.locator(f"xpath={locator_value}")
            case "text":
                return self.page.get_by_text(locator_value)
            case "role":
                role_value = locator_value.get("role")
                name_value = locator_value.get("name")

                if not role_value or not name_value:
                    raise ValueError("For 'role' locator, provide both 'role' and 'name' keys.")

                return self.page.get_by_role(role_value, name=name_value)
            case "alt":
                return self.page.get_by_alt_text(locator_value)
            case "label":
                return self.page.get_by_label(locator_value)
            case "placeholder":
                return self.page.get_by_placeholder(locator_value)
            case "title":
                return self.page.get_by_title(locator_value)
            case _:
                raise ValueError(f"Unsupported locator type: '{locator_type}'")

    """Clicks on a UI element identified by the given locator."""
    def click_element(self, locator_type: str, locator_value, description: str = ""):
        log_step(f"Clicking on element: {description}")
        try:
            locator = self.get_locator(locator_type, locator_value)
            locator.click()
            log_step(f"Successfully clicked: {description}")
        except TimeoutError:
            capture_and_log_failure(f"Element not clickable in time: {description}")
            raise
        except Exception as e:
            capture_and_log_failure(f"Failed to click on element '{description}': {str(e)}")
            raise

    """Clears any existing content and fills the input or textarea with the provided text."""
    def fill_element(self, locator_type: str, locator_value, input_text: str, description: str = ""):
        log_step(f"Filling element: {description} with text: '{input_text}'")
        try:
            locator = self.get_locator(locator_type, locator_value)
            locator.fill(input_text)
            log_step(f"Filled '{description}' with '{input_text}'")
        except TimeoutError:
            capture_and_log_failure(f"Element not ready to fill in time: {description}")
            raise
        except Exception as e:
            capture_and_log_failure(f"Failed to fill element '{description}': {str(e)}")
            raise

    """Waits until the element is visible in the DOM (appears)."""
    def wait_until_element_appears(self, locator_type: str, locator_value, description: str = "", timeout: int = 10000):
        try:
            locator = self.get_locator(locator_type, locator_value)
            locator.wait_for(state="visible", timeout=timeout)
            log_step(f"{description}: Element appeared on the page.")
        except Exception:
            capture_and_log_failure(f"Element: {description} did not appear within timeout.")
            raise AssertionError(f"Element: {description} did not appear within timeout.")

    """Waits until the element is hidden or removed from the DOM (disappears)."""
    def wait_until_element_disappears(self, locator_type: str, locator_value, description: str = "",
                                      timeout: int = 10000):
        try:
            locator = self.get_locator(locator_type, locator_value)
            locator.wait_for(state="hidden", timeout=timeout)
            log_step(f"{description}: Element disappeared from the page.")
        except Exception:
            capture_and_log_failure(f"Element: {description} did not disappear within timeout.")
            raise AssertionError(f"Element: {description} did not disappear within timeout.")

    """Selects an option from a dropdown by label or value and asserts the selection."""
    def select_dropdown_option_and_assert(self, locator_type, locator_value, option: str, by: str, description: str):
        try:
            locator = self.get_locator(locator_type, locator_value)
            # Perform selection
            if by.lower() == "label":
                locator.select_option(label=option)
            elif by.lower() == "value":
                locator.select_option(value=option)
            else:
                raise ValueError("Invalid 'by' argument. Use 'label' or 'value'.")

            # Assertion after selection
            expect(locator).to_have_value(option)
            log_step(f"{description}: Option '{option}' selected successfully using '{by}'.")

        except Exception as e:
            capture_and_log_failure(f"Failed to select option '{option}' by '{by}'.")
            raise AssertionError(f"Failed to select option '{option}' by '{by}'.")

    """Clicks the element to focus and fills it with the given text."""
    def click_and_fill_element(self, locator_type, locator_value, text: str, description: str):
        try:
            locator = self.get_locator(locator_type, locator_value)
            locator.click()
            locator.fill(text)
            log_step(f"{description}: Clicked and entered text '{text}'.")
        except Exception:
            capture_and_log_failure(f"{description}: Failed to click and fill with text '{text}'.")
            raise AssertionError(f"{description}: Failed to click and fill with text '{text}'.")

    """Scrolls the element into view and clicks it."""
    def scroll_and_click_element(self, locator_type, locator_value, description: str):
        try:
            locator = self.get_locator(locator_type, locator_value)

            # Scroll into view first
            locator.scroll_into_view_if_needed()

            # Wait until clickable
            locator.wait_for(state="visible")
            locator.wait_for(state="attached")
            locator.wait_for(state="enabled")

            # Click
            locator.click()

            log_step(f"{description}: Scrolled into view and clicked.")
        except Exception as e:
            capture_and_log_failure(f"{description}: Failed to scroll and click. Error: {e}")
            raise AssertionError(f"{description}: Failed to scroll and click. Error: {e}")

    """Scrolls the page until the element is in view."""
    def scroll_to_element(self, locator_type, locator_value, description: str):
        try:
            locator = self.get_locator(locator_type, locator_value)
            locator.scroll_into_view_if_needed()
            log_step(f"{description}: Scrolled to the element.")
        except Exception as e:
            capture_and_log_failure(f"{description}: Failed to scroll to the element. Error: {e}")
            raise AssertionError(f"{description}: Failed to scroll to the element. Error: {e}")

    """Appends the provided text to the existing content of an input or editable element."""
    def append_text_to_element(self, locator_type: str, locator_value, input_text: str, description: str = ""):
        try:
            locator = self.get_locator(locator_type, locator_value)
            locator.type(input_text)
            log_step(f"{description}: Appended text '{input_text}'.")
        except Exception:
            capture_and_log_failure(f"{description}: Failed to append text '{input_text}'.")
            raise AssertionError(f"{description}: Failed to append text '{input_text}'.")

    """Hovers the mouse over the specified element to trigger hover effects like tooltips or menus."""
    def hover_over_element(self, locator_type: str, locator_value, description: str = ""):
        try:
            locator = self.get_locator(locator_type, locator_value)
            locator.hover()
            log_step(f"{description}: Hovered over element.")
        except Exception:
            capture_and_log_failure(f"{description}: Unable to Hover over element.")
            raise AssertionError(f"{description}: Unable to Hover over element.")

    """Returns the visible text content of the specified element (e.g., div, span, p)"""
    def get_element_text(self, locator_type: str, locator_value, description: str = "") -> str:
        try:
            locator = self.get_locator(locator_type, locator_value)
            text = locator.text_content()
            log_step(f"{description}: Retrieved text -> '{text.strip() if text else ''}'")
            return text.strip() if text else ""
        except Exception:
            capture_and_log_failure(f"{description}: Failed to retrieve text from element.")
            raise AssertionError(f"{description}: Failed to retrieve text from element.")

    """Returns the current value of an input or textarea element."""
    def get_input_value(self, locator_type: str, locator_value, description: str = "") -> str:

        try:
            locator = self.get_locator(locator_type, locator_value)
            value = locator.input_value()
            log_step(f"{description}: Retrieved value -> '{value.strip() if value else ''}'")
            return value.strip() if value else ""
        except Exception:
            capture_and_log_failure(f"{description}: Failed to retrieve input value.")
            raise AssertionError(f"{description}: Failed to retrieve input value.")

    """Switches context to the given iframe.(frame_name_or_selector (str): The iframe name/id or selector.)"""
    def switch_to_frame(self, frame_name_or_selector: str, description: str):
        try:
            # If the argument looks like a CSS/XPath selector, treat it as a locator
            if frame_name_or_selector.startswith("//") or frame_name_or_selector.startswith(
                    "[") or frame_name_or_selector.startswith(".") or frame_name_or_selector.startswith("#"):
                frame_element = self.page.locator(frame_name_or_selector)
                frame_element.wait_for(state="visible")
                frame = frame_element.content_frame()
            else:
                # Treat it as a frame name
                frame = self.page.frame(name=frame_name_or_selector)

            if frame is None:
                raise ValueError(f"Frame '{frame_name_or_selector}' not found.")

            self.current_frame = frame  # Store current frame for later actions
            log_step(f"{description}: Switched to frame '{frame_name_or_selector}'.")
            return frame
        except Exception as e:
            capture_and_log_failure(f"{description}: Failed to switch to frame '{frame_name_or_selector}'. Error: {e}")
            raise AssertionError(f"{description}: Failed to switch to frame '{frame_name_or_selector}'. Error: {e}")

    """Switches context back to the main page frame."""
    def switch_to_main_frame(self, description: str):
        try:
            self.current_frame = self.page
            log_step(f"{description}: Switched to main frame.")
        except Exception as e:
            capture_and_log_failure(f"{description}: Failed to switch to main frame. Error: {e}")
            raise AssertionError(f"{description}: Failed to switch to main frame. Error: {e}")

    """Performs a double-click on the specified element."""
    def double_click_element(self, locator_type: str, locator_value, description: str = ""):
        try:
            locator = self.get_locator(locator_type, locator_value)
            locator.dblclick()
            log_step(f"Double-clicked on element: {description}")
        except Exception as e:
            capture_and_log_failure(f"Failed to double-click element '{description}': {str(e)}")
            raise AssertionError(f"Failed to double-click element '{description}': {str(e)}")

    """Performs a right-click (context click) on the specified element."""
    def right_click_element(self, locator_type: str, locator_value, description: str = ""):
        try:
            locator = self.get_locator(locator_type, locator_value)
            locator.click(button="right")
            log_step(f"Right-clicked on element: {description}")
        except Exception as e:
            capture_and_log_failure(f"Failed to right-click element '{description}': {str(e)}")
            raise AssertionError(f"Failed to right-click element '{description}': {str(e)}")

    """Clears the text/content of the specified input or textarea element."""
    def clear_element(self, locator_type: str, locator_value, description: str = ""):
        try:
            locator = self.get_locator(locator_type, locator_value)
            locator.fill("")  # Clears the input
            log_step(f"Cleared text from element: {description}")
        except Exception as e:
            capture_and_log_failure(f"Failed to clear element '{description}': {str(e)}")
            raise AssertionError(f"Failed to clear element '{description}': {str(e)}")

    """Asserts that the element is visible in the DOM."""
    def assert_element_visible(self, locator_type: str, locator_value, description: str):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).to_be_visible()
            log_step(f"{description} is visible as expected.")
        except Exception as e:
            capture_and_log_failure(self.page,f"Expected '{description}' to be visible but not.")
            raise AssertionError(f"Expected '{description}' to be visible but not.")

    """Asserts that the element is hidden or not in the DOM."""
    def assert_element_not_visible(self, locator_type, locator_value, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).not_to_be_visible()
            log_step(f"{description} is not visible as expected.")
        except Exception:
            capture_and_log_failure(self.page, f"'{description}' was unexpectedly visible.")
            raise AssertionError(f"'{description}' was unexpectedly visible.")

    """Asserts that the element (checkbox/radio) is checked."""
    def assert_element_checked(self, locator_type, locator_value, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).to_be_checked()
            log_step(f"{description} is checked as expected.")
        except Exception:
            capture_and_log_failure(self.page, f"'{description}' was not checked.")
            raise AssertionError(f"'{description}' was not checked as expected.")

    """Asserts that the element (checkbox/radio) is not checked."""
    def assert_element_not_checked(self, locator_type, locator_value, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).not_to_be_checked()
            log_step(f"{description} is not checked as expected.")
        except Exception:
            capture_and_log_failure(self.page,f"'{description}' was checked which is not as per expectation.")
            raise AssertionError(f"'{description}' was checked which is not as per expectation.")

    """Asserts that the element is disabled."""
    def assert_element_disabled(self, locator_type, locator_value, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).to_be_disabled()
            log_step(f"{description} is disabled as expected.")
        except Exception:
            capture_and_log_failure(self.page, f"'{description}' was not disabled.")
            raise AssertionError(f"'{description}' was not disabled as expected.")

    """Asserts that the element is enabled."""
    def assert_element_enabled(self, locator_type, locator_value, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).to_be_enabled()
            log_step(f"{description} is enabled as expected.")
        except Exception:
            capture_and_log_failure(self.page, f"'{description}' was not enabled.")
            raise AssertionError(f"'{description}' was not enabled as expected.")

    """Asserts that the input or textarea element has the expected value."""
    def assert_element_has_value(self, locator_type, locator_value, expected_value, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).to_have_value(expected_value)
            log_step(f"{description} has expected value: '{expected_value}'.")
        except Exception:
            capture_and_log_failure(self.page,f"'{description}' did not have value '{expected_value}'.")
            raise AssertionError(f"'{description}' did not have value '{expected_value}'.")

    """Asserts that the element is editable."""
    def assert_element_editable(self, locator_type, locator_value, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).to_be_editable()
            log_step(f"{description} is editable as expected.")
        except Exception:
            capture_and_log_failure(self.page, f"'{description}' was not editable.")
            raise AssertionError(f"'{description}' was not editable as expected.")

    """Asserts that the element is not editable (readonly or disabled)."""
    def assert_element_not_editable(self, locator_type, locator_value, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).not_to_be_editable()
            log_step(f"{description} is not editable as expected.")
        except Exception:
            capture_and_log_failure(self.page, f"'{description}' was unexpectedly editable.")
            raise AssertionError(f"'{description}' was unexpectedly editable")

    """Asserts that the element has the expected placeholder text."""
    def assert_element_placeholder(self, locator_type, locator_value, expected_placeholder, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).to_have_attribute("placeholder", expected_placeholder)
            log_step(f"{description} has expected placeholder: '{expected_placeholder}'.")
        except Exception:
            capture_and_log_failure(self.page,f"'{description}' did not have placeholder '{expected_placeholder}'.")
            raise AssertionError(f"'{description}' did not have placeholder '{expected_placeholder}'.")

    """Asserts that the select dropdown has the expected selected value(s)."""
    def assert_select_has_value(self, locator_type, locator_value, expected_values, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).to_have_values(expected_values)
            log_step(f"{description} has selected values: {expected_values}")
        except Exception:
            capture_and_log_failure(self.page, f"'{description}' did not have selected values {expected_values}.")
            raise AssertionError(f"'{description}' did not have selected values {expected_values}.")

    """Asserts that the select dropdown has the expected list of options."""
    def assert_select_has_options(self, locator_type, locator_value, expected_options, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).to_have_select_options(expected_options)
            log_step(f"{description} has expected select options: {expected_options}")
        except Exception:
            capture_and_log_failure(self.page, f"'{description}' did not have expected select options: {expected_options}")
            raise AssertionError(f"'{description}' did not have expected select options: {expected_options}")

    """Asserts that the element has the expected value."""
    def assert_element_has_text(self, locator_type, locator_value, expected_text, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).to_have_text(expected_text)
            log_step(f"{description} has expected text: '{expected_text}'.")
        except Exception:
            capture_and_log_failure(self.page,f"'{description}' did not have text '{expected_text}'.")
            raise AssertionError(f"'{description}' did not have text '{expected_text}'.")

    """Asserts that the element's text contains the expected substring."""
    def assert_element_contains_text(self, locator_type, locator_value, partial_text, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).to_contain_text(partial_text)
            log_step(f"{description} contains text: '{partial_text}'.")
        except Exception:
            capture_and_log_failure(self.page, f"'{description}' did not contain text '{partial_text}'.")
            raise AssertionError(f"'{description}' did not contain text '{partial_text}'.")

    """Asserts that the element has the specified attribute and value."""
    def assert_element_has_attribute(self, locator_type, locator_value, attr_name, attr_value, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).to_have_attribute(attr_name, attr_value)
            log_step(f"{description} has attribute '{attr_name}' with value '{attr_value}'.")
        except Exception:
            capture_and_log_failure(self.page,f"'{description}' did not have attribute '{attr_name}' with value '{attr_value}'.")
            raise AssertionError(f"'{description}' did not have attribute '{attr_name}' with value '{attr_value}'.")

    """Asserts that the number of matched elements equals the expected count."""
    def assert_element_count(self, locator_type, locator_value, expected_count, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).to_have_count(expected_count)
            log_step(f"{description} has {expected_count} matching elements.")
        except Exception:
            capture_and_log_failure(self.page, f"'{description}' did not have {expected_count} matching elements.")
            raise AssertionError(f"'{description}' did not have {expected_count} matching elements.")

    """Asserts that the page title matches the expected title."""
    def assert_page_title(self, page, expected_title, description="Page title"):
        try:
            expect(page).to_have_title(expected_title)
            log_step(f"{description} matches expected: '{expected_title}'.")
        except Exception:
            capture_and_log_failure(self.page, f"Assertion  : Page title mismatch. Expected: '{expected_title}'")
            raise AssertionError(f"Assertion  : Page title mismatch. Expected: '{expected_title}'")

    """Asserts that the element is focused."""
    def assert_element_focused(self, locator_type, locator_value, description):
        try:
            locator = self.get_locator(locator_type, locator_value)
            expect(locator).to_be_focused()
            log_step(f"{description} is focused as expected.")
        except Exception:
            capture_and_log_failure(self.page, f"'{description}' was not focused.")
            raise AssertionError(f"'{description}' was not focused.")

    """Asserts that the given condition is True."""
    def assert_true(self, condition: bool, description: str):
        try:
            assert condition is True
            log_step(f"{description} is True as expected.")
        except Exception:
            capture_and_log_failure(self.page, f"{description} was expected to be True but was False.")
            raise AssertionError(f"{description} was expected to be True but was False.")

    """Asserts that the given condition is False."""
    def assert_false(self, condition: bool, description: str):
        try:
            assert condition is False
            log_step(f"{description} is False as expected.")
        except Exception:
            capture_and_log_failure(self.page, f"{description} was expected to be False but was True.")
            raise AssertionError(f"{description} was expected to be False but was True.")

    """Asserts that the actual value equals the expected value."""
    def assert_equal(self, actual, expected, description: str):
        try:
            assert actual == expected
            log_step(f"{description}: Actual = Expected = {expected}")
        except Exception:
            capture_and_log_failure(self.page, f"{description}: Expected '{expected}', but got '{actual}'")
            raise AssertionError(f"{description}: Expected '{expected}', but got '{actual}'")