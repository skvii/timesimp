# Dit is het hoofdbestand om de verschillende onderdelen van het project aan te sturen.
from ifexists import if_env_exists, check_bestanden
from profiel import laad_of_maak_profiel
from dates import (
    genereer_nederlandse_kalender,
    filter_kalender,
    voeg_uren_toe,
    voeg_adressen_en_kantoordag_toe,
    voeg_projectgegevens_toe,
    controleer_en_vul_contracturen,
)
from bot import (
    main as run_bot_main,
    uren_invullen,
    ritten_invullen,
)

import pandas as pd
import sys

print("-- check 1: bestaat .env bestand?")
if_env_exists()


print("\n..::: Check (2/2): Profiel laden ::..")
profiel_data = laad_of_maak_profiel()

# --- STAP 3: STANDAARD KEUZES BIJWERKEN (OPTIONEEL) ---
# Vragen of de gebruiker de standaard klant/project/activiteit wil instellen/bijwerken
if "standaard_klant" not in profiel_data:
    print("\n⚠️ Je hebt nog geen standaard klant, project en activiteit ingesteld.")
    run_bot_vraag = "j"  # Forceer de bot om te runnen als het de eerste keer is
else:
    run_bot_vraag = input(
        "\nWil je de standaard klant/project/activiteit bijwerken? (j/n): "
    ).lower()

if run_bot_vraag == "j":
    print("\n--- Stap 3: Standaard keuzes instellen via browser ---")
    try:
        # Roep de main functie van de bot aan, deze geeft de driver terug
        timechimp_driver = run_bot_main()

        print("\nBrowser acties zijn voltooid.")
        input("Druk op ENTER om de browser te sluiten...")
        timechimp_driver.quit()
    except Exception as e:
        print(f"\n❌ Er ging iets mis met de browser bot: {e}")
        print("We gaan verder met de rest van het script...")
else:
    print("\nStap 3 overgeslagen.")

# --- STAP 4: DATUMS SELECTEREN (OPTIONEEL) ---
# Check of bestanden al bestaan
bestanden_lijst = ["alldata.xlsx", "uren.xlsx", "ritten.xlsx"]
check_bestanden(bestanden_lijst)
run_dates = input(
    "\nWil je datums selecteren voor een nieuwe urenregistratie? (j/n): "
).lower()
if run_dates == "j":
    print("\n--- Stap 4: Datums selecteren ---")
    df_kalender = genereer_nederlandse_kalender()
    mijn_selectie = filter_kalender(df_kalender)

    # Resultaat verwerken
    if mijn_selectie is not None and not mijn_selectie.empty:
        mijn_selectie = mijn_selectie.reset_index(drop=True)
        mijn_selectie.index = mijn_selectie.index + 1

        print(f"\n✅ Succes! {len(mijn_selectie)} dagen gevonden.")
        print("-" * 40)
        print("Geselecteerde datums:")
        print(mijn_selectie)

        # Uren toevoegen
        print("\n--- Uren berekenen op basis van profiel ---")
        df_met_uren = voeg_uren_toe(mijn_selectie, profiel_data)

        if df_met_uren is not None:
            # Vraag om weekenddagen te verwijderen
            verwijder_weekend = (
                input(
                    "\nWil je weekenddagen (zaterdag en zondag) uit de lijst halen? (j/n): "
                )
                .strip()
                .lower()
            )
            if verwijder_weekend == "j":
                # Filter zaterdag en zondag eruit
                df_met_uren = df_met_uren[
                    ~df_met_uren["dag"].isin(["zaterdag", "zondag"])
                ]
                # Reset index voor netheid
                df_met_uren = df_met_uren.reset_index(drop=True)
                print("Weekenddagen zijn verwijderd.")

            # --- RBI FRIDAY SELECTIE ---
            # Filter alle vrijdagen
            vrijdagen = df_met_uren[df_met_uren["dag"] == "vrijdag"]

            rbi_indices = []
            if not vrijdagen.empty:
                print("\n--- RBI Friday Selectie ---")
                print("De volgende vrijdagen zijn gevonden:")

                # Maak een tijdelijke view met een schone index voor de gebruiker (0, 1, 2...)
                # reset_index() zet de oude index in een kolom genaamd 'index'
                vrijdagen_display = vrijdagen.reset_index()

                # Toon de lijst met de nieuwe tijdelijke index
                print(vrijdagen_display[["datum", "dag", "aantal uren"]])

                print(
                    "\nGeef de indexnummers op van de vrijdagen die een 'RBI Friday' zijn (gescheiden door komma's, bijv: 0, 2)."
                )
                print("Druk op Enter als er geen RBI Fridays zijn.")
                keuze_rbi = input("Indexnummers: ").strip()

                if keuze_rbi:
                    try:
                        gekozen_display_indices = [
                            int(x.strip()) for x in keuze_rbi.split(",") if x.strip()
                        ]

                        # Vertaal de gekozen display-indices terug naar de originele indices in df_met_uren
                        for display_idx in gekozen_display_indices:
                            if display_idx in vrijdagen_display.index:
                                # Haal de originele index op uit de 'index' kolom
                                original_idx = vrijdagen_display.at[
                                    display_idx, "index"
                                ]
                                rbi_indices.append(original_idx)
                            else:
                                print(
                                    f"Waarschuwing: Index {display_idx} bestaat niet in de getoonde lijst."
                                )

                    except ValueError:
                        print("Ongeldige invoer. Geen RBI Fridays gemarkeerd.")

            # Voeg kolom toe, standaard 'nee'
            df_met_uren["RBI_friday"] = "nee"

            # Zet 'ja' voor de gekozen indices
            for idx in rbi_indices:
                df_met_uren.at[idx, "RBI_friday"] = "ja"

            # --- ADRESSEN EN KANTOORDAGEN TOEVOEGEN ---
            print("\n--- Adressen en kantoordagen toevoegen ---")
            df_compleet = voeg_adressen_en_kantoordag_toe(df_met_uren, profiel_data)

            if df_compleet is not None:
                # --- PROJECTGEGEVENS TOEVOEGEN ---
                print("\n--- Projectgegevens toevoegen ---")
                df_final = voeg_projectgegevens_toe(df_compleet, profiel_data)

                # --- CONTRACTUREN CONTROLEREN ---
                print("\n--- Contracturen controleren ---")
                df_final = controleer_en_vul_contracturen(df_final, profiel_data)

                if df_final is not None:
                    print("\nVolledige urenregistratie tabel:")
                    # Toon alle kolommen om te controleren
                    pd.set_option("display.max_columns", None)
                    pd.set_option("display.width", 1000)
                    print(df_final)

                    # --- EXPORT NAAR EXCEL ---
                    print("\n--- Exporteren naar Excel ---")

                    while True:
                        try:
                            # Selecteer specinfieke kolommen voor uren en ritten
                            uren_df = df_final[
                                [
                                    "datum",
                                    "dag",
                                    "aantal uren",
                                    "klant",
                                    "project",
                                    "activiteit",
                                ]
                            ]

                            # --- RITTEN FILTEREN ---
                            # 1. Selecteer kolommen
                            ritten_df = df_final[
                                [
                                    "datum",
                                    "dag",
                                    "adres_van",
                                    "adres_naar",
                                    "kantoordag",
                                    "klant",
                                    "RBI_friday",
                                    "project",
                                ]
                            ]

                            # 2. Filter op kantoordag='ja' OF RBI_friday='ja'
                            ritten_df = ritten_df[
                                (ritten_df["kantoordag"] == "ja")
                                | (ritten_df["RBI_friday"] == "ja")
                            ]

                            # 3. Ontdubbelen op datum (behoud eerste)
                            ritten_df = ritten_df.drop_duplicates(
                                subset=["datum"], keep="first"
                            )

                            # Verwijder RBI_friday kolom weer voor de export (optioneel, maar netter)
                            if "RBI_friday" in ritten_df.columns:
                                ritten_df = ritten_df.drop(columns=["RBI_friday"])

                            # Schrijf naar Excel bestanden
                            df_final.to_excel("alldata.xlsx", index=False)
                            uren_df.to_excel("uren.xlsx", index=False)
                            ritten_df.to_excel("ritten.xlsx", index=False)

                            print("✅ Data succesvol geëxporteerd naar:")
                            print("   - alldata.xlsx")
                            print("   - uren.xlsx")
                            print("   - ritten.xlsx")
                            break  # Succes, dus uit de loop
                        except PermissionError:
                            print("\n❌ Fout: Een van de Excel-bestanden is geopend.")
                            print(
                                "   Sluit de bestanden (alldata.xlsx, uren.xlsx, ritten.xlsx) en probeer opnieuw."
                            )
                            retry = input(
                                "   Druk op ENTER om opnieuw te proberen (of typ 'q' om te stoppen): "
                            ).lower()
                            if retry == "q":
                                print("Export geannuleerd.")
                                break
                        except Exception as e:
                            print(f"❌ Onverwachte fout bij exporteren: {e}")
                            break
    else:
        print("\nGeen data gevonden of er ging iets mis.")
else:
    print("\n⏭️  Geen nieuwe uren/ritten geschreven...")

print("\n🚀 In de volgende stap worden de uren automatisch in TimeChimp gezet.")
print(
    "   Hierbij wordt gebruik gemaakt van de bestanden: 'uren.xlsx', 'ritten.xlsx' en 'alldata.xlsx'."
)
print(
    "\n⚠️  Wil je nog handmatige wijzigingen doen in de Excel-bestanden? Doe dat dan NU. Lees eventueel README.MD."
)
print(
    "   Als je nog geen template hebt gemaakt, start het script dan opnieuw en kies 'j' bij Stap 4."
)
start_or_not = input(
    "\nDruk op ENTER om de automatisering te starten... (of q om te sluiten)"
).lower()
if start_or_not == "q":
    sys.exit()

run_mileage_or_hours = input(
    "\nWat wil je doen?\n⏱️ 1. Uren boeken\n🚗 2. Ritten boeken\n🔃 3. Uren & ritten boeken\nKeuze: "
)

if run_mileage_or_hours == "1":
    uren_invullen()
elif run_mileage_or_hours == "2":
    ritten_invullen()
elif run_mileage_or_hours == "3":
    uren_invullen()
    ritten_invullen()

sys.exit()
