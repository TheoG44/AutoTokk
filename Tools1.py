import os
import logging
import shutil
import subprocess
from pytubefix import YouTube
from concurrent.futures import ProcessPoolExecutor
import sys
import random

#============================================================================
#
#
#         Télécharger des Vidéos d'arrière Plan
#
#
#============================================================================


# ===============================
# 📝 Setup Logging
# ===============================
logging.basicConfig(
    level=logging.INFO,
    filename=".log",
    filemode="a",  # append pour conserver les logs
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding='utf-8'
)

# --------------------------------------
# 🎬 Découpe rapide d'une vidéo en segments
# --------------------------------------
def decouper_video_fast(input_file, output_folder, segment_length=60):
    logging.info(f"📂 [DECOUPE] Début de la découpe de {input_file} en segments de {segment_length}s")

    os.makedirs(output_folder, exist_ok=True)

    # Récupérer la durée totale
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration","-of", "default=noprint_wrappers=1:nokey=1", input_file],stdout=subprocess.PIPE,stderr=subprocess.STDOUT
    )
    duration = int(float(result.stdout))
    logging.info(f"⏱️ Durée détectée : {duration} secondes pour {input_file}")

    for i, start in enumerate(range(0, duration, segment_length)):
        end = min(start + segment_length, duration)
        output_file = os.path.join(output_folder, f"{os.path.basename(input_file)}_seg_{i+1:03d}.mp4")

        subprocess.run([
            "ffmpeg", "-y", "-ss", str(start), "-to", str(end),
            "-i", input_file, "-c", "copy", output_file
        ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        logging.info(f"✅ Segment {i+1} sauvegardé : {output_file}")

    logging.info(f"📦 Découpe terminée pour {input_file}, segments enregistrés dans {output_folder}")
    return output_folder



# --------------------------------------
# 📥 Téléchargement et fusion rapide
# --------------------------------------
def download_and_merge(url, output_folder="VideoFinis"):
    logging.info(f"🌐 [DOWNLOAD] Téléchargement de la vidéo : {url}")

    os.makedirs(output_folder, exist_ok=True)

    yt = YouTube(url)
    logging.info(f"🎬 Titre de la vidéo : {yt.title}")

    video_stream = yt.streams.filter(adaptive=True, file_extension="mp4", type="video").order_by("resolution").desc().first()
    audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()

    logging.info("📥 Téléchargement de la vidéo et de l'audio séparément...")
    video_path = video_stream.download(filename="video.mp4")  # type: ignore
    audio_path = audio_stream.download(filename="audio.mp3")  # type: ignore

    final_path = os.path.join(output_folder, "VideoFinale1080p.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path, "-i", audio_path, "-c", "copy", final_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)  # type: ignore

    os.remove(video_path)  # type: ignore
    os.remove(audio_path)  # type: ignore

    logging.info(f"✅ Vidéo fusionnée et sauvegardée : {final_path}")
    return final_path


# --------------------------------------
# 🚀 Fonction principale
# --------------------------------------
def main(urls):
    logging.info("🚀 [MAIN] Lancement du pipeline vidéo")

    if not shutil.which("ffmpeg"):
        logging.error("❌ FFmpeg introuvable dans le PATH")
        sys.exit(
            "❌ FFmpeg n'est pas installé ou introuvable dans le PATH.\n"
            "Téléchargez-le ici : https://www.gyan.dev/ffmpeg/builds/\n"
            "Assurez-vous que le dossier 'bin' contenant ffmpeg.exe est ajouté au PATH."
        )

    print("✅ FFmpeg trouvé ! On peut continuer…")
    logging.info("✅ FFmpeg trouvé dans le PATH")

    if isinstance(urls, str):
        urls = [urls]

    # 📥 Téléchargement et fusion des vidéos
    video_files = [download_and_merge(url) for url in urls]

    # ✂️ Découper toutes les vidéos en parallèle
    segments_folder = os.path.join("Videos2")
    logging.info("✂️ Début de la découpe en segments")
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(decouper_video_fast, f, segments_folder) for f in video_files]
        for future in futures:
            future.result()

# --------------------------------------
# ▶️ Lancer le programme
# --------------------------------------
if __name__ == "__main__":
    urls = "https://www.youtube.com/watch?v=XBIaqOm0RKQ"
    main(urls)