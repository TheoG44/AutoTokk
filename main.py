import os
import logging
from pytubefix import YouTube
from moviepy import VideoFileClip, AudioFileClip

# Import des fonctions des autres fichiers
from decoup import decouper_video
from assembleur import assembler_videos

# ---- Setup Logging ---- #
logging.basicConfig(
    level=logging.INFO,
    filename=".log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    # ---- Paramètres ---- #
    url = "https://www.youtube.com/watch?v=YyAuFiIv-V4"
    output_folder = "VideoFinis"
    os.makedirs(output_folder, exist_ok=True)

    # ---- Téléchargement en Piste Audio & Vidéo ---- #
    logging.info("Démarrage du téléchargement...")
    yt = YouTube(url)

    # Meilleure vidéo (adaptive, sans audio)
    video_stream = yt.streams.filter(adaptive=True, file_extension="mp4", type="video").order_by("resolution").desc().first()
    video_path = video_stream.download(filename="video.mp4")  # type: ignore
    print(f"✅ Vidéo téléchargée en {video_stream.resolution}")  # type: ignore
    logging.info(f"Vidéo téléchargée en {video_stream.resolution}")  # type: ignore

    # Meilleure piste audio
    audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()
    audio_path = audio_stream.download(filename="audio.mp3")  # type: ignore
    print("✅ Audio téléchargé")
    logging.info("Audio téléchargé")

    # ---- Fusion des Pistes Audio & Vidéo ---- #
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    final_clip = video_clip.with_audio(audio_clip)

    final_path = os.path.join(output_folder, "VideoFinale1080p.mp4")
    final_clip.write_videofile(final_path, codec="libx264", audio_codec="aac")

    # ---- Nettoyage fichiers temporaires ---- #
    video_clip.close()
    audio_clip.close()
    final_clip.close()
    os.remove(video_path) # type: ignore
    os.remove(audio_path) # type: ignore
    print("✅ Fusion terminée et fichiers temporaires supprimés")
    logging.info("Fusion terminée et fichiers temporaires supprimés")

    # ---- Étape 2 : Découper la vidéo ---- #
    decouper_video(final_path, os.path.join(output_folder, "segments"))

    # ---- Étape 3 : Assembler les segments ---- #
    assembler_videos(
        os.path.join(output_folder, "segments"),
        os.path.join(output_folder, "segments"),
        os.path.join(output_folder, "VideoMonte")
    )

if __name__ == "__main__":
    main()
