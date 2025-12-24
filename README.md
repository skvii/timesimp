![Screenshot](timesimp.jpg)
# 🤖 TimeChimp Automatisering
Ken je dat WhatsApp-berichtje dat je eraan herinnert dat je wéér je uren niet hebt ingevuld?
Ik ook. Te vaak. Dus heb ik een automatisering gemaakt. Niet omdat het moest, maar omdat ik om jullie (en mijn mentale rust) geef.

Welkom bij de **TimeChimp Automatiseringstool**. Dit script helpt je bij het genereren van urenregistraties, het exporteren naar Excel en het automatisch invullen van je uren in TimeChimp via een browser-bot.

> ⚠️ **LET OP: Eerste Versie (Beta)**  
> Dit is een eerste versie van de software. Er kan nog van alles misgaan.  
> **Controleer altijd handmatig** in TimeChimp of de uren, projecten en datums correct zijn ingevoerd voordat je ze definitief indient. Gebruik is op eigen risico.

## 🚀 Installatie

Volg onderstaande stappen om het project lokaal draaiende te krijgen. We maken gebruik van **uv** voor razendsnel package management.

### 1. Project Clonen
Haal de code binnen via git:

```bash
git clone https://github.com/skvii/timechimp.git
cd timechimp
```

### 2. UV Installeren (Globaal)
Als je `uv` nog niet hebt, installeer deze dan eerst globaal op je systeem:

```bash
# Voor Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Of via pip
pip install uv
```

### 3. Omgeving opzetten
Initialiseer het project en installeer de afhankelijkheden.

```bash
# Initialiseer een nieuw project (maakt pyproject.toml aan indien niet aanwezig)
uv init


# Synchroniseer de omgeving (maakt de .venv aan)
uv sync
```

## ⚙️ Configuratie

Voordat je begint, moet je een `.env` bestand aanmaken in de hoofdmap van het project. Hierin komen je inloggegevens.

Maak een bestand genaamd `.env` en zet daar het volgende in:

```env
TIMECHIMP_EMAIL=jouw.email@voorbeeld.nl
TIMECHIMP_PASSWORD=JouwGeheimeWachtwoord123!
```

*Opmerking: Dit bestand wordt niet gedeeld via Git, dus je wachtwoord blijft lokaal.*
*Opmerking2: Gebruik .env.example als voorbeeld.*

## 🖥️ Gebruik

Het script wordt aangestuurd vanuit `control.py`. Start het script als volgt:

```bash
uv run control.py
```

### Wat doet het script?
Het script loodst je door 4 stappen:

1.  **Omgeving controleren:** Checkt of je `.env` bestand correct is.
2.  **Profiel laden:** Laadt je instellingen (werkdagen, adressen, contracturen) uit `profiel.json` of helpt je deze aan te maken.
3.  **Browser Bot (Optioneel):** Logt in op TimeChimp om je standaard klant/project/activiteit in te stellen.
4.  **Datums & Excel:**
    *   Genereert een kalender voor een specifieke maand of periode.
    *   Berekent uren, reiskosten en kantoordagen.
    *   Exporteert alles naar `alldata.xlsx`, `uren.xlsx` en `ritten.xlsx`.
    *   **Nieuw:** Kan de `uren.xlsx` automatisch inlezen en boeken in TimeChimp.

## 📁 Bestanden
- `control.py`: Het hoofdbestand dat alles aanstuurt.
- `bot.py`: De Selenium bot die de browser bestuurt.
- `dates.py`: Logica voor kalenders, datums en berekeningen.
- `profiel.py`: Beheert je persoonlijke instellingen.
- `ifexists.py`: Hulpfuncties voor bestandscontrole.
