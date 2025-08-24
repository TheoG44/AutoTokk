import os
from moviepy import VideoFileClip

# ---- Création de dossier --- #
input_folder = "VideoFinis"
output_folder = os.path.join(input_folder, "segments")
os.makedirs(output_folder, exist_ok=True)

# Nom du fichier a découper
video_path = os.path.join(input_folder, "VideoFinale1080p.mp4")

segment_length = 60  # secondes

# On récup vidéo pour avoir durée totale
with VideoFileClip(video_path) as video:
    duration = int(video.duration)

# Boucle pour decouper la vidéo en morceauw
for i, start in enumerate(range(0, duration, segment_length)):
    end = min(start + segment_length, duration)
    
    # On recharge la vidéo à chaque itération 
    with VideoFileClip(video_path) as video:
        segment = video.subclipped(start, end)
        segment_filename = os.path.join(output_folder, f"segment_{i+1:03d}.mp4") # nom du segments en sortie
        segment.write_videofile(
            segment_filename,
            codec="libx264",
            audio_codec="aac",
            threads=4
        )
        segment.close()

print(f"✅ Découpage terminé ! Segments dans : {output_folder}")