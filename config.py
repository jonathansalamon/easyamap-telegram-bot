import os

# --- VARIABLES D'ENVIRONNEMENT ---
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
TOPIC_ID = os.environ.get('TELEGRAM_TOPIC_ID')
USERNAME = os.environ.get('AMAP_USERNAME')
PASSWORD = os.environ.get('AMAP_PASSWORD')

# --- CONSTANTES ---
BASE_DOMAIN = "https://votre-amap.easyamap.fr"

LOGIN_URL = f"{BASE_DOMAIN}/login"
BASE_PRODUCTS_URL = f"{BASE_DOMAIN}/produits_a_recuperer"
CONTRACTS_URL = f"{BASE_DOMAIN}/liste_contrats"
