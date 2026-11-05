# Automatización móvil con Appium y Python

Proyecto didáctico para construir paso a paso un entorno de automatización de Android e iOS. Actualmente ejecuta dos recorridos por la aplicación de Ajustes de los dispositivos y guarda capturas cuando falla el cuerpo de un test.

## Estado comprobado

- Android: abrir Ajustes → entrar en «Network & internet» → comprobar «Airplane mode» → volver.
- iOS: abrir Ajustes → entrar en «General» → comprobar «Información» → volver.
- Ambos tests han pasado juntos, de forma secuencial.
- La generación de capturas se ha comprobado provocando fallos controlados en ambas plataformas y restaurando después los localizadores.

## Herramientas del entorno preparado

| Herramienta | Versión registrada |
| --- | --- |
| Python | 3.13.5 ARM64 |
| Node.js / npm | 22.23.2 / 10.9.8 |
| Appium local | 3.9.0 |
| Driver UiAutomator2 | 8.7.3 |
| Driver XCUITest | 12.22.8 |
| Appium-Python-Client | 6.1.4 |
| pytest | 9.2.0 |
| Selenium | 4.52.0 |
| Java incluido en Android Studio | 21.0.6 |
| Xcode | 27.2 (27B52) |

Estas versiones describen el entorno utilizado; no son una recomendación de actualizar a las versiones más recientes. Las dependencias Python están registradas en `requirements.txt` y Appium está fijado en `package.json` y `package-lock.json`.

## Estructura y responsabilidades

```text
appium-python-automation/
├── config.py                  # Servidor, dispositivos y aplicaciones
├── conftest.py                # Fixtures, informe de pytest y capturas
├── env.sh                     # Variables de las herramientas del sistema
├── tests/
│   ├── test_android_settings.py
│   └── test_ios_settings.py
├── primera_sesion_android.py  # Ejercicio inicial; fuera de la suite tests/
├── requirements.txt           # Dependencias Python registradas
├── package.json              # Appium como dependencia local
├── package-lock.json         # Resolución de dependencias npm
├── .gitignore
├── .venv/                    # Entorno Python local
├── node_modules/             # Servidor Appium y dependencias locales
├── .appium/                  # Drivers locales
└── artifacts/screenshots/    # Evidencias generadas cuando falla un test
```

Las dependencias, cachés, configuración local del IDE y evidencias están excluidas mediante `.gitignore`. Ese archivo no inicializa un repositorio Git.

## Arranque de una sesión de trabajo

Este procedimiento parte del entorno ya instalado en este Mac. No es una guía de instalación desde cero.

### 1. Arrancar los dispositivos necesarios

**Android:** iniciar el AVD `Pixel_9a_API_36` desde Android Studio o, en una terminal dedicada:

```bash
"$HOME/Library/Android/sdk/emulator/emulator" -avd Pixel_9a_API_36
```

En otra terminal, comprobar la conexión y el arranque:

```bash
"$HOME/Library/Android/sdk/platform-tools/adb" devices -l
"$HOME/Library/Android/sdk/platform-tools/adb" -s emulator-5554 shell getprop sys.boot_completed
```

Se espera el estado `device` y el valor `1`, respectivamente. La configuración actual usa `emulator-5554`; si ADB muestra otro identificador, hay que actualizar `ANDROID_CAPABILITIES` en `config.py`.

El test Android utiliza textos en inglés.

**iOS:** abrir Xcode → Open Developer Tool → Device Hub y abrir el iPhone 17 configurado. Usamos el UDID, porque existen dispositivos con nombres duplicados:

```text
4AFF4321-301C-45E0-9D7B-B82983C3C17F
```

Para arrancarlo por terminal si está apagado:

```bash
xcrun simctl boot 4AFF4321-301C-45E0-9D7B-B82983C3C17F
```

Para esperar o comprobar que ha arrancado:

```bash
xcrun simctl bootstatus 4AFF4321-301C-45E0-9D7B-B82983C3C17F -b
```

No repetir `boot` si ya está arrancado. Para consultar los dispositivos disponibles:

```bash
xcrun simctl list devices available
```

El simulador utilizado tiene iOS 27.2 y Ajustes en español. En esta instalación abrimos la interfaz desde Device Hub: la ruta habitual de `Simulator.app` no estaba disponible.

### 2. Comprobar o arrancar Appium

Primero consultar si ya existe un servidor activo:

```bash
curl http://127.0.0.1:4723/status
```

Si devuelve `ready: true` y la versión esperada, se puede utilizar el servidor existente. Si no hay conexión, abrir una terminal para Appium y ejecutar:

```bash
cd ~/PycharmProjects/appium-python-automation
source ./env.sh
npx --no-install appium --address 127.0.0.1 --port 4723
```

Mantener esa terminal abierta. El servidor debe cargar UiAutomator2 y XCUITest desde `.appium` del proyecto. `--no-install` permite usar Appium local sin descargar otra copia.

`env.sh` configura `APPIUM_HOME`, `ANDROID_HOME`, `JAVA_HOME` y las rutas de Java, ADB y el emulador. Debe cargarse desde la raíz del proyecto porque usa `$PWD`, y hay que cargarlo en cada terminal nueva que vaya a arrancar Appium. No activa el entorno Python ni inicia dispositivos.

Si aparece `EADDRINUSE`, el puerto ya está ocupado. Consultar `/status` antes de intentar iniciar otra instancia; no detener procesos sin identificarlos.

### 3. Ejecutar los tests en otra terminal

```bash
cd ~/PycharmProjects/appium-python-automation
source .venv/bin/activate
python -m pytest -v tests/
```

Para ejecutar una sola plataforma:

```bash
python -m pytest -v tests/test_android_settings.py
python -m pytest -v tests/test_ios_settings.py
```

`python -m pytest` usa pytest del intérprete Python seleccionado. En PyCharm debe estar seleccionado `.venv/bin/python` del proyecto. El resultado esperado para la suite actual es `2 passed`; la duración puede variar. Los tests se ejecutan uno después del otro.

## Cómo funciona un test

1. Pytest descubre el test y las fixtures de `conftest.py`.
2. El argumento `android_driver` o `ios_driver` solicita la fixture correspondiente.
3. La fixture lee las opciones de `config.py` y solicita una sesión al servidor Appium ya activo.
4. `yield driver` entrega el control al test.
5. El test ejecuta acciones y comprueba resultados mediante aserciones y esperas explícitas.
6. El hook `pytest_runtest_makereport` guarda el informe de la fase `call`, que corresponde al cuerpo del test.
7. La fixture consulta ese informe, intenta guardar una captura si hubo un fallo y finalmente intenta cerrar la sesión con `driver.quit()`.

Cerrar la sesión no detiene el servidor Appium. Las fixtures tampoco arrancan el servidor ni los dispositivos.

Los localizadores describen cómo encontrar un elemento; no son el elemento. `WebDriverWait(driver, 10)` comprueba una condición repetidamente durante un máximo aproximado de diez segundos y continúa en cuanto se cumple. No es una pausa fija. El tiempo total incluye también las operaciones del dispositivo y la preparación y cierre de la sesión.

## Capturas y diagnóstico de fallos

Las capturas se guardan en:

```text
artifacts/screenshots/<nombre_del_test>_<fecha>_<hora>_<microsegundos>.png
```

La fecha y hora proceden del reloj local del equipo. El nombre permite conservar capturas de distintas ejecuciones. Una ejecución correcta no genera una captura nueva ni elimina las anteriores.

La captura muestra el estado de la pantalla al realizarla, después del fallo y antes del cierre de la sesión. Si la captura falla, se informa por consola sin sustituir el fallo original del cuerpo del test.

La implementación actual cubre fallos de la fase `call`. No recoge capturas de fallos durante la preparación (`setup`) ni durante el cierre (`teardown`). Si no se ha creado una sesión, puede no existir un driver utilizable.

Para leer un fallo:

1. Identificar el test y la línea señalada.
2. Leer el tipo de excepción y el mensaje personalizado, si existe.
3. Revisar la captura y compararla con el localizador y la pantalla esperada.
4. Consultar la terminal de Appium si el problema está en la sesión o el driver.

Un `TimeoutException` indica que la condición no llegó a cumplirse dentro del plazo; por sí solo no demuestra que el problema sea falta de tiempo.

## Límites actuales y próximos pasos

- Las rutas de `env.sh` y los dispositivos de `config.py` corresponden a este Mac.
- Los tests dependen del idioma y del estado de Ajustes; todavía no existe una preparación general de la pantalla inicial independiente de su estado previo.
- No hay ejecución paralela, integración continua ni informes HTML.
- Las evidencias actuales son capturas; no se exporta aún la jerarquía de elementos.
- Se registraron avisos moderados de seguridad npm durante la instalación, pendientes de revisión. No se ejecutó `npm audit fix --force` porque proponía cambiar a una versión incompatible con el entorno preparado.

El objetivo es incorporar cada mejora cuando resuelva una necesidad concreta, explicarla y comprobarla antes de continuar.
