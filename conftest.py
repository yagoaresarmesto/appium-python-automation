import pytest
from pathlib import Path
from datetime import datetime
from config import (
    APPIUM_SERVER_URL,
    ANDROID_CAPABILITIES,
    IOS_CAPABILITIES,
)
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions

def guardar_captura_si_falla(driver, request):
    report = getattr(request.node, "test_call_report", None)

    if report is None or not report.failed:
        return

    try:
        screenshots_dir = (
            Path(request.config.rootpath)
            / "artifacts"
            / "screenshots"
        )
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        screenshot_path = (
                screenshots_dir
                / f"{request.node.name}_{timestamp}.png"
        )
        saved = driver.save_screenshot(str(screenshot_path))

        if saved:
            print(f"\nCaptura guardada: {screenshot_path}")
        else:
            print("\nNo se pudo guardar la captura.")

    except Exception as error:
        print(f"\nError al guardar la captura: {error}")

@pytest.fixture
def android_driver(request):
    options = UiAutomator2Options().load_capabilities(
        ANDROID_CAPABILITIES
    )

    driver = webdriver.Remote(
        APPIUM_SERVER_URL,
        options=options,
    )

    try:
        yield driver
    finally:
        try:
            guardar_captura_si_falla(driver, request)
        finally:
            driver.quit()


@pytest.fixture
def ios_driver(request):
    options = XCUITestOptions().load_capabilities(
        IOS_CAPABILITIES
    )

    driver = webdriver.Remote(
        APPIUM_SERVER_URL,
        options=options,
    )

    try:
        driver.activate_app("com.apple.Preferences")
        yield driver
    finally:
        try:
            guardar_captura_si_falla(driver, request)
        finally:
            driver.quit()

@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield

    if report.when == "call":
        item.test_call_report = report

    return report