from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def test_navega_a_redes_y_vuelve(android_driver):
    driver = android_driver
    wait = WebDriverWait(driver, 10)

    paquete_actual = driver.current_package
    assert paquete_actual == "com.android.settings", (
        f"Se esperaba Ajustes (com.android.settings), "
        f"pero la aplicación activa es {paquete_actual}"
    )

    network_locator = (
        AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().text("Network & internet")',
    )

    network_option = wait.until(
        EC.element_to_be_clickable(network_locator),
        message=(
            "No se encontró la opción 'Network & internet' "
            "visible y habilitada en la pantalla inicial de Ajustes."
        ),
    )
    network_option.click()

    wait.until(
        EC.visibility_of_element_located((
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().text("Airplane mode")',
        ))
    )

    driver.back()

    network_option = wait.until(
        EC.element_to_be_clickable(network_locator),
        message=(
            "No se encontró la opción 'Network & internet' "
            "visible y habilitada en la pantalla inicial de Ajustes."
        ),
    )