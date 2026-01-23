import re
from telegram import Update
from telegram.ext import ContextTypes
import config
import amap_api

# --- UTILITAIRES ---
def log_command(update: Update):
    user = update.effective_user
    msg = update.message.text if update.message else "System"
    print(f"📝 [LOG] Commande de {user.first_name} : {msg}")

async def send_formatted_basket(bot, target_chat_id, target_topic_id):
    """Fonction utilitaire pour envoyer le panier."""
    data = amap_api.get_amap_data()
    if not data: return False
    
    date_label, prods = amap_api.find_basket_for_friday(data)
    if prods:
        msg = f"Voici les produits à récupérer pour la distribution du *{date_label}* :\n\n" + "\n".join([f"• {p}" for p in prods])
        await bot.send_message(
            chat_id=target_chat_id, 
            message_thread_id=int(target_topic_id) if target_topic_id else None, 
            text=msg, 
            parse_mode='Markdown'
        )
        return True
    return False

# --- COMMANDES ---

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update)
    help_text = (
        "🤖 *Bot AMAP*\n\n"
        "🔹 /panier : Affiche les produits à récupérer ce vendredi.\n"
        "🔹 /contrats : Liste les Contrats ouverts.\n"
        "🔹 /chercher [mot] : Cherche quand un produit sera distribué.\n"
        "🔹 /aide : Affiche l'aide."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def panier_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update)
    current_chat = update.effective_chat.id
    current_topic = update.effective_message.message_thread_id
    await update.message.reply_text("🔄 Récupération du panier...")
    success = await send_formatted_basket(context.bot, current_chat, current_topic)
    if not success: await update.message.reply_text("ℹ️ Aucun panier trouvé.")

async def contrats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update)
    await update.message.reply_text("📂 Chargement des contrats...")
    
    # Utilise le cache via l'API
    contracts = amap_api.get_open_contracts(force_refresh=False)
    
    if not contracts:
        await update.message.reply_text("ℹ️ Aucun contrat ouvert.")
        return

    msg = "📝 *Contrats ouverts* :\n\n"
    for c in contracts:
        msg += f"🔹 *{c['title']}*\n   _{c['deadline']}_\n   [Lien]({c['url']})\n\n"
    
    await update.message.reply_text(msg, parse_mode='Markdown', disable_web_page_preview=True)

async def chercher_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_command(update)
    if not context.args:
        await update.message.reply_text("ℹ️ Ex: `/chercher miel`", parse_mode='Markdown')
        return
    query = " ".join(context.args).strip()
    
    data = amap_api.get_amap_data()
    if data is None: return

    results = []
    regex = re.compile(re.escape(query), re.IGNORECASE)
    for date, prods in data.items():
        matches = [p for p in prods if regex.search(p)]
        if matches:
            results.append(f"📅 *{date}*\n" + "\n".join([f"  └ {m}" for m in matches]))

    if results:
        await update.message.reply_text("✅ Trouvé :\n\n" + "\n\n".join(results), parse_mode='Markdown')
    else:
        await update.message.reply_text(f"🤷‍♂️ Pas de '{query}' trouvé.")

# --- TASKS (JOBS) ---

async def weekly_reminder(context: ContextTypes.DEFAULT_TYPE):
    print("⏰ [JOB] Rappel Panier Jeudi 10h.")
    await send_formatted_basket(context.bot, config.CHAT_ID, config.TOPIC_ID)

async def daily_contracts_check(context: ContextTypes.DEFAULT_TYPE):
    print("⏰ [JOB] Vérification quotidienne des contrats (14h)...")
    
    # 1. Sauvegarde l'ancien état (cache actuel)
    old_contracts = amap_api.CACHE_CONTRACTS_DATA
    
    # 2. Force le rafraîchissement
    new_contracts = amap_api.get_open_contracts(force_refresh=True)
    
    if new_contracts is None:
        print("❌ Echec récupération contrats lors du job.")
        return

    if old_contracts is None:
        print("ℹ️ Premier remplissage du cache contrats (pas de notif).")
        return

    # 3. Comparaison
    old_dict = {c['url']: c for c in old_contracts}
    notifications = []
    
    for c in new_contracts:
        url = c['url']
        if url not in old_dict:
            notifications.append(c) # Nouveau contrat
        elif old_dict[url]['title'] != c['title'] or old_dict[url]['deadline'] != c['deadline']:
            print(f"♻️ Mise à jour détectée sur : {c['title']}")
            notifications.append(c) # Mise à jour
            
    if notifications:
        print(f"✨ {len(notifications)} nouveautés à notifier !")
        for c in notifications:
            msg = (
                f"🆕 *Nouveau contrat (ou mise à jour) !*\n\n"
                f"📜 *{c['title']}*\n"
                f"⏳ _{c['deadline']}_\n"
                f"👉 [Voir le contrat]({c['url']})"
            )
            await context.bot.send_message(
                chat_id=config.CHAT_ID,
                message_thread_id=int(config.TOPIC_ID) if config.TOPIC_ID else None,
                text=msg,
                parse_mode='Markdown'
            )
    else:
        print("✅ Aucune nouveauté dans les contrats.")
