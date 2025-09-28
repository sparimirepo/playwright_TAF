import traceback
from collections import defaultdict
from datetime import datetime
import time
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
import matplotlib.pyplot as plt


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
        default=".env.dev",
        help="Path to the .env.prod file to load (e.g., .env.prod.dev, .env.prod.prod)"
    )


# ---------- Load selected .env.prod file before any tests run ----------
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


@pytest.fixture()
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


# Store test start times and metadata
_start_times = {}
_test_metadata = defaultdict(dict)
_pass_fail_counts = {"passed": 0, "failed": 0, "skipped": 0}

# Capture start time and metadata
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    _start_times[item.nodeid] = time.time()
    page = item.funcargs.get("page")
    if page and hasattr(page, "url"):
        _test_metadata[item.nodeid]["url"] = page.url
    yield

# Enhance test report with metadata and screenshots
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    start_time = _start_times.get(item.nodeid, time.time())
    end_time = time.time()
    rep.start_time = start_time
    rep.end_time = end_time
    rep.duration_str = f"{end_time - start_time:.2f}s"
    rep.test_url = _test_metadata.get(item.nodeid, {}).get("url", "N/A")

    # Update pass/fail/skipped counts
    if rep.when == "call":
        if rep.passed:
            _pass_fail_counts["passed"] += 1
        elif rep.failed:
            _pass_fail_counts["failed"] += 1
        else:
            _pass_fail_counts["skipped"] += 1

    # Handle failures and screenshots
    if rep.when == "call" and rep.failed:
        filename, lineno, testname = rep.location
        class_name = getattr(item.cls, "__name__", 'N/A')

        tb = traceback.extract_tb(call.excinfo.tb)
        real_frame = None
        for frame in reversed(tb):
            if "site-packages" not in frame.filename and ".venv" not in frame.filename:
                real_frame = frame
                break

        if real_frame:
            fail_file = real_frame.filename
            fail_lineno = real_frame.lineno
            text = real_frame.line
            global_logger.error(f"Assertion failed in test '{testname}' (class: '{class_name}') at {fail_file}:{fail_lineno}. Line: {text}")

        page = item.funcargs.get("page")
        if page:
            base_folder = getattr(item.config, "base_folder", "reports")
            screenshots_dir = os.path.join(base_folder, "screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)

            safe_name = testname.replace("/", "_").replace("::", "_") + ".png"
            screenshot_path = os.path.join(screenshots_dir, safe_name)
            page.screenshot(path=screenshot_path)

            rel_path = os.path.relpath(screenshot_path, base_folder)
            if not hasattr(rep, "extra"):
                rep.extra = []
            rep.extra.append(f'<div style="margin:10px 0;"><img src="{rel_path}" alt="screenshot" style="max-width:600px;border:2px solid red;"></div>')

# Generate a visually enhanced summary graph and metadata table
def pytest_sessionfinish(session, exitstatus):
    base_folder = getattr(session.config, "base_folder", "reports")
    os.makedirs(base_folder, exist_ok=True)

    # Graph
    plt.style.use("ggplot")
    plt.figure(figsize=(8, 5))
    bars = plt.bar(_pass_fail_counts.keys(), _pass_fail_counts.values(), color=['green', 'red', 'orange'])
    plt.title(f"Test Summary ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    plt.ylabel("Number of Tests")
    plt.xlabel("Status")

    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.1, f'{int(yval)}', ha='center', va='bottom', fontweight='bold')

    graph_path = os.path.join(base_folder, "summary_graph.png")
    plt.savefig(graph_path)
    plt.close()

    # HTML summary
    html_path = os.path.join(base_folder, "summary_report.html")
    with open(html_path, "w") as f:
        f.write(f"<html><head><title>Test Summary</title></head><body>")
        f.write(f"<h1 style='color:navy;'>Test Summary Report</h1>")
        f.write(f"<img src='{os.path.basename(graph_path)}' alt='summary graph'><br>")

        f.write("<h2>Individual Test Details</h2><table border='1' cellpadding='5' cellspacing='0'>")
        f.write("<tr><th>Test Name</th><th>Class</th><th>Status</th><th>Duration</th><th>Start Time</th><th>End Time</th><th>URL</th></tr>")
        for item in session.items:
            nodeid = item.nodeid
            rep = getattr(item, "rep_call", None)
            status = getattr(rep, "outcome", "N/A") if rep else "N/A"
            duration = getattr(rep, "duration_str", "N/A") if rep else "N/A"
            start_time = datetime.fromtimestamp(getattr(rep, "start_time", 0)).strftime("%H:%M:%S") if rep else "N/A"
            end_time = datetime.fromtimestamp(getattr(rep, "end_time", 0)).strftime("%H:%M:%S") if rep else "N/A"
            url = getattr(rep, "test_url", "N/A") if rep else "N/A"
            class_name = getattr(item.cls, "__name__", "N/A")
            color = "green" if status=="passed" else "red" if status=="failed" else "orange"

            f.write(f"<tr style='color:{color};'><td>{nodeid}</td><td>{class_name}</td><td>{status}</td><td>{duration}</td><td>{start_time}</td><td>{end_time}</td><td>{url}</td></tr>")

        f.write("</table></body></html>")

    print(f"\nEnhanced summary report saved to {html_path}")