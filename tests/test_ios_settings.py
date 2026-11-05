from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_navega_a_general_y_vuelve(ios_driver):
    driver = ios_driver
    wait = WebDriverWait(driver, 10)

    app_info = driver.execute_script("mobile: activeAppInfo")
    assert app_info["bundleId"] == "com.apple.Preferences", (
        f"Se esperaba Ajustes (com.apple.Preferences), "
        f"pero la aplicación activa es {app_info['bundleId']}"
    )

    general = wait.until(
        EC.element_to_be_clickable(
            (AppiumBy.ACCESSIBILITY_ID, "General")
        )
    )
    general.click()

    wait.until(
        EC.visibility_of_element_located(
            (AppiumBy.ACCESSIBILITY_ID, "Información")
        )
    )

    # Volver a la pantalla principal de Ajustes
    driver.back()

    wait.until(
        EC.element_to_be_clickable(
            (AppiumBy.ACCESSIBILITY_ID, "General")
        )
    )

    wait.until(
        EC.invisibility_of_element_located(
            (AppiumBy.ACCESSIBILITY_ID, "Información")
        )
    )