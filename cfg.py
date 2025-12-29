import os

# --- BESTANDSNAMEN ---
PROFIEL_BESTAND = "profiel.json"
SESSIE_MAP = "cookies"
SESSIE_BESTAND = "timechimp_compleet.pkl"
SESSIE_PAD = os.path.join(SESSIE_MAP, SESSIE_BESTAND)

# --- EXCEL BESTANDEN ---
EXCEL_ALLDATA = "alldata.xlsx"
EXCEL_UREN = "uren.xlsx"
EXCEL_RITTEN = "ritten.xlsx"

# --- URLS ---
BASE_URL = "https://app.timechimp.com/auth/login"
URL_UREN_DAG = "https://app.timechimp.com/registration/time/day"
URL_RITTEN = "https://app.timechimp.com/registration/mileage"

# --- WACHTTIJDEN ---
TIMEOUT_STD = 10       # Standaard wachttijd voor elementen
TIMEOUT_LONG = 20      # Lange wachttijd (bijv. login)
TIMEOUT_SHORT = 5      # Korte wachttijd (bijv. cookies)

SLEEP_VERWERKRITTENEXCEL_NEXTITEM = 3
SLEEP_UREN_VOLGENDE_ITEM = 3
SLEEP_VULADRESIN = 1

# --- STANDAARD WAARDEN ---
TIJD_START = "09:00"   # Hoe laat begint je werkdag standaard?

# --- VASTE DATA (Business Logic) voor RBI-fridays en aanvullen uren---
ADRES_RBI = "Europalaan 500, Utrecht, Nederland"
INTERN_KLANT = "RBI Solutions"
INTERN_PROJECT = "Intern"
INTERN_ACTIVITEIT = "Overig Intern"
