import pandas as pd
from datetime import datetime

# --- CONFIGURATIE ---
# Hulptabel om van maandnaam naar nummer te gaan (nodig voor de range-functie)
maand_naar_nummer = {
    'januari': 1, 'februari': 2, 'maart': 3, 'april': 4, 'mei': 5, 'juni': 6,
    'juli': 7, 'augustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'december': 12
}


# --- FUNCTIE 1: MAAK DE KALENDER ---
def genereer_nederlandse_kalender():
    # 1. Bepaal jaren (vorig, huidig, volgend)
    huidig_jaar = datetime.now().year
    start_datum = f"{huidig_jaar - 1}-01-01"
    eind_datum = f"{huidig_jaar + 1}-12-31"

    # 2. Genereer alle datums
    datums = pd.date_range(start=start_datum, end=eind_datum, freq='D')

    # 3. Maak DataFrame en vul kolommen
    df = pd.DataFrame({'datum': datums})
    df['jaar'] = df['datum'].dt.year
    df['kwartaal'] = df['datum'].dt.quarter
    df['maand_nr'] = df['datum'].dt.month
    df['dag_nr'] = df['datum'].dt.day

    # 4. Vertalingen
    dag_vertaling = {
        'Monday': 'maandag', 'Tuesday': 'dinsdag', 'Wednesday': 'woensdag',
        'Thursday': 'donderdag', 'Friday': 'vrijdag', 'Saturday': 'zaterdag', 'Sunday': 'zondag'
    }
    maand_vertaling = {
        'January': 'januari', 'February': 'februari', 'March': 'maart',
        'April': 'april', 'May': 'mei', 'June': 'juni', 'July': 'juli',
        'August': 'augustus', 'September': 'september', 'October': 'oktober',
        'November': 'november', 'December': 'december'
    }

    df['dag_naam'] = df['datum'].dt.day_name().map(dag_vertaling)
    df['maand_naam'] = df['datum'].dt.month_name().map(maand_vertaling)

    return df


# --- FUNCTIE 2: FILTER DE KALENDER ---
def filter_kalender(df):
    print("\n--- Maak een selectie ---")
    keuze = input("Kies optie: typ 'maand' of 'range': ").strip().lower()

    if keuze == 'maand':
        # Scenario: 1 specifieke maand
        jaar_invoer = int(input("Welk jaar? (bijv. 2025): "))
        maand_invoer = input("Welke maand? (bijv. januari): ").strip().lower()

        masker = (df['jaar'] == jaar_invoer) & (df['maand_naam'] == maand_invoer)
        return df[masker]

    elif keuze == 'range':
        # Scenario: Periode van X tot Y
        print("\n--- Startdatum ---")
        start_jaar = int(input("Jaar: "))
        start_maand_naam = input("Maand: ").strip().lower()

        print("\n--- Einddatum (t/m) ---")
        eind_jaar = int(input("Jaar: "))
        eind_maand_naam = input("Maand: ").strip().lower()

        try:
            # Start is de 1e van de maand
            start_maand_nr = maand_naar_nummer[start_maand_naam]
            start_datum = pd.Timestamp(year=start_jaar, month=start_maand_nr, day=1)

            # Eind is de LAATSTE dag van de maand
            eind_maand_nr = maand_naar_nummer[eind_maand_naam]
            eind_datum = pd.Timestamp(year=eind_jaar, month=eind_maand_nr, day=1) + pd.offsets.MonthEnd(0)

            masker = (df['datum'] >= start_datum) & (df['datum'] <= eind_datum)
            return df[masker]

        except KeyError:
            print("Fout: Controleer of je de maandnamen goed hebt gespeld.")
            return None
    else:
        print("Ongeldige keuze. Typ 'maand' of 'range'.")
        return None


# --- HOOFDPROGRAMMA ---
if __name__ == "__main__":
    # 1. Tabel genereren
    print("Kalender genereren...")
    df_kalender = genereer_nederlandse_kalender()

    # 2. Filteren
    mijn_selectie = filter_kalender(df_kalender)

    # 3. Resultaat verwerken
    if mijn_selectie is not None and not mijn_selectie.empty:
        # HIER GEBEURT DE MAGIC:
        # drop=True zorgt dat de oude index wordt weggegooid in plaats van een kolom te worden
        mijn_selectie = mijn_selectie.reset_index(drop=True)

        # Optioneel: Als je liever bij 1 begint te tellen in plaats van 0:
        # mijn_selectie.index = mijn_selectie.index + 1

        print(f"\nSucces! {len(mijn_selectie)} dagen gevonden.")
        print("-" * 40)
        print(mijn_selectie.head())  # Laat de eerste paar zien (start nu bij 0)
        print("...")
        print(mijn_selectie.tail())  # Laat de laatste paar zien
    else:
        print("\nGeen data gevonden of er ging iets mis.")