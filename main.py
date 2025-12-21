import os
from dotenv import load_dotenv
from dates import *

if os.path.exists('.env'):
    # Path X
    load_dotenv()
    email = os.getenv("TIMECHIMP_EMAIL")
    password = os.getenv("TIMECHIMP_PASSWORD")

    if email:
        print(f"✅ Email gevonden: {email}")
    else:
        print("⚠️ Email ontbreekt in .env")

    if password:
        print("✅ Wachtwoord is ingevuld (niet getoond om veiligheidsredenen)")
    else:
        print("⚠️ Wachtwoord ontbreekt in .env")

else:
    # Path Y
    print("⚠️.env bestand bestaat niet, lees de readme.md")

#/#/#