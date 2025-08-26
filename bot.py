# ===============================
# 📌 BOT TELEGRAM : Téléchargement & Compression de vidéos YouTube
# ===============================

import os
import logging
import asyncio
import shutil
import subprocess
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from telegram import Update
from main import main  # <-- On importe la fonction principale de main2.py

# ===============================
# 🎬 Fonction : Compression d'une vidéo avec FFmpeg
# ===============================
def compresser_video(input_file, output_file):
    """
    Compresse une vidéo pour réduire sa taille avant envoi sur Telegram.
    - Redimensionne en largeur max 720px (hauteur auto)
    - Bitrate vidéo limité à 1 Mbps
    - Audio converti en AAC 128 kbps
    """
    logging.info(f"📉 Compression de la vidéo : {input_file} -> {output_file}")

    cmd = [
    "ffmpeg", "-y", "-i", input_file,
    "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2",
    "-b:v", "1M",
    "-c:a", "aac", "-b:a", "128k",
    output_file
]


    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True)
        logging.info(f"✅ Compression réussie : {output_file}")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ Erreur lors de la compression : {e}")

    return output_file


# ===============================
# 🔑 Chargement du Token Telegram
# ===============================
load_dotenv()  
token = os.getenv('TOKEN')  # Récupération du TOKEN dans le fichier .env
logging.info("🔑 Token Telegram chargé avec succès")


# ===============================
# 📝 Configuration du Logging
# ===============================
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.INFO,
    filename=".log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding='utf-8'
)


# ===============================
# 🚀 Commande : /start
# ===============================
async def start(update, context):
    """Message d'accueil quand un utilisateur lance /start"""
    logging.info(f"👋 Commande /start reçue de {update.effective_user.username}")
    await update.message.reply_text(
        "👋 Bienvenue sur le bot Modu !\n"
        "👉 Pour télécharger une vidéo YouTube : /youtube <lien>"
    )


# ===============================
# 🎥 Commande : /youtube
# ===============================
async def youtube(update, context):
    """
    Commande principale :
    - Mode test : envoie des vidéos déjà présentes
    - Mode normal : télécharge et monte la vidéo YouTube
    - Compresse la vidéo avant envoi
    """
    logging.info(f"🎥 Commande /youtube reçue de {update.effective_user.username} avec args: {context.args}")

    if len(context.args) == 0:
        await update.message.reply_text("❌ Veuillez fournir un lien YouTube ou 'test'.")
        logging.warning("⚠️ Aucun argument fourni pour /youtube")
        return

    arg = context.args[0]

    # ------------------- 🧪 MODE TEST ------------------- #
    if arg.lower() == "test":
        logging.info(f"[TEST MODE] Envoi de vidéos locales à {update.effective_user.username}")
        input_folder = "VideoFinis/VideoMonte"

        if not os.path.exists(input_folder):
            await update.message.reply_text("⚠️ Aucun dossier trouvé.")
            logging.warning(f"📂 Dossier introuvable : {input_folder}")
            return

        # Liste toutes les vidéos du dossier
        video_paths = [
            os.path.join(input_folder, f)
            for f in sorted(os.listdir(input_folder))
            if f.endswith(".mp4")
        ]
        logging.info(f"📂 {len(video_paths)} vidéos trouvées en mode test")
        await update.message.reply_text(f"⏳ Mode test : {len(video_paths)} vidéos prêtes.")

    # ------------------- 🎬 MODE NORMAL ------------------- #
    else:
        url = arg
        logging.info(f"🔗 Téléchargement demandé pour URL : {url}")
        await update.message.reply_text("⏳ Téléchargement et montage en cours...")

        try:
            # On lance la fonction main() dans un thread séparé pour ne pas bloquer le bot
            video_paths = await asyncio.to_thread(main, url)
            logging.info(f"📥 Téléchargement terminé, {len(video_paths) if video_paths else 0} vidéo(s) générée(s)")
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'appel à main() : {e}")
            await update.message.reply_text("⚠️ Erreur lors du téléchargement.")
            return


    # ===============================
    # 📤 Envoi des vidéos à l'utilisateur
    # ===============================
    try:
        if not video_paths:
            await update.message.reply_text("⚠️ Aucune vidéo n'a été trouvée.")
            logging.warning("⚠️ Liste de vidéos vide")
            return

        for final_path in video_paths:
            logging.info(f"📂 Traitement du fichier : {final_path}")

            if os.path.exists(final_path):
                # 🔽 Compression avant envoi
                compressed_path = final_path.replace(".mp4", "_compressed.mp4")
                compresser_video(final_path, compressed_path)

                # 📩 Envoi sur Telegram
                try:
                    with open(compressed_path, "rb") as video_file:
                        await update.message.reply_document(document=video_file)

                    logging.info(f"✅ Vidéo envoyée avec succès : {compressed_path}")

                    # 🗑️ Suppression après envoi
                    os.remove(final_path)
                    os.remove(compressed_path)

                except Exception as e:
                    logging.error(f"❌ Erreur lors de l'envoi Telegram : {e}")

            else:
                logging.error(f"❌ Fichier introuvable : {final_path}")

        # ✅ Fin de l’envoi + Nettoyage global
        await update.message.reply_text("✅ Envoi terminé !")
        logging.info("📤 Envoi terminé avec succès")

        # 🧹 Nettoyage global des dossiers temporaires
        try:
            shutil.rmtree("VideoFinis/segments", ignore_errors=True)
            shutil.rmtree("VideoFinis/VideoMonte", ignore_errors=True)

            # Suppression de la vidéo finale si elle existe
            if os.path.exists("VideoFinis/VideoFinale1080p.mp4"):
                os.remove("VideoFinis/VideoFinale1080p.mp4")

            # 🔎 Suppression des vidéos temporaires AutoTok
            for f in os.listdir("."):
                if f.startswith("AutoTok") and f.endswith(".mp4"):
                    os.remove(f)
                    logging.info(f"🗑️ Fichier temporaire supprimé : {f}")

            logging.info("🧹 Nettoyage effectué après envoi")
        except Exception as e:
            logging.error(f"❌ Erreur lors du nettoyage final : {e}")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Une erreur est survenue : {e}")
        logging.exception("❌ Exception lors de l'envoi des vidéos")


# ===============================
# ▶️ Lancement du Bot
# ===============================
if __name__ == "__main__":
    logging.info("🚀 Démarrage du bot...")
    try:
        # On construit l'application Telegram
        app = Application.builder().token(token).read_timeout(300).write_timeout(300).build()  # type: ignore

        # Ajout des commandes disponibles
        app.add_handler(CommandHandler('start', start))
        app.add_handler(CommandHandler('youtube', youtube))

        print("✅ Lancement du bot...")
        app.run_polling(poll_interval=5)
    except Exception as e:
        logging.exception(f"❌ Erreur critique au démarrage du bot : {e}")
