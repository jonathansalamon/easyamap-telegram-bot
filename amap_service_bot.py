from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from datetime import datetime
import config
import bot_handlers

if __name__ == '__main__':
    print("🚀 Démarrage du service Bot AMAP")
    
    if not config.TOKEN:
        print("❌ ERREUR : TELEGRAM_BOT_TOKEN manquant !")
    else:
        application = ApplicationBuilder().token(config.TOKEN).build()
        
        # Ajout des Handlers
        application.add_handler(CommandHandler("start", bot_handlers.help_command))
        application.add_handler(CommandHandler("aide", bot_handlers.help_command))
        application.add_handler(CommandHandler("panier", bot_handlers.panier_command))
        application.add_handler(CommandHandler("contrats", bot_handlers.contrats_command))
        application.add_handler(CommandHandler("chercher", bot_handlers.chercher_command))
        # Heartbeat toutes les 60 secondes
        application.job_queue.run_repeating(bot_handlers.heartbeat_job, interval=60, first=10)
        # Gestion d'erreurs
        application.add_error_handler(bot_handlers.error_handler)
        
        # Configuration des Jobs
        if application.job_queue:
            # 1. Rappel Panier : Jeudi à 10h00
            application.job_queue.run_daily(
                bot_handlers.weekly_reminder, 
                time=datetime.strptime("10:00", "%H:%M").time(), 
                days=(3,)
            )
            # 2. Vérif Contrats : Tous les jours à 14h00
            application.job_queue.run_daily(
                bot_handlers.daily_contracts_check,
                time=datetime.strptime("14:00", "%H:%M").time()
            )

        print("🚀 Bot opérationnel.")
        application.run_polling()
