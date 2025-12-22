import os
from dotenv import load_dotenv

def if_env_exists(path='.env'):
    if os.path.exists(path):
        # Path X
        load_dotenv(dotenv_path=path)
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
        print(f"⚠️ {path} bestand bestaat niet, lees de readme.md")
if __name__ == "__main__":
    if_env_exists()