import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import locale
import traceback
import config

# --- SESSION ET CACHE GLOBAL ---
session = requests.Session()

CACHE_PANIER_DATA = None
CACHE_PANIER_DATE = None
CACHE_CONTRACTS_DATA = None
CACHE_CONTRACTS_DATE = None

# --- FONCTIONS UTILITAIRES (PRIVÉES) ---

def _perform_login():
    """Effectue la connexion au site (logique interne)."""
    print("🔄 Session expirée, tentative de connexion...")
    try:
        res = session.get(config.LOGIN_URL, timeout=15)
        soup = BeautifulSoup(res.content, 'html.parser')
        csrf_input = soup.find('input', {'name': '_csrf_token'})
        
        if not csrf_input:
            print("❌ ERREUR : Token CSRF introuvable.")
            return False
        
        login_data = {
            'username': config.USERNAME,
            'password': config.PASSWORD,
            '_csrf_token': csrf_input['value']
        }
        
        # On tente le login
        post_res = session.post(config.LOGIN_URL, data=login_data, timeout=15, allow_redirects=True)
        
        # Si on est toujours sur la page de login, c'est un échec
        if post_res.url.startswith(config.LOGIN_URL):
            print("❌ ERREUR : Login échoué (Toujours sur la page de login).")
            return False
            
        print("✅ Connexion réussie !")
        return True
    except Exception as e:
        print(f"💥 Erreur login : {e}")
        return False

def _get_with_auto_login(target_url):
    """
    Wrapper intelligent : Tente d'accéder à une URL.
    Si redirigé vers le login, se connecte et réessaie.
    """
    try:
        res = session.get(target_url, timeout=15)
        
        # Si l'URL finale correspond à l'URL de login définie dans la config
        if res.url.startswith(config.LOGIN_URL):
            if not _perform_login():
                return None
            # Nouvelle tentative après connexion réussie
            res = session.get(target_url, timeout=15)
            
        return res
    except Exception as e:
        print(f"💥 Erreur requête ({target_url}) : {e}")
        return None

# --- FONCTIONS PUBLIQUES (MÉTIER) ---

def get_amap_data(start_date=None):
    """Récupère les produits (Panier) avec cache."""
    global CACHE_PANIER_DATA, CACHE_PANIER_DATE

    try:
        for loc in ['fr_FR.UTF-8', 'fr_FR', 'fra']:
            try:
                locale.setlocale(locale.LC_TIME, loc)
                break
            except: continue
    except: pass

    # Vérification du cache (si pas de date spécifique demandée)
    if not start_date:
        today = datetime.now().date()
        if CACHE_PANIER_DATA is not None and CACHE_PANIER_DATE == today:
            return CACHE_PANIER_DATA
        start_date = datetime.now().strftime("%Y-%m-%d")

    target_url = f"{config.BASE_PRODUCTS_URL}/{start_date}/14"
    
    # Utilisation du wrapper pour éviter la duplication de code
    res = _get_with_auto_login(target_url)
    if not res: return None

    try:
        soup = BeautifulSoup(res.content, 'html.parser')
        table = soup.find('table', id='table-summary')
        if not table: return None

        all_data = {}
        rows = table.find_all('tr')
        if len(rows) < 2: return None

        headers = [th.get_text(strip=True) for th in rows[0].find_all('th') if th.get_text(strip=True)]
        cells = rows[1].find_all('td')

        for i, date_label in enumerate(headers):
            if i >= len(cells): break
            products = []
            for div in cells[i].find_all('div', class_='product'):
                qty_div = div.find('div', class_='product-quantity')
                if qty_div:
                    qty = qty_div.get_text(strip=True)
                    name_node = qty_div.next_sibling
                    product_name = name_node.strip() if name_node else "Produit"
                    products.append(f"{qty} x {product_name}")
            all_data[date_label] = products
        
        # Mise à jour du cache si c'est la requête du jour
        if start_date == datetime.now().strftime("%Y-%m-%d"):
            CACHE_PANIER_DATA = all_data
            CACHE_PANIER_DATE = datetime.now().date()

        return all_data
    except Exception as e:
        print(f"💥 Erreur parsing panier : {e}")
        return None

def find_basket_for_friday(data):
    today = datetime.now()
    days_until_friday = (4 - today.weekday() + 7) % 7
    target_dt = today + timedelta(days=days_until_friday)
    day_num = target_dt.strftime("%d")
    month_name = target_dt.strftime("%B").lower()

    for key, products in data.items():
        clean_key = key.strip().lower()
        if day_num in clean_key and month_name in clean_key:
            return key, products
    return None, None

def get_open_contracts(force_refresh=False):
    """Récupère les contrats ouverts."""
    global CACHE_CONTRACTS_DATA, CACHE_CONTRACTS_DATE
    today = datetime.now().date()

    if not force_refresh and CACHE_CONTRACTS_DATA is not None and CACHE_CONTRACTS_DATE == today:
        print("📦 [CONTRATS] Utilisation du cache.")
        return CACHE_CONTRACTS_DATA

    print(f"--- 🌐 Récupération des contrats (Force: {force_refresh}) ---")
    
    # Utilisation du wrapper
    res = _get_with_auto_login(config.CONTRACTS_URL)
    if not res: return None

    try:
        soup = BeautifulSoup(res.content, 'html.parser')
        contract_links = soup.find_all('a', class_='btn-success')
        
        contracts = []
        for link in contract_links:
            import copy
            link_copy = copy.copy(link)
            small_tag = link_copy.find('small')
            deadline = small_tag.get_text(strip=True) if small_tag else ""
            if small_tag: small_tag.decompose()
            
            title = link_copy.get_text(separator=" ", strip=True)
            
            # Reconstruction d'URL propre avec la config
            raw_url = link.get('href')
            if raw_url:
                if raw_url.startswith('http'):
                    url = raw_url
                else:
                    # Gestion propre du slash
                    if raw_url.startswith('/'):
                        url = f"{config.BASE_DOMAIN}{raw_url}"
                    else:
                        url = f"{config.BASE_DOMAIN}/{raw_url}"
            else:
                url = ""
            
            contracts.append({'title': title, 'deadline': deadline, 'url': url})
            
        CACHE_CONTRACTS_DATA = contracts
        CACHE_CONTRACTS_DATE = today
        return contracts

    except Exception as e:
        print(f"💥 Erreur parsing contrats : {e}")
        return None
