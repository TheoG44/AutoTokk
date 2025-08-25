import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from telegram import Update
import logging

from main import main

load_dotenv() # Charge le fichier .env pour que ton token soit dispo
token = os.getenv('TOKEN') # Charge le Token du Bot dans la var token


# Ne logge pas les requêtes HTTP du bot
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# ---- Setup Logging ---- #
logging.basicConfig(
    level=logging.INFO,
    filename=".log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding='utf-8'
)

# ---- /start ---- #
async def start(update, context):
    await update.message.reply_text(
        "Bienvenue sur le bot Modu !\n"
        "Pour télécharger une vidéo YouTube : /youtube <lien>"
    )

# ---- /youtube ---- #
async def youtube(update, context):
    if len(context.args) == 0:  # Si pas d'arguments
        await update.message.reply_text("❌ Veuillez fournir un lien YouTube ou 'test'.")
        return

    arg = context.args[0]

    # ------------------- MODE TEST ------------------- #
    if arg.lower() == "test":
        logging.info(f"[TEST MODE] Envoi de vidéos déjà présentes à {update.effective_user.username}")

        input_folder = "VideoFinis/VideoMonte"
        if not os.path.exists(input_folder):
            await update.message.reply_text("⚠️ Aucun dossier 'VideoFinis/segments' trouvé.")
            return

        # On récupère toutes les vidéos déjà prêtes
        video_paths = [
            os.path.join(input_folder, f)
            for f in sorted(os.listdir(input_folder))
            if f.endswith(".mp4")
        ]

        if not video_paths:
            await update.message.reply_text("⚠️ Aucune vidéo trouvée dans 'VideoFinis/segments'.")
            return

        await update.message.reply_text(f"⏳ Mode test : {len(video_paths)} vidéos trouvées, envoi en cours...")

    # ------------------- MODE NORMAL ------------------- #
    else:
        url = arg
        logging.info(f"Nouvelle requête /youtube de {update.effective_user.username} pour l'URL : {url}")
        await update.message.reply_text("⏳ Téléchargement et montage de la vidéo en cours...")
        video_paths = main(url)  # ta fonction qui télécharge + découpe

    try:
        if not video_paths:
            await update.message.reply_text("⚠️ Aucune vidéo n'a été trouvée.")
            return

        for final_path in video_paths:
            if os.path.exists(final_path):
                with open(final_path, "rb") as video_file:
                    await update.message.reply_document(document=video_file)
                logging.info(f"Vidéo envoyée avec succès à {update.effective_user.username}")
            else:
                logging.error(f"❌ Fichier introuvable : {final_path}")

        await update.message.reply_text("✅ Envoi terminé !")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Une erreur est survenue : {e}")
        logging.exception(e)


#################################    
#       Démarrage du Bot        #
################################# 

if __name__ == "__main__":
    app = Application.builder().token(token).read_timeout(300).write_timeout(300).build()  # type: ignore
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('youtube', youtube))
    app.run_polling(poll_interval=5)
    print("Lancement du bot...")