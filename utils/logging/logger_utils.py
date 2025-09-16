import inspect
import os
import allure
from logging_config import global_logger


def log_step(step_name: str):
    global_logger.info(f"TEST STEP: {step_name}", stacklevel=2)


def capture_and_log_failure(page, step_name="Step failed", error: Exception = None):
    """
    Attach screenshot & log, and log test file & line number.
    """
    try:
        # Capture screenshot
        screenshot_dir = "logs/screenshots/"
        os.makedirs(screenshot_dir, exist_ok=True)

        ##--- Capturing UI Failures
        if page is not None:
            screenshot_path = os.path.join(screenshot_dir, f"{step_name}.png")
            page.screenshot(path=screenshot_path, full_page=True)

            allure.attach.file(
                screenshot_path, name=f"screenshot_{step_name}",
                attachment_type=allure.attachment_type.PNG
            )
            msg = f"Screenshot captured at {screenshot_path}"
        else:
            msg = f"Non-UI failure (no screenshot)."

        # Attach log file
        log_file = "logs/test_run.log"
        if os.path.exists(log_file):
            allure.attach.file(
                log_file, name=f"log_{step_name}",
                attachment_type=allure.attachment_type.TEXT
            )

        # Log actual caller file & line number
        caller_frame = inspect.stack()[2]  # go back two frames: test -> safe_expect -> here
        file_name = caller_frame.filename
        line_number = caller_frame.lineno

        if error:
            global_logger.error(
               f"{step_name} failed in {file_name}:{line_number} - {msg} | Error: {error}"
            )
        else:
            global_logger.info(f"{step_name} failed in {file_name}:{line_number} - {msg}")

        global_logger.error(
            f"Step failed in {file_name}:{line_number} - screenshot and logs attached."
        )
    except Exception as e:
        global_logger.error(f"Failed to capture failure info: {e}")
