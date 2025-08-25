import os
import logging
import shutil
import subprocess
from pytubefix import YouTube
from concurrent.futures import ProcessPoolExecutor
import sys

# ---- Setup Logging ---- #
logging.basicConfig(
    level=logging.INFO,
    filename=".log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding='utf-8'
)

# --------------------------------------
# Découpe rapide d'une vidéo en segments
# --------------------------------------
def decouper_video_fast(input_file, output_folder, segment_length=60):
    os.makedirs(output_folder, exist_ok=True)

    # Récupérer la durée totale
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", input_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    duration = int(float(result.stdout))

    for i, start in enumerate(range(0, duration, segment_length)):
        end = min(start + segment_length, duration)
        output_file = os.path.join(output_folder, f"{os.path.basename(input_file)}_seg_{i+1:03d}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-ss", str(start), "-to", str(end),
            "-i", input_file, "-c", "copy", output_file
        ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        logging.info(f"✅ Segment {i+1} sauvegardé : {output_file}")
    return output_folder

# --------------------------------------
# Fonction globale pour assembler une paire de vidéos
# --------------------------------------
def assembler_pair(top, bottom, output):
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
# Assemblage rapide vertical avec FFmpeg
# --------------------------------------
def assembler_videos_ffmpeg(folder_path1: str, folder_path2: str, output_folder: str):
    os.makedirs(output_folder, exist_ok=True)

    videos1 = sorted([os.path.join(folder_path1, f) for f in os.listdir(folder_path1) if f.endswith(".mp4")])
    videos2 = sorted([os.path.join(folder_path2, f) for f in os.listdir(folder_path2) if f.endswith(".mp4")])

    with ProcessPoolExecutor() as executor:
        futures = []
        for i, (top, bottom) in enumerate(zip(videos1, videos2)):
            output_file = os.path.join(output_folder, f'AutoTok_video_{i+1:03d}.mp4')
            futures.append(executor.submit(assembler_pair, top, bottom, output_file))
        for f in futures:
            f.result()

    # Nettoyage dossiers intermédiaires
    shutil.rmtree(folder_path1, ignore_errors=True)

# --------------------------------------
# Téléchargement et fusion rapide
# --------------------------------------
def download_and_merge(url, output_folder="VideoFinis"):
    os.makedirs(output_folder, exist_ok=True)

    yt = YouTube(url)
    video_stream = yt.streams.filter(adaptive=True, file_extension="mp4", type="video").order_by("resolution").desc().first()
    audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()

    video_path = video_stream.download(filename="video.mp4")
    audio_path = audio_stream.download(filename="audio.mp3")

    final_path = os.path.join(output_folder, "VideoFinale1080p.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
        "-c", "copy", final_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

    os.remove(video_path)
    os.remove(audio_path)
    logging.info(f"✅ Vidéo fusionnée et sauvegardée : {final_path}")
    return final_path

# --------------------------------------
# Fonction principale
# --------------------------------------
def main(urls):
    if not shutil.which("ffmpeg"):
        sys.exit(
            "❌ FFmpeg n'est pas installé ou introuvable dans le PATH.\n"
            "Téléchargez-le ici : https://www.gyan.dev/ffmpeg/builds/\n"
            "Assurez-vous que le dossier 'bin' contenant ffmpeg.exe est ajouté au PATH."
        )

    print("✅ FFmpeg trouvé ! On peut continuer…")
        
    if isinstance(urls, str):
        urls = [urls]

    # Téléchargement et fusion des vidéos
    video_files = [download_and_merge(url) for url in urls]

    # Découper toutes les vidéos en parallèle
    segments_folder = os.path.join("VideoFinis", "segments")
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(decouper_video_fast, f, segments_folder) for f in video_files]
        for future in futures:
            future.result()

    # Assembler les segments avec FFmpeg (rapide)
    montage_folder = os.path.join("VideoFinis", "VideoMonte")
    assembler_videos_ffmpeg(segments_folder, segments_folder, montage_folder)

    # Retourner la liste des fichiers finaux
    all_videos = sorted([
        os.path.join(montage_folder, f)
        for f in os.listdir(montage_folder)
        if f.endswith(".mp4")
    ])
    return all_videos

# --------------------------------------
# Lancer le programme
# --------------------------------------
if __name__ == "__main__":
    urls = "https://www.youtube.com/watch?v=PsUDbM5O8sU"
    main(urls)
