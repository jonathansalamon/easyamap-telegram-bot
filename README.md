# 🥦 Bot Telegram AMAP - EasyAmap

Ce bot Telegram automatise la récupération d'informations depuis le site **EasyAmap**. Il notifie le groupe chaque semaine du contenu du panier et alerte lors de l'ouverture de nouveaux contrats.

**ATTENTION: Ce bot à été 100% développé par l'IA Gemini**

## ✨ Fonctionnalités

### 🤖 Commandes Telegram
* **/panier** : Affiche la composition du panier de la distribution du vendredi à venir.
* **/contrats** : Liste les contrats actuellement ouverts (boutons verts sur le site) avec leurs liens directs vers le site.
* **/chercher [mot]** : Recherche un produit spécifique (ex: `miel`, `pomme`) sur les 14 prochaines semaines de distribution.
* **/aide** : Affiche la liste des commandes disponibles.

### ⏰ Tâches Automatiques (Jobs)
* **Rappel Hebdomadaire** : Tous les **jeudis à 10h00**, le bot envoie automatiquement la liste des produits dans le canal configuré.
* **Veille des Contrats** : Tous les jours à **14h00**, le bot vérifie s'il y a de nouveaux contrats ou des mises à jour de dates limites et envoie une alerte s'il détecte un changement.

---

### 📸 Screenshots

#### Notification de prochaine distribution
<img alt="Panier" src="https://github.com/user-attachments/assets/b31ec975-9f49-4fe8-a3b8-2d4c12e14a2c" />

#### Recherche de produits
<img alt="Recherche" src="https://github.com/user-attachments/assets/08c593bf-bcf6-4961-980c-08bb258fc5e1" />

#### Détection de nouveaux contrats
<img alt="Contrats" src="https://github.com/user-attachments/assets/506cbcab-7a32-47c5-acd5-3ca0dc851324" />

---

## 📂 Architecture du Projet

Le code est structuré en quatre modules pour une maintenance facilitée :

* **`amap_service_bot.py`** : Point d'entrée principal. Il initialise le bot Telegram et gère la planification des tâches (JobQueue).
* **`config.py`** : Centralise l'URL de base (`BASE_DOMAIN`) et les variables d'environnement.
* **`amap_api.py`** : Gère la logique métier : connexion persistante, gestion du cache journalier et scraping des données (panier et contrats).
* **`bot_handlers.py`** : Contient la logique de réponse aux commandes et le formatage des messages Telegram.

---

## 🚀 Installation

### 1. Prérequis
* Python 3.8 ou supérieur.
* Un Bot Telegram créé via [@BotFather](https://t.me/botfather).

### 2. Récupération des fichiers
Placez les fichiers `amap_service_bot.py`, `config.py`, `amap_api.py` et `bot_handlers.py` dans un dossier dédié.

### 3. Installation des dépendances
Il est fortement recommandé d'utiliser un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```
Installez les bibliothèques requises :
```bash
pip install python-telegram-bot[job-queue] requests beautifulsoup4
```
### 4. Lancement
Assurez-vous que les variables d'environnement sont définies (voir section suivante), puis lancez :
```bash
python amap_service_bot.py
```

---

## ⚙️ Configuration

Le bot utilise les variables d'environnement suivantes, à configurer sur votre serveur :

| Variable | Description |
| :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | Token API fourni par @BotFather. |
| `TELEGRAM_CHAT_ID` | Identifiant du groupe ou canal de destination. |
| `TELEGRAM_TOPIC_ID` | ID du "Sujet" (Topic) dans lequel le bot doit poster. |
| `AMAP_USERNAME` | Identifiant de connexion au site EasyAmap. |
| `AMAP_PASSWORD` | Mot de passe associé au compte. |

---

## 🧠 Optimisations Techniques

* **Cache Journalier** : Pour limiter les requêtes vers le site EasyAmap, le bot stocke les données du panier et des contrats en mémoire. Elles ne sont rafraîchies qu'une fois par jour.
* **Session Persistante** : Le bot conserve ses cookies et ses jetons CSRF pour éviter de se reconnecter à chaque commande, ce qui accélère le temps de réponse.

---

## 📝 Logs

Le bot journalise son activité dans la console :
* **`📝 [LOG]`** : Détail des commandes reçues.
* **`⏰ [JOB]`** : Suivi de l'exécution des tâches planifiées.
* **`🔄 / ✅ / ❌`** : État des tentatives de connexion et de récupération.
