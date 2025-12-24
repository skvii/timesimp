import pandas as pd
from datetime import datetime
import json

# --- CONFIGURATIE ---
# Hulptabel om van maandnaam naar nummer te gaan (nodig voor de range-functie)
maand_naar_nummer = {
    "januari": 1,
    "februari": 2,
    "maart": 3,
    "april": 4,
    "mei": 5,
    "juni": 6,
    "juli": 7,
    "augustus": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "december": 12,
}


# --- FUNCTIE 1: MAAK DE KALENDER ---
def genereer_nederlandse_kalender():
    # 1. Bepaal jaren (vorig, huidig, volgend)
    huidig_jaar = datetime.now().year
    start_datum = f"{huidig_jaar - 1}-01-01"
    eind_datum = f"{huidig_jaar + 1}-12-31"

    # 2. Genereer alle datums
    datums = pd.date_range(start=start_datum, end=eind_datum, freq="D")

    # 3. Maak DataFrame en vul kolommen
    df = pd.DataFrame({"datum": datums})

    # Ensure 'datum' is datetime type for .dt accessor to work correctly
    df["datum"] = pd.to_datetime(df["datum"])

    # noinspection PyTypeChecker
    df["jaar"] = df["datum"].dt.year
    # noinspection PyTypeChecker
    df["kwartaal"] = df["datum"].dt.quarter
    # noinspection PyTypeChecker
    df["maand_nr"] = df["datum"].dt.month
    # noinspection PyTypeChecker
    df["dag_nr"] = df["datum"].dt.day

    # 4. Vertalingen
    dag_vertaling = {
        "Monday": "maandag",
        "Tuesday": "dinsdag",
        "Wednesday": "woensdag",
        "Thursday": "donderdag",
        "Friday": "vrijdag",
        "Saturday": "zaterdag",
        "Sunday": "zondag",
    }
    maand_vertaling = {
        "January": "januari",
        "February": "februari",
        "March": "maart",
        "April": "april",
        "May": "mei",
        "June": "juni",
        "July": "juli",
        "August": "augustus",
        "September": "september",
        "October": "oktober",
        "November": "november",
        "December": "december",
    }

    # noinspection PyUnresolvedReferences
    df["dag_naam"] = df["datum"].dt.day_name().map(dag_vertaling)
    # noinspection PyUnresolvedReferences
    df["maand_naam"] = df["datum"].dt.month_name().map(maand_vertaling)

    return df


# --- FUNCTIE 2: FILTER DE KALENDER ---
def filter_kalender(df):
    print("\n--- Maak een selectie ---")
    keuze = input("Kies optie: typ 'maand' of 'range': ").strip().lower()

    if keuze == "maand":
        # Scenario: 1 specifieke maand
        try:
            jaar_invoer = int(input("Welk jaar? (bijv. 2025): "))
            maand_invoer = input("Welke maand? (bijv. januari): ").strip().lower()

            masker = (df["jaar"] == jaar_invoer) & (df["maand_naam"] == maand_invoer)
            return df[masker]
        except ValueError:
            print("Ongeldige invoer voor jaar.")
            return None

    elif keuze == "range":
        # Scenario: Periode van X tot Y
        try:
            print("\n--- Startdatum ---")
            start_jaar = int(input("Jaar: "))
            start_maand_naam = input("Maand: ").strip().lower()

            print("\n--- Einddatum (t/m) ---")
            eind_jaar = int(input("Jaar: "))
            eind_maand_naam = input("Maand: ").strip().lower()

            # Start is de 1e van de maand
            start_maand_nr = maand_naar_nummer[start_maand_naam]
            start_datum = pd.Timestamp(year=start_jaar, month=start_maand_nr, day=1)

            # Eind is de LAATSTE dag van de maand
            eind_maand_nr = maand_naar_nummer[eind_maand_naam]
            eind_datum = pd.Timestamp(
                year=eind_jaar, month=eind_maand_nr, day=1
            ) + pd.offsets.MonthEnd(0)

            masker = (df["datum"] >= start_datum) & (df["datum"] <= eind_datum)
            return df[masker]

        except KeyError:
            print("Fout: Controleer of je de maandnamen goed hebt gespeld.")
            return None
        except ValueError:
            print("Fout: Ongeldige invoer voor jaar.")
            return None
    else:
        print("Ongeldige keuze. Typ 'maand' of 'range'.")
        return None


# --- FUNCTIE 3: BEREKEN WERKUREN ---
def voeg_uren_toe(mijn_selectie):
    try:
        with open("profiel.json", "r") as f:
            profiel = json.load(f)
    except FileNotFoundError:
        print("Fout: profiel.json niet gevonden.")
        return None

    uren_per_dag = profiel.get("uren_per_dag", {})

    # Mapping van volledige dagnaam naar korte dagnaam zoals in profiel.json
    dag_vertaling_kort = {
        "maandag": "ma",
        "dinsdag": "di",
        "woensdag": "wo",
        "donderdag": "do",
        "vrijdag": "vr",
        "zaterdag": "za",
        "zondag": "zo",
    }

    # Lijst opbouwen met uren
    uren_lijst = []
    for dag_naam in mijn_selectie["dag_naam"]:
        dag_kort = dag_vertaling_kort.get(dag_naam)
        # Haal uren op, default naar 0.0 als dag niet in profiel staat
        uren = uren_per_dag.get(dag_kort, 0.0)
        uren_lijst.append(uren)

    # Nieuw DataFrame maken
    df_uren = pd.DataFrame(
        {
            "datum": mijn_selectie["datum"],
            "dag": mijn_selectie["dag_naam"],
            "aantal uren": uren_lijst,
        }
    )

    return df_uren


# --- FUNCTIE 4: VOEG ADRESSEN EN KANTOORDAG TOE ---
def voeg_adressen_en_kantoordag_toe(df_met_uren):
    try:
        with open("profiel.json", "r") as f:
            profiel = json.load(f)
    except FileNotFoundError:
        print("Fout: profiel.json niet gevonden.")
        return None

    adres_huis = profiel.get("adres_huis", "")
    adres_werk = profiel.get("adres_opdrachtgever", "")
    standaard_kantoordagen = profiel.get("standaard_kantoordagen", [])

    # Mapping van volledige dagnaam naar korte dagnaam
    dag_vertaling_kort = {
        "maandag": "ma",
        "dinsdag": "di",
        "woensdag": "wo",
        "donderdag": "do",
        "vrijdag": "vr",
        "zaterdag": "za",
        "zondag": "zo",
    }

    adres_van_lijst = []
    adres_naar_lijst = []
    kantoordag_lijst = []

    for index, row in df_met_uren.iterrows():
        dag_naam = row["dag"]
        rbi_friday = row.get("RBI_friday", "nee")

        # 1. Adres van (altijd thuis)
        adres_van_lijst.append(adres_huis)

        # 2. Adres naar
        if rbi_friday == "ja":
            adres_naar_lijst.append("Europalaan 500, Utrecht, Nederland")
        else:
            adres_naar_lijst.append(adres_werk)

        # 3. Kantoordag
        dag_kort = dag_vertaling_kort.get(dag_naam)

        # Check of het een standaard kantoordag is
        is_kantoordag = dag_kort in standaard_kantoordagen

        # Specifieke logica voor vrijdag en RBI
        if dag_naam == "vrijdag":
            if rbi_friday == "ja":
                is_kantoordag = (
                    False  # RBI Friday is geen kantoordag (volgens instructie)
                )
            # Als het geen RBI Friday is, blijft de standaard check (is_kantoordag) geldig
            # Dus als vr in standaard_kantoordagen zit, is het True, anders False

        kantoordag_lijst.append("ja" if is_kantoordag else "nee")

    # Voeg kolommen toe aan een kopie van de dataframe
    df_uitgebreid = df_met_uren.copy()
    df_uitgebreid["adres_van"] = adres_van_lijst
    df_uitgebreid["adres_naar"] = adres_naar_lijst
    df_uitgebreid["kantoordag"] = kantoordag_lijst

    return df_uitgebreid


# --- FUNCTIE 5: VOEG STANDAARD PROJECTGEGEVENS TOE ---
def voeg_projectgegevens_toe(df_compleet):
    try:
        with open("profiel.json", "r") as f:
            profiel = json.load(f)
    except FileNotFoundError:
        print("Fout: profiel.json niet gevonden.")
        return None

    klant = profiel.get("standaard_klant", "")
    project = profiel.get("standaard_project", "")
    activiteit = profiel.get("standaard_activiteit", "")

    df_final = df_compleet.copy()
    df_final["klant"] = klant
    df_final["project"] = project
    df_final["activiteit"] = activiteit

    return df_final


# --- FUNCTIE 6: CONTROLEER CONTRACTUREN ---
def controleer_en_vul_contracturen(df_final):
    try:
        with open("profiel.json", "r") as f:
            profiel = json.load(f)
    except FileNotFoundError:
        print("Fout: profiel.json niet gevonden.")
        return df_final

    contract_uren = profiel.get("contract_uren")
    if not contract_uren:
        print("Geen contracturen gevonden in profiel. Sla controle over.")
        return df_final

    contract_uren = float(contract_uren)

    # Voeg tijdelijke kolommen toe voor weeknummering
    # isocalendar() geeft (year, week, weekday)
    df_werk = df_final.copy()
    df_werk["iso_jaar"] = df_werk["datum"].dt.isocalendar().year
    df_werk["iso_week"] = df_werk["datum"].dt.isocalendar().week

    nieuwe_rijen = []

    # Groepeer per jaar en week
    for (jaar, week), group in df_werk.groupby(["iso_jaar", "iso_week"]):
        totaal_uren = group["aantal uren"].sum()

        if totaal_uren < contract_uren:
            tekort = contract_uren - totaal_uren
            print(
                f"\n⚠️ Week {week} ({jaar}): {totaal_uren} uur geboekt. Contract is {contract_uren} uur."
            )
            print(f"   Er ontbreken {tekort} uren.")

            keuze = (
                input(
                    f"   Wil je {tekort} uur toevoegen aan de vrijdag van deze week? (j/n): "
                )
                .strip()
                .lower()
            )

            if keuze == "j":
                # Zoek de vrijdag in deze groep
                vrijdag_rijen = group[group["dag"] == "vrijdag"]

                if not vrijdag_rijen.empty:
                    # Kopieer de eerste gevonden vrijdagrij
                    # We gebruiken iloc[0] van de groep, en zorgen dat we een Series krijgen
                    bron_rij = vrijdag_rijen.iloc[0].copy()

                    # Pas de uren aan naar het tekort
                    bron_rij["aantal uren"] = tekort

                    # Pas klant, project en activiteit aan
                    bron_rij["klant"] = "RBI Solutions"
                    bron_rij["project"] = "Intern"
                    bron_rij["activiteit"] = "Overig Intern"

                    # Verwijder de tijdelijke kolommen uit de bron_rij voordat we hem opslaan
                    # (anders krijgen we warnings bij concat als we ze later droppen)
                    if "iso_jaar" in bron_rij:
                        del bron_rij["iso_jaar"]
                    if "iso_week" in bron_rij:
                        del bron_rij["iso_week"]

                    nieuwe_rijen.append(bron_rij)
                    print(
                        f"   ✅ {tekort} uur toegevoegd aan vrijdag {bron_rij['datum'].strftime('%Y-%m-%d')}."
                    )
                else:
                    print(
                        "   ❌ Geen vrijdag gevonden in de selectie van deze week. Kan niet kopiëren."
                    )
            else:
                print("   Geen actie ondernomen.")

    # Als er nieuwe rijen zijn, voeg ze toe aan de originele dataframe
    if nieuwe_rijen:
        df_extra = pd.DataFrame(nieuwe_rijen)
        df_final = pd.concat([df_final, df_extra], ignore_index=True)

        # Sorteer opnieuw op datum zodat de nieuwe vrijdag netjes bij de week staat
        df_final = df_final.sort_values(by="datum").reset_index(drop=True)

    return df_final


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
        mijn_selectie.index = mijn_selectie.index + 1

        print(f"\nSucces! {len(mijn_selectie)} dagen gevonden.")
        print("-" * 40)
        print(mijn_selectie.head())  # Laat de eerste paar zien (start nu bij 0)
        print("...")
        print(mijn_selectie.tail())  # Laat de laatste paar zien

        # 4. Uren toevoegen
        print("\n--- Uren berekenen op basis van profiel ---")
        df_met_uren = voeg_uren_toe(mijn_selectie)
        if df_met_uren is not None:
            # Test nieuwe functie (mock RBI_friday kolom als die er niet is)
            if "RBI_friday" not in df_met_uren.columns:
                df_met_uren["RBI_friday"] = "nee"

            print("\n--- Adressen en kantoordagen toevoegen ---")
            df_compleet = voeg_adressen_en_kantoordag_toe(df_met_uren)
            if df_compleet is not None:
                print("\n--- Projectgegevens toevoegen ---")
                df_final = voeg_projectgegevens_toe(df_compleet)

                print("\n--- Contracturen controleren ---")
                df_final = controleer_en_vul_contracturen(df_final)
                print(df_final)

    else:
        print("\nGeen data gevonden of er ging iets mis.")
