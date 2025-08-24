import os
from moviepy import VideoFileClip

# ---- Fichier vidéo à découper ---- #
input_folder = "VideoFinis"
output_folder = os.path.join(input_folder, "segments")

# Crée le dossier s'il n'existe pas
os.makedirs(output_folder, exist_ok=True)

# Charge la vidéo
video_path = os.path.join(input_folder, "VideoFinale1080p.mp4")
video = VideoFileClip(video_path)
duration = int(video.duration)  # durée en secondes

# Boucle pour découper segments de 60s
segment_length = 60
for i, start in enumerate(range(0, duration, segment_length)):
    end = min(start + segment_length, duration)
    segment = video.subclipped(start, end)
    segment_filename = os.path.join(output_folder, f"segment_{i+1:03d}.mp4")
    segment.write_videofile(segment_filename, codec="libx264", audio_codec="aac")
    segment.close()

video.close()
print(f"✅ Découpage terminé ! Segments dans : {output_folder}")
