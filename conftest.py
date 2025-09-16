import traceback
from pathlib import Path

import pytest
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import subprocess

from logging_config import global_logger
from utils.CommonUtilities import CommonUtilities
from utils.NextGenUtilities import NextgenUtils
from logging_config import global_logger
from utils.database.DB_Util import ADW_Util


# ---------- Add command-line options ----------
def pytest_addoption(parser):
    parser.addoption(
        "--browserName",
        action="store",
        default="chromium",
        help="Browser to run tests against: chromium | firefox | webkit"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode"
    )
    parser.addoption(
        "--envfile",
        action="store",
        default=".env",
        help="Path to the .env file to load (e.g., .env.dev, .env.prod)"
    )


# ---------- Load selected .env file before any tests run ----------
def pytest_configure(config):
    env_file = config.getoption("--envfile")
    if os.path.exists(env_file):
        load_dotenv(dotenv_path=env_file, override=True)
        global_logger.info(f"Loaded env from: {env_file}")
    else:
        raise FileNotFoundError(f"Environment file '{env_file}' not found.")


# ---------- Session-level fixture to read environment variables ----------
@pytest.fixture(scope="session")
def configuration():
    return {
        "username": os.getenv("adminUser"),
        "password": os.getenv("adminPass"),
        "url": os.getenv("url"),
        "db_Username": os.getenv("db_Username"),
        "db_Password": os.getenv("db_Password"),
        "db_wallet_dir": os.getenv("db_wallet_dir"),
        "db_tns_alias": os.getenv("db_tns_alias")
    }


# ---------- Class-level browser fixture using command-line option ----------
@pytest.fixture(scope="class")
def browser_context(request, configuration):
    browser_name = request.config.getoption("--browserName")
    headless = request.config.getoption("--headless")

    global_logger.info(f"Selected browser: {browser_name}")
    global_logger.info(f"Running in headless mode: {headless}")

    with sync_playwright() as p:
        browser_type = getattr(p, browser_name)
        browser = browser_type.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        # Navigate to URL on launch
        base_url = configuration["url"]
        global_logger.info(f"Navigating to URL: {base_url}")
        page.goto(base_url)
        yield page

        context.close()
        browser.close()
        global_logger.info("Closed browser and context")


@pytest.fixture(scope="class")
def utils_setup(request, browser_context):
    request.cls.nextgen = NextgenUtils(browser_context)


@pytest.fixture(scope="class", autouse=True)
def db_connection(configuration):
    """ Creating DB Connection with params"""
    dbwalletdir = configuration["db_wallet_dir"]
    global_logger.info(f"DB Wallet Directory fetched from is {dbwalletdir}")
    wallet_dir_relative_path = Path.cwd() / "tests/testdata/wallets/" / dbwalletdir if dbwalletdir else Path.cwd() / "tests/testdata/wallets/Wallet_uat2oneclone"

    tns_alias = configuration["db_tns_alias"]
    username = configuration["db_Username"]
    password = configuration["db_Password"]

    db_util = ADW_Util(wallet_dir_relative_path, tns_alias, username, password)

    # Setting up db connection before executing tests
    db_util.connect()

    # This will provide DB Object across the tests
    yield db_util

    # Close the db connection after test execution
    db_util.close_db_connection()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        filename, lineno, testname = rep.location
        class_name = getattr(item.cls, "__name__", 'N/A')

        tb = traceback.extract_tb(call.excinfo.tb)
        real_frame = None

        # Walk from last frame backward
        for frame in reversed(tb):
            file_path = frame.filename
            if "site-packages" not in file_path and ".venv" not in file_path:
                real_frame = frame
                break

        if real_frame:
            fail_file = real_frame.filename
            fail_lineno = real_frame.lineno
            text = real_frame.line
            global_logger.error(
                f"Assertion failed in test '{testname}' (class: '{class_name}') "
                f"at {fail_file}:{fail_lineno}. Line: {text}"
            )
        else:
            # fallback: log last frame inside site-packages
            last_call = tb[-1] if tb else None
            if last_call:
                global_logger.error(
                    f"Assertion failed in test '{testname}' (class: '{class_name}') "
                    f"at {last_call.filename}:{last_call.lineno}. Line: {last_call.line}"
                )
            else:
                global_logger.error(
                    f"Assertion failed in test '{testname}' (class: '{class_name}')"
                )
