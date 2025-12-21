import os
import time
import pickle
import undetected_chromedriver as uc
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURATIE ---
load_dotenv()
EMAIL = os.getenv("TIMECHIMP_EMAIL")
WACHTWOORD = os.getenv("TIMECHIMP_PASSWORD")

BASE_URL = "https://app.timechimp.com/auth/login"
# We gebruiken 1 bestand voor alles (cookies + local storage)
SESSIE_MAP = "cookies"
SESSIE_BESTAND = "timechimp_compleet.pkl"
SESSIE_PAD = os.path.join(SESSIE_MAP, SESSIE_BESTAND)


# --- FUNCTIES ---

def start_driver():
    """Start de browser met de juiste opties en schoont tabs op."""
    print("🚀 Browser wordt gestart...")
    options = uc.ChromeOptions()
    options.add_argument("--disable-restore-session-state")

    # Wachtwoord popup uitzetten
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    options.add_experimental_option("prefs", prefs)

    driver = uc.Chrome(options=options)
    sluit_alle_andere_tabbladen(driver)
    return driver


def sluit_alle_andere_tabbladen(driver):
    """Zorgt dat er maar 1 tabblad open blijft."""
    try:
        while len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            driver.close()
        driver.switch_to.window(driver.window_handles[0])
    except:
        pass


def klik_cookie_popup_weg(driver):
    """Probeert de cookie banner weg te klikken."""
    try:
        wait = WebDriverWait(driver, 5)
        knop = wait.until(EC.presence_of_element_located((
            By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"
        )))
        driver.execute_script("arguments[0].click();", knop)
        print("✅ Cookie melding weggeklikt.")
        time.sleep(1)
    except:
        pass


def sla_sessie_op(driver):
    """Slaat Cookies EN Local Storage op."""
    if not os.path.exists(SESSIE_MAP):
        os.makedirs(SESSIE_MAP)

    try:
        # 1. Haal Cookies op
        cookies = driver.get_cookies()

        # 2. Haal Local Storage op (Hier zit waarschijnlijk je token!)
        # We gebruiken een JS trucje om alles als een dictionary terug te krijgen
        local_storage = driver.execute_script("return Object.assign({}, window.localStorage);")

        sessie_data = {
            "cookies": cookies,
            "local_storage": local_storage
        }

        with open(SESSIE_PAD, "wb") as file:
            pickle.dump(sessie_data, file)

        print(f"💾 Volledige sessie (Cookies + LocalStorage) opgeslagen in: {SESSIE_PAD}")
    except Exception as e:
        print(f"❌ Kon sessie niet opslaan: {e}")


def laad_sessie_in(driver):
    """Laadt Cookies EN Local Storage in."""
    if not os.path.exists(SESSIE_PAD):
        return False

    print("📦 Oude sessie gevonden. Inladen...")
    try:
        # Eerst naar de site gaan, anders mag je geen opslag aanpassen
        if "timechimp.com" not in driver.current_url:
            driver.get(BASE_URL)
            time.sleep(2)

        with open(SESSIE_PAD, "rb") as file:
            data = pickle.load(file)

        # 1. Cookies herstellen
        cookies = data.get("cookies", [])
        driver.delete_all_cookies()
        for cookie in cookies:
            try:
                if 'domain' in cookie: del cookie['domain']  # Fix voor domein fouten
                driver.add_cookie(cookie)
            except:
                continue

        # 2. Local Storage herstellen (CRUCIAAL)
        local_storage = data.get("local_storage", {})
        # Eerst legen
        driver.execute_script("window.localStorage.clear();")
        # Dan vullen
        for key, value in local_storage.items():
            # We moeten oppassen met quotes in de javascript string
            # driver.execute_script(f"window.localStorage.setItem('{key}', '{value}');") is onveilig
            # Veilige manier via arguments:
            driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", key, value)

        print("✅ Cookies & Local Storage geïnjecteerd.")

        # 3. Verversen
        print("🔄 Pagina verversen...")
        driver.refresh()
        time.sleep(4)  # Iets langer wachten

        # Check URL
        if "login" in driver.current_url:
            return False

        return True

    except Exception as e:
        print(f"⚠️ Kon sessie niet laden: {e}")
        return False


def login_met_wachtwoord(driver):
    """Volledige login procedure."""
    print("⌨️ Handmatig inloggen...")
    if "auth/login" not in driver.current_url:
        driver.get(BASE_URL)

    klik_cookie_popup_weg(driver)
    wait = WebDriverWait(driver, 20)

    try:
        wait.until(EC.element_to_be_clickable((By.NAME, "username"))).send_keys(EMAIL)
        ww = driver.find_element(By.NAME, "password")
        ww.send_keys(WACHTWOORD)
        ww.send_keys(Keys.RETURN)

        wait.until(EC.url_contains("dashboard"))
        print("✅ Ingelogd! Even wachten op opslaan...")
        time.sleep(5)  # Wacht tot alle tokens in LocalStorage staan
        sla_sessie_op(driver)

    except Exception as e:
        print(f"❌ Inloggen mislukt: {e}")
        raise e


# --- HOOFD PROGRAMMA ---

def main():
    driver = start_driver()

    # Altijd eerst naar de site voor context
    driver.get(BASE_URL)

    # Probeer Pad X (Sessie herstellen)
    if laad_sessie_in(driver):
        print("🎉 Direct ingelogd via opgeslagen sessie!")
    else:
        # Pad Y (Opnieuw inloggen)
        print("⚠️ Sessie laden mislukt of verlopen. We loggen opnieuw in.")
        login_met_wachtwoord(driver)

    print("\nKlaar voor actie!")
    input("Druk op ENTER om af te sluiten...")
    driver.quit()


if __name__ == "__main__":
    main()