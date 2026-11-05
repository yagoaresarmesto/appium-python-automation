APPIUM_SERVER_URL = "http://127.0.0.1:4723"

ANDROID_CAPABILITIES = {
    "platformName": "Android",
    "appium:automationName": "UiAutomator2",
    "appium:udid": "emulator-5554",
    "appium:appPackage": "com.android.settings",
    "appium:appActivity": ".Settings",
    "appium:noReset": True,
    "appium:forceAppLaunch": True,
}

IOS_CAPABILITIES = {
    "platformName": "iOS",
    "appium:automationName": "XCUITest",
    "appium:udid": "4AFF4321-301C-45E0-9D7B-B82983C3C17F",
    "appium:bundleId": "com.apple.Preferences",
    "appium:noReset": True,
}