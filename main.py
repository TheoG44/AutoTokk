import os
import logging
import shutil
import subprocess
from pytubefix import YouTube
from concurrent.futures import ProcessPoolExecutor
import sys
import random

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
# 🎥 Fonction pour assembler une paire de vidéos
# --------------------------------------
def assembler_pair(top, bottom, output):
    logging.info(f"🎞️ [ASSEMBLAGE] Empilement vertical : {top} + {bottom} -> {output}")

    cmd = [
        "ffmpeg", "-y", "-i", top, "-i", bottom,
        "-filter_complex", "[0:v][1:v]vstack=inputs=2",
        "-c:v", "libx264", "-preset", "ultrafast",
        "-crf", "23",
        output
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    logging.info(f"✅ Assemblage créé : {output}")


# --------------------------------------
# 🎬 Assemblage rapide vertical avec FFmpeg
# --------------------------------------
def assembler_videos_ffmpeg(folder_path1: str, output_folder: str):
    logging.info(f"📂 [ASSEMBLAGE MULTIPLE] Début assemblage des segments dans {output_folder}")

    os.makedirs(output_folder, exist_ok=True)

    # Liste des segments à superposer
    videos1 = sorted([os.path.join(folder_path1, f) for f in os.listdir(folder_path1) if f.endswith(".mp4")])

    # Liste des vidéos dans Videos2
    videos2_all = [os.path.join("Videos2", f) for f in os.listdir("Videos2") if f.endswith(".mp4")]

    logging.info(f"📊 {len(videos1)} segments trouvés dans {folder_path1}")
    logging.info(f"📊 {len(videos2_all)} vidéos disponibles dans Videos2")

    with ProcessPoolExecutor() as executor:
        futures = []
        for i, top in enumerate(videos1):
            # Choisir aléatoirement une vidéo dans Videos2
            bottom = random.choice(videos2_all)
            output_file = os.path.join(output_folder, f'AutoTok_video_{i+1:03d}.mp4')
            logging.info(f"🔗 Assemblage segment {i+1}: {top} + {bottom}")
            futures.append(executor.submit(assembler_pair, top, bottom, output_file))

        # Attendre que tous les assemblages soient terminés
        for f in futures:
            f.result()

    logging.info(f"🧹 Nettoyage du dossier intermédiaire : {folder_path1}")
    shutil.rmtree(folder_path1, ignore_errors=True)

    logging.info(f"✅ Assemblage terminé, vidéos sauvegardées dans {output_folder}")



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
    segments_folder = os.path.join("VideoFinis", "segments")
    logging.info("✂️ Début de la découpe en segments")
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(decouper_video_fast, f, segments_folder) for f in video_files]
        for future in futures:
            future.result()

    # 🎞️ Assembler les segments
    montage_folder = os.path.join("VideoFinis", "VideoMonte")
    assembler_videos_ffmpeg(segments_folder, montage_folder)  
    
    # 📂 Récupération des fichiers finaux
    all_videos = sorted([
        os.path.join(montage_folder, f)
        for f in os.listdir(montage_folder)
        if f.endswith(".mp4")
    ])

    logging.info(f"📦 Pipeline terminé, {len(all_videos)} vidéos générées dans {montage_folder}")
    return all_videos


# --------------------------------------
# ▶️ Lancer le programme
# --------------------------------------
if __name__ == "__main__":
    urls = "https://www.youtube.com/watch?v=PsUDbM5O8sU"
    logging.info("▶️ Exécution directe de main2.py")
    main(urls)
