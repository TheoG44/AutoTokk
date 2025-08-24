import os
from moviepy import VideoClip, VideoFileClip

# ---- Fichier vidéo à découper ---- #
input_folder = "VideoFinis"
output_folder = os.path.join(input_folder, "segment")

# Crée le dossier s'y il n'existe pas
os.makedirs(output_folder, exist_ok=True)

# Charge la vidéo
video = VideoFileClip("VideoFinale1080p.mp4")
duration = int(video.duration) # durée en seconde

# Boucle pour découper segments de 60s
segment_length = 60
for i, start in enumerate(range(0, duration, segment_length)):
  end = min(start + segment_length, duration)
  segment = video.subclipped(start, end)
  segment_filename = os.path.join(output_folder, f"segment_{i+1:03d}.mp4")
  segment.write_videofile(segment_filename, codec="libx264", audio="aac")
  segment.close()

video.close()

print(f"✅ Découpage terminé ! Segments dans : {output_folder}.")