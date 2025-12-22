# Dit is het hoofdbestand om de verschillende onderdelen van het project aan te sturen.

from ifexists import if_env_exists
from profiel import laad_of_maak_profiel
from dates import genereer_nederlandse_kalender, filter_kalender, voeg_uren_toe, voeg_adressen_en_kantoordag_toe, voeg_projectgegevens_toe, controleer_en_vul_contracturen
from bot import main as run_bot_main # Geef de main functie een duidelijke naam
import pandas as pd

# --- STAP 1: OMGEVING CONTROLEREN ---
print("--- Stap 1: Omgeving controleren ---")
if_env_exists()

# --- STAP 2: PROFIEL LADEN OF AANMAKEN ---
print("\n--- Stap 2: Profiel laden ---")
profiel_data = laad_of_maak_profiel()

# --- STAP 3: STANDAARD KEUZES BIJWERKEN (OPTIONEEL) ---
# Vragen of de gebruiker de standaard klant/project/activiteit wil instellen/bijwerken
if 'standaard_klant' not in profiel_data:
    print("\n⚠️ Je hebt nog geen standaard klant, project en activiteit ingesteld.")
    run_bot_vraag = 'j' # Forceer de bot om te runnen als het de eerste keer is
else:
    run_bot_vraag = input("\nWil je de standaard klant/project/activiteit bijwerken? (j/n): ").lower()

if run_bot_vraag == 'j':
    print("\n--- Stap 3: Standaard keuzes instellen via browser ---")
    # Roep de main functie van de bot aan, deze geeft de driver terug
    timechimp_driver = run_bot_main() 
    
    print("\nBrowser acties zijn voltooid.")
    input("Druk op ENTER om de browser te sluiten...")
    timechimp_driver.quit()
else:
    print("\nStap 3 overgeslagen.")

# --- STAP 4: DATUMS SELECTEREN (OPTIONEEL) ---
run_dates = input("\nWil je datums selecteren voor urenregistratie? (j/n): ").lower()
if run_dates == 'j':
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
        df_met_uren = voeg_uren_toe(mijn_selectie)
        
        if df_met_uren is not None:
            # Vraag om weekenddagen te verwijderen
            verwijder_weekend = input("\nWil je weekenddagen (zaterdag en zondag) uit de lijst halen? (j/n): ").strip().lower()
            if verwijder_weekend == 'j':
                # Filter zaterdag en zondag eruit
                df_met_uren = df_met_uren[~df_met_uren['dag'].isin(['zaterdag', 'zondag'])]
                # Reset index voor netheid
                df_met_uren = df_met_uren.reset_index(drop=True)
                print("Weekenddagen zijn verwijderd.")

            # --- RBI FRIDAY SELECTIE ---
            # Filter alle vrijdagen
            vrijdagen = df_met_uren[df_met_uren['dag'] == 'vrijdag']
            
            rbi_indices = []
            if not vrijdagen.empty:
                print("\n--- RBI Friday Selectie ---")
                print("De volgende vrijdagen zijn gevonden:")
                
                # Maak een tijdelijke view met een schone index voor de gebruiker (0, 1, 2...)
                # reset_index() zet de oude index in een kolom genaamd 'index'
                vrijdagen_display = vrijdagen.reset_index()
                
                # Toon de lijst met de nieuwe tijdelijke index
                print(vrijdagen_display[['datum', 'dag', 'aantal uren']])
                
                print("\nGeef de indexnummers op van de vrijdagen die een 'RBI Friday' zijn (gescheiden door komma's, bijv: 0, 2).")
                print("Druk op Enter als er geen RBI Fridays zijn.")
                keuze_rbi = input("Indexnummers: ").strip()
                
                if keuze_rbi:
                    try:
                        gekozen_display_indices = [int(x.strip()) for x in keuze_rbi.split(',') if x.strip()]
                        
                        # Vertaal de gekozen display-indices terug naar de originele indices in df_met_uren
                        for display_idx in gekozen_display_indices:
                            if display_idx in vrijdagen_display.index:
                                # Haal de originele index op uit de 'index' kolom
                                original_idx = vrijdagen_display.at[display_idx, 'index']
                                rbi_indices.append(original_idx)
                            else:
                                print(f"Waarschuwing: Index {display_idx} bestaat niet in de getoonde lijst.")
                                
                    except ValueError:
                        print("Ongeldige invoer. Geen RBI Fridays gemarkeerd.")

            # Voeg kolom toe, standaard 'nee'
            df_met_uren['RBI_friday'] = 'nee'
            
            # Zet 'ja' voor de gekozen indices
            for idx in rbi_indices:
                df_met_uren.at[idx, 'RBI_friday'] = 'ja'

            # --- ADRESSEN EN KANTOORDAGEN TOEVOEGEN ---
            print("\n--- Adressen en kantoordagen toevoegen ---")
            df_compleet = voeg_adressen_en_kantoordag_toe(df_met_uren)
            
            if df_compleet is not None:
                # --- PROJECTGEGEVENS TOEVOEGEN ---
                print("\n--- Projectgegevens toevoegen ---")
                df_final = voeg_projectgegevens_toe(df_compleet)
                
                # --- CONTRACTUREN CONTROLEREN ---
                print("\n--- Contracturen controleren ---")
                df_final = controleer_en_vul_contracturen(df_final)
                
                if df_final is not None:
                    print("\nVolledige urenregistratie tabel:")
                    # Toon alle kolommen om te controleren
                    pd.set_option('display.max_columns', None)
                    pd.set_option('display.width', 1000)
                    print(df_final)
    else:
        print("\nGeen data gevonden of er ging iets mis.")
else:
    print("\nStap 4 overgeslagen.")

print("\nScript is klaar.")
