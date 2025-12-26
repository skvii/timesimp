import json
import os
import time

PROFIEL_BESTAND = "profiel.json"


def vraag_en_valideer(vraag, type_conversie=str):
    """Blijft een vraag stellen tot een geldig antwoord is gegeven."""
    while True:
        antwoord = input(vraag).strip()
        if not antwoord:
            print("Invoer mag niet leeg zijn.")
            continue
        try:
            return type_conversie(antwoord)
        except ValueError:
            print(
                f"Ongeldige invoer. Voer een waarde van het type '{type_conversie.__name__}' in."
            )


def vraag_dagen(vraag):
    """Vraagt om een lijst van dagen, gescheiden door komma's."""
    while True:
        dagen_str = input(vraag).lower()
        dagen_lijst = [dag.strip() for dag in dagen_str.split(",") if dag.strip()]
        if not dagen_lijst:
            print("Voer minimaal één dag in.")
            continue
        return dagen_lijst


def vraag_adres(type_adres):
    """Vraagt straat, huisnummer, postcode en stad en combineert dit tot één string."""
    print(f"\n--- {type_adres} ---")
    straat = vraag_en_valideer("Straatnaam: (geen huisnummer) ")
    huisnummer = vraag_en_valideer("Huisnummer (evt. toevoeging): ")

    stad = vraag_en_valideer("Stad: (bv. Rotterdam)")
    return f"{straat} {huisnummer}, {stad}, Nederland"


def toon_profiel_samenvatting(profiel):
    """Print een nette samenvatting van het geladen profiel."""
    print("\n📋 ..::: Profiel Samenvatting :::..")

    print("   🕒 Uren per dag:")
    uren_per_dag = profiel.get("uren_per_dag", {})
    for dag, uren in uren_per_dag.items():
        print(f"      - {dag.capitalize()}: {uren} uur")

    print(f"   🏠 Huisadres:         {profiel.get('adres_huis')}")
    print(f"   🏢 Werkadres:         {profiel.get('adres_opdrachtgever')}")
    print(
        f"   💼 Kantoordagen:      {', '.join(profiel.get('standaard_kantoordagen', []))}"
    )
    print(f"   📄 Contracturen:      {profiel.get('contract_uren', 'Onbekend')}")

    # Nieuwe velden tonen
    klant = profiel.get("standaard_klant")
    project = profiel.get("standaard_project")
    activiteit = profiel.get("standaard_activiteit")

    print("\n   📌 Standaard Instellingen:")
    if klant and project and activiteit:
        print(f"      - Klant:      {klant}")
        print(f"      - Project:    {project}")
        print(f"      - Activiteit: {activiteit}")
    else:
        print("      ⚠️ Nog niet ingesteld. Dit wordt straks gevraagd.")

    print("------------------------------\n")


def maak_profiel_aan():
    """Stelt vragen aan de gebruiker en bouwt een profiel dictionary op."""
    print("--- Nieuw profiel aanmaken ---")
    print("We gaan eenmalig je profiel instellen.")

    # 1. Werkdagen vragen
    werkdagen = vraag_dagen("Op welke dagen werk je normaal? (ma,di,wo,do,vr): ")

    # 2. Uren per dag vragen
    uren_per_dag = {}
    print("\nHoeveel uur werk je op deze dagen? (in getallen dus bv. 4 of 8")
    for dag in werkdagen:
        uren = vraag_en_valideer(f"  - {dag.capitalize()}: ", float)
        uren_per_dag[dag] = uren

    # 3. Adressen vragen
    adres_huis = vraag_adres("Huisadres")
    adres_werk = vraag_adres("Adres Opdrachtgever")

    # 4. Kantoordagen vragen
    kantoordagen = vraag_dagen("\nWat zijn je standaard kantoordagen? (bijv. di,do): ")

    # 5. Contracturen vragen
    print("\n--- Contractgegevens ---")
    contract_uren = vraag_en_valideer(
        "Hoeveel uur is je contract per week? (bv. 32, 36, 40): ", float
    )

    profiel = {
        "standaard_werkdagen": werkdagen,
        "uren_per_dag": uren_per_dag,
        "adres_huis": adres_huis,
        "adres_opdrachtgever": adres_werk,
        "standaard_kantoordagen": kantoordagen,
        "contract_uren": contract_uren,
    }

    try:
        with open(PROFIEL_BESTAND, "w") as f:
            json.dump(profiel, f, indent=4)
        print(f"\n✅ Profiel opgeslagen in {PROFIEL_BESTAND}")
        toon_profiel_samenvatting(profiel)
        return profiel
    except Exception as e:
        print(f"❌ Fout bij opslaan profiel: {e}")
        return profiel


def laad_of_maak_profiel():
    """
    Controleert of het profielbestand bestaat.
    Zo ja, laadt het en toont een samenvatting.
    Zo nee, start de procedure om het aan te maken.
    """
    if os.path.exists(PROFIEL_BESTAND):
        print(f"✅ Profiel ({PROFIEL_BESTAND}) gevonden.")
        try:
            with open(PROFIEL_BESTAND, "r") as f:
                profiel = json.load(f)

            # Check of contract_uren bestaat, zo niet, vraag erom en sla op
            if "contract_uren" not in profiel:
                print("\n⚠️ Contracturen ontbreken in je profiel.")
                contract_uren = vraag_en_valideer(
                    "Hoeveel uur is je contract per week? (bv. 32, 36, 40): ", float
                )
                profiel["contract_uren"] = contract_uren
                with open(PROFIEL_BESTAND, "w") as f_out:
                    json.dump(profiel, f_out, indent=4)
                print("✅ Contracturen toegevoegd aan profiel.")

            toon_profiel_samenvatting(profiel)
            return profiel

        except json.JSONDecodeError:
            print(f"❌ Fout: {PROFIEL_BESTAND} is beschadigd of leeg.")
            keuze = input("Wil je een nieuw profiel aanmaken? (j/n): ").lower()
            if keuze == "j":
                return maak_profiel_aan()
            else:
                print("Kan niet verder zonder geldig profiel.")
                exit()
        except Exception as e:
            print(f"❌ Onverwachte fout bij laden profiel: {e}")
            exit()
    else:
        print(f"⚠️ Profiel ({PROFIEL_BESTAND}) niet gevonden.")
        return maak_profiel_aan()
