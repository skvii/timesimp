import os
import time
import pickle
import json
import pandas as pd
import undetected_chromedriver as uc
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# --- CONFIGURATIE ---
load_dotenv()
EMAIL = os.getenv("TIMECHIMP_EMAIL")
WACHTWOORD = os.getenv("TIMECHIMP_PASSWORD")

BASE_URL = "https://app.timechimp.com/auth/login"
# We gebruiken 1 bestand voor alles (cookies + local storage)
SESSIE_MAP = "cookies"
SESSIE_BESTAND = "timechimp_compleet.pkl"
SESSIE_PAD = os.path.join(SESSIE_MAP, SESSIE_BESTAND)
PROFIEL_BESTAND = "profiel.json"


# --- FUNCTIES ---


def start_driver():
    """Start de browser met de juiste opties en schoont tabs op."""
    print("🚀 Browser wordt gestart...")
    options = uc.ChromeOptions()
    options.add_argument("--disable-restore-session-state")
    # options.add_argument("--headless=new")

    # Wachtwoord popup uitzetten
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
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
    except Exception:
        pass


def klik_cookie_popup_weg(driver):
    """Probeert de cookie banner weg te klikken."""
    try:
        wait = WebDriverWait(driver, 5)
        knop = wait.until(
            EC.presence_of_element_located(
                (By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
            )
        )
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
        local_storage = driver.execute_script(
            "return Object.assign({}, window.localStorage);"
        )

        sessie_data = {"cookies": cookies, "local_storage": local_storage}

        with open(SESSIE_PAD, "wb") as file:
            pickle.dump(sessie_data, file)

        print(
            f"💾 Volledige sessie (Cookies + LocalStorage) opgeslagen in: {SESSIE_PAD}"
        )
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
                if "domain" in cookie:
                    del cookie["domain"]  # Fix voor domein fouten
                driver.add_cookie(cookie)
            except:
                continue

        # 2. Local Storage herstellen (CRUCIAAL)
        local_storage = data.get("local_storage", {})
        # Eerst legen
        driver.execute_script("window.localStorage.clear();")
        # Dan vullen
        for key, value in local_storage.items():
            driver.execute_script(
                "window.localStorage.setItem(arguments[0], arguments[1]);", key, value
            )

        print("✅ Cookies & Local Storage geïnjecteerd.")

        # 3. Verversen
        print("🔄 Pagina verversen...")
        driver.refresh()
        time.sleep(3)  # Iets langer wachten

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

        wait.until(lambda d: "login" not in d.current_url)

        print("✅ Ingelogd! Even wachten op opslaan...")
        time.sleep(5)
        sla_sessie_op(driver)

    except Exception as e:
        print(f"❌ Inloggen mislukt: {e}")
        raise e


def klik_dag_knop(driver):
    """Zoekt de knop met tekst 'Dag' en klikt erop."""
    print("🔍 Zoeken naar 'Dag' knop...")
    try:
        wait = WebDriverWait(driver, 10)
        xpath = "//button[.//span[text()='Dag']]"
        knop = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        knop.click()
        print("✅ 'Dag' knop geklikt.")
    except Exception as e:
        print(f"❌ Kon 'Dag' knop niet vinden of klikken: {e}")


def klik_agenda(driver):
    """Klikt op de agenda knop in de kalender container."""
    print("🔍 Zoeken naar Agenda knop...")
    try:
        wait = WebDriverWait(driver, 10)
        knop = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "section[aria-label='Calendar container'] button")
            )
        )
        knop.click()
        print("✅ Agenda knop geklikt.")
    except Exception as e:
        print(f"❌ Kon Agenda knop niet vinden of klikken: {e}")


def update_profiel(nieuwe_data):
    """Voegt nieuwe data toe aan profiel.json."""
    try:
        if os.path.exists(PROFIEL_BESTAND):
            with open(PROFIEL_BESTAND, "r") as f:
                profiel = json.load(f)
        else:
            profiel = {}

        profiel.update(nieuwe_data)

        with open(PROFIEL_BESTAND, "w") as f:
            json.dump(profiel, f, indent=4)
        print(f"💾 Profiel bijgewerkt met: {list(nieuwe_data.keys())}")
    except Exception as e:
        print(f"❌ Kon profiel niet updaten: {e}")


def kies_uit_dropdown(driver, input_id, naam_veld):
    """
    Algemene functie om een dropdown te openen, opties te tonen, gebruiker te laten kiezen en te klikken.
    Returnt de gekozen tekst.
    """
    print(f"\n🔍 Zoeken naar dropdown: {naam_veld}...")
    try:
        wait = WebDriverWait(driver, 10)

        dropdown_input = wait.until(EC.element_to_be_clickable((By.ID, input_id)))
        dropdown_input.click()
        time.sleep(1)

        opties = driver.find_elements(
            By.CSS_SELECTOR, "div[id^='react-select'][role='option']"
        )
        if not opties:
            opties = driver.find_elements(By.CSS_SELECTOR, "div[class*='option']")

        if not opties:
            print(f"⚠️ Geen opties gevonden voor {naam_veld}.")
            return None

        print(f"📋 Beschikbare opties voor {naam_veld}:")
        optie_teksten = [optie.text for optie in opties]

        for i, tekst in enumerate(optie_teksten):
            print(f"   [{i + 1}] {tekst}")

        if "Geen opties" in optie_teksten:
            print(f"⚠️ Dropdown {naam_veld} bevat 'Geen opties'.")
            return "GEEN_OPTIES"

        while True:
            keuze = input(f"👉 Kies een nummer voor {naam_veld}: ")
            try:
                index = int(keuze) - 1
                if 0 <= index < len(opties):
                    gekozen_optie = opties[index]
                    gekozen_tekst = optie_teksten[index]

                    gekozen_optie.click()
                    print(f"✅ Geselecteerd: {gekozen_tekst}")
                    time.sleep(1)
                    return gekozen_tekst
                else:
                    print("Ongeldig nummer, probeer opnieuw.")
            except ValueError:
                print("Voer een geldig nummer in.")

    except Exception as e:
        print(f"❌ Fout bij dropdown {naam_veld}: {e}")
        return None


def selecteer_klant_project_activiteit(driver):
    """Doorloopt de flow: Klant -> Project -> Activiteit."""

    klant = kies_uit_dropdown(driver, "customer", "Klant")
    if not klant:
        return

    project = kies_uit_dropdown(driver, "project", "Project")

    if project == "GEEN_OPTIES":
        print("❌ Geen projecten beschikbaar voor deze klant.")
        opnieuw = input("Wil je een andere klant kiezen? (j/n): ").lower()
        if opnieuw == "j":
            driver.refresh()
            time.sleep(3)
            time.sleep(1)
            selecteer_klant_project_activiteit(driver)
            return
        else:
            return

    if not project:
        return

    activiteit = kies_uit_dropdown(driver, "projectTask", "Activiteit")
    if not activiteit:
        return

    nieuwe_data = {
        "standaard_klant": klant,
        "standaard_project": project,
        "standaard_activiteit": activiteit,
    }
    update_profiel(nieuwe_data)


def vul_dropdown_automatisch(driver, input_id, waarde):
    """Vult een React-Select dropdown in op basis van tekst en drukt op Tab."""
    try:
        wait = WebDriverWait(driver, 10)
        elem = wait.until(EC.element_to_be_clickable((By.ID, input_id)))

        # Scroll naar het element om zeker te zijn dat het zichtbaar is (niet onder een header/kalender)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
        time.sleep(0.25)
        elem.send_keys(waarde)
        time.sleep(1)
        elem.send_keys(Keys.TAB)
    except Exception as e:
        print(f"   ⚠️ Kon dropdown {input_id} niet vullen met '{waarde}': {e}")


def zet_toggle_aan(driver, input_id):
    """Zorgt dat een toggle (bijv. switch) op 'checked' staat."""
    try:
        wait = WebDriverWait(driver, 10)
        # Gebruik CSS selector voor ID's met speciale tekens (zoals :r3:)
        elem = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f"[id='{input_id}']"))
        )

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
        time.sleep(0.25)

        if elem.get_attribute("data-state") != "checked":
            elem.click()
            time.sleep(0.5)
    except Exception as e:
        print(f"   ⚠️ Kon toggle {input_id} niet aanzetten: {e}")


def vul_adres_in(driver, input_id, waarde):
    """Vult een adres in, wacht op de suggesties en selecteert de eerste."""
    try:
        wait = WebDriverWait(driver, 10)
        elem = wait.until(EC.element_to_be_clickable((By.ID, input_id)))

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
        time.sleep(0.25)

        # Adres typen
        elem.send_keys(waarde)

        # Wachten tot de dropdown openklapt (aria-expanded="true")
        try:
            wait.until(lambda d: elem.get_attribute("aria-expanded") == "true")
        except:
            pass  # Als het wachten faalt (timeout), proberen we het alsnog

        time.sleep(1.5)  # Iets langere pauze zodat de opties zeker geladen zijn
        elem.send_keys(Keys.ARROW_DOWN)
        elem.send_keys(Keys.TAB)

    except Exception as e:
        print(f"   ⚠️ Kon adres {input_id} niet vullen: {e}")


def start_en_login():
    """Hulpfunctie: Start driver en zorgt dat je ingelogd bent."""
    driver = start_driver()
    if not driver:
        return None

    ingelogd = False
    if laad_sessie_in(driver):
        print("🎉 Direct ingelogd via opgeslagen sessie!")
        ingelogd = True
    else:
        print("⚠️ Sessie laden mislukt of verlopen. We loggen opnieuw in.")
        try:
            login_met_wachtwoord(driver)
            ingelogd = True
        except Exception:
            print("❌ Kritieke fout bij inloggen.")
    
    return driver if ingelogd else None

def verwerk_uren_excel(driver):
    """Leest uren.xlsx en selecteert voor elke regel de juiste datum in de kalender."""
    print("\n📂 Uren bestand laden en verwerken...")

    if not os.path.exists("uren.xlsx"):
        print("❌ Bestand 'uren.xlsx' niet gevonden.")
        return

    try:
        df = pd.read_excel("uren.xlsx")
        # Zorg dat datum kolom datetime objecten zijn
        df["datum"] = pd.to_datetime(df["datum"])
    except Exception as e:
        print(f"❌ Fout bij lezen Excel: {e}")
        return

    wait = WebDriverWait(driver, 10)

    for index, row in df.iterrows():
        datum = row["datum"]
        datum_str = datum.strftime("%Y-%m-%d")  # Formaat: 2025-12-01
        maand_waarde = str(datum.month - 1)  # HTML value is 0-indexed (Jan=0, Dec=11)
        jaar_waarde = str(datum.year)

        print(f"📅 Bezig met regel {index + 1}: {datum_str}...")

        try:
            # 1. Agenda openen
            klik_agenda(driver)

            # 2. Jaar controleren en selecteren
            jaar_dropdown = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "rdp-years_dropdown"))
            )
            select_jaar = Select(jaar_dropdown)

            if select_jaar.first_selected_option.get_attribute("value") != jaar_waarde:
                select_jaar.select_by_value(jaar_waarde)
                time.sleep(0.5)  # Korte pauze voor UI update

            # 3. Maand controleren en selecteren
            maand_dropdown = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "rdp-months_dropdown"))
            )
            select_maand = Select(maand_dropdown)

            if (
                select_maand.first_selected_option.get_attribute("value")
                != maand_waarde
            ):
                select_maand.select_by_value(maand_waarde)
                time.sleep(0.5)  # Korte pauze voor UI update

            # 4. Dag knop zoeken en klikken
            # We zoeken de <td data-day="..."> en klikken op de <button> daarbinnen
            dag_selector = f"td[data-day='{datum_str}'] button"
            dag_knop = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, dag_selector))
            )
            dag_knop.click()
            print(f"   ✅ Datum {datum_str} geselecteerd.")

            # Kalender geforceerd sluiten door op de body te klikken
            driver.find_element(By.TAG_NAME, "body").click()

            # 5. Dropdowns invullen (Klant, Project, Activiteit)
            vul_dropdown_automatisch(driver, "customer", row["klant"])
            vul_dropdown_automatisch(driver, "project", row["project"])
            vul_dropdown_automatisch(driver, "projectTask", row["activiteit"])

            # 6. Tijden invullen
            # Starttijd (vast op 09:00)
            start_input = driver.find_element(By.ID, "start")
            start_input.send_keys(Keys.CONTROL + "a")
            start_input.send_keys(Keys.BACKSPACE)
            start_input.send_keys("09:00")

            # Eindtijd berekenen (9 + aantal uren)
            time.sleep(0.1)
            aantal_uren = float(row["aantal uren"])
            eind_decimaal = 9.0 + aantal_uren
            eind_uur = int(eind_decimaal)
            eind_minuut = int((eind_decimaal - eind_uur) * 60)
            eind_tijd_str = f"{eind_uur:02d}:{eind_minuut:02d}"
            end_input = driver.find_element(By.ID, "end")
            end_input.send_keys(eind_tijd_str)

            # 7. Opslaan (Klik op 'Voeg uren toe')
            submit_knop = driver.find_element(
                By.XPATH, "//button[@type='submit'][contains(., 'Voeg uren toe')]"
            )
            submit_knop.click()

            print(
                f"   💾 Opgeslagen: {row['klant']} - {aantal_uren} uur (09:00 - {eind_tijd_str})"
            )
            driver.refresh()
            time.sleep(3)  # Korte pauze voor de volgende iteratie
        except Exception as e:
            print(f"   ❌ Fout bij selecteren datum {datum_str}: {e}")


def verwerk_ritten_excel(driver):
    print("\n📂 Ritten bestand laden en verwerken...")

    if not os.path.exists("ritten.xlsx"):
        print("❌ Bestand 'ritten.xlsx' niet gevonden.")
        return

    try:
        df = pd.read_excel("ritten.xlsx")
        # Zorg dat datum kolom datetime objecten zijn
        df["datum"] = pd.to_datetime(df["datum"])
    except Exception as e:
        print(f"❌ Fout bij lezen Excel: {e}")
        return

    wait = WebDriverWait(driver, 10)

    for index, row in df.iterrows():
        datum = row["datum"]
        datum_str = datum.strftime("%Y-%m-%d")  # Formaat: 2025-12-01
        maand_waarde = str(datum.month - 1)  # HTML value is 0-indexed (Jan=0, Dec=11)
        jaar_waarde = str(datum.year)

        print(f"📅 Bezig met regel {index + 1}: {datum_str}...")

        try:
            # 1. Agenda openen
            klik_agenda(driver)

            # 2. Jaar controleren en selecteren
            jaar_dropdown = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "rdp-years_dropdown"))
            )
            select_jaar = Select(jaar_dropdown)

            if select_jaar.first_selected_option.get_attribute("value") != jaar_waarde:
                select_jaar.select_by_value(jaar_waarde)
                time.sleep(0.5)  # Korte pauze voor UI update

            # 3. Maand controleren en selecteren
            maand_dropdown = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "rdp-months_dropdown"))
            )
            select_maand = Select(maand_dropdown)

            if (
                select_maand.first_selected_option.get_attribute("value")
                != maand_waarde
            ):
                select_maand.select_by_value(maand_waarde)
                time.sleep(0.5)  # Korte pauze voor UI update

            # 4. Dag knop zoeken en klikken

            dag_selector = f"td[data-day='{datum_str}'] button"
            dag_knop = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, dag_selector))
            )
            dag_knop.click()
            print(f"   ✅ Datum {datum_str} geselecteerd.")

            # Kalender geforceerd sluiten door op de body te klikken
            driver.find_element(By.TAG_NAME, "body").click()

            # 5. Dropdowns invullen (Klant, Project, Activiteit)
            vul_dropdown_automatisch(driver, "customer", row["klant"])
            vul_dropdown_automatisch(driver, "project", row["project"])
            vul_adres_in(driver, "fromAddress", row["adres_van"])
            vul_adres_in(driver, "toAddress", row["adres_naar"])
            
            # Dynamisch de ID zoeken voor de dropdown (de eerste combobox NA toAddress)
            dropdown_el = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[@id='toAddress']/following::input[@role='combobox'][1]")
            ))
            vul_dropdown_automatisch(driver, dropdown_el.get_attribute("id"), "Zakelijk")
            
            # Dynamisch de ID zoeken voor de toggle (zoek naar een button met role='checkbox')
            toggle_el = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@role='checkbox']")))
            zet_toggle_aan(driver, toggle_el.get_attribute("id"))
            
            # # Opslaan
            # submit_knop = driver.find_element(By.XPATH, "//button[@type='submit']")
            # submit_knop.click()
            
            print(f"   💾 Rit opgeslagen: {row['adres_van']} -> {row['adres_naar']}")
            driver.refresh()
            time.sleep(3) # Korte pauze voor volgende iteratie

        except Exception as e:
            print(f"   ❌ Fout bij regel {index + 1}: {e}")
            time.sleep(2)


def main():
    """Hoofdfunctie om de bot te draaien. Geeft de driver instance terug."""
    driver = start_driver()

    driver.get(BASE_URL)

    ingelogd = False
    if laad_sessie_in(driver):
        print("🎉 Direct ingelogd via opgeslagen sessie!")
        ingelogd = True
    else:
        print("⚠️ Sessie laden mislukt of verlopen. We loggen opnieuw in.")
        try:
            login_met_wachtwoord(driver)
            ingelogd = True
        except Exception:
            print("❌ Kritieke fout bij inloggen.")

    if ingelogd:
        time.sleep(3)
        selecteer_klant_project_activiteit(driver)

    return driver


def nieuwe_automatisering():
    """Nieuwe functie voor extra automatisering."""
    driver = start_en_login()
    if driver:
        print("🚀 Start nieuwe automatisering...")
        driver.get("https://app.timechimp.com/registration/time/day")
        verwerk_uren_excel(driver)

    return driver


def ritten_invullen():
    """Nieuwe functie voor extra automatisering."""
    driver = start_en_login()
    if driver:
        print("🚀 Start nieuwe automatisering...")
        driver.get("https://app.timechimp.com/registration/mileage")
        verwerk_ritten_excel(driver)
    return driver


if __name__ == "__main__":
    # Dit stuk wordt alleen uitgevoerd als je bot.py direct runt
    timechimp_driver = main()
    print("\nKlaar voor actie!")
    input("Druk op ENTER om af te sluiten...")
    timechimp_driver.quit()
