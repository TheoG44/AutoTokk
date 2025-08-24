import os 
from pytubefix import YouTube
from moviepy import VideoFileClip, AudioFileClip

# URL de la vidéo
url = "https://www.youtube.com/watch?v=aAdfoRu6ysY"
yt = YouTube(url)

# ---- Création Dossier ---- #
output_folder = "VideoFinis"
os.makedirs(output_folder, exist_ok=True) # Crée le dossier si n'existe pas

# ---- Téléchargement en Piste Audio & Video ---- #

# Meilleure vidéo (adaptive, sans audio)
video_stream = yt.streams.filter(adaptive=True, file_extension="mp4", type="video").order_by("resolution").desc().first()
video_path = video_stream.download(filename="video.mp4") # type: ignore
print(f"✅ Vidéo téléchargée en {video_stream.resolution}") # type: ignore

# Meilleure piste audio
audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()
audio_path = audio_stream.download(filename="audio.mp3") # type: ignore
print("✅ Audio téléchargé")

# ---- Fusion des Piste Audio & Video ---- #

# Charge video_clip & audio-clip 
video_clip = VideoFileClip(video_path)
audio_clip = AudioFileClip(audio_path)

# Fusion video clip avec audio clip
final_clip = video_clip.with_audio(audio_clip)

# ---- Placer Video dans le dossier ---- #

final_path = os.path.join(output_folder, "VideoFinale1080p.mp4")

# Crée la video final
final_clip.write_videofile(final_path, codec="libx264", audio_codec="aac")

# ---- Supprime Fichiers Temp ---- #
video_clip.close()
audio_clip.close()
final_clip.close()

os.remove(video_path) # Sup video.mp4 # type: ignore
os.remove(audio_path) # Su audio.mp3 # type: ignore

print("✅ Fusion terminée ! Fichier final_1080p.mp4 créé.")
print("✅ Supression des fichiers temporaires terminée !")
