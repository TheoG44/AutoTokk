import os
from moviepy import VideoFileClip

def decouper_video(input_path: str, output_folder: str, segment_length: int = 60):
    """
    Découpe une vidéo en segments de durée fixe.

    Args:
        input_path (str): Chemin vers la vidéo d'entrée.
        output_folder (str): Dossier où sauvegarder les segments.
        segment_length (int): Longueur de chaque segment en secondes (par défaut 60).
    """
    os.makedirs(output_folder, exist_ok=True)

    # On récupère la durée totale de la vidéo
    with VideoFileClip(input_path) as video:
        duration = int(video.duration)

    # Boucle pour découper la vidéo en morceaux
    for i, start in enumerate(range(0, duration, segment_length)):
        end = min(start + segment_length, duration)

        # Recharge la vidéo à chaque itération pour éviter bugs de MoviePy
        with VideoFileClip(input_path) as video:
            segment = video.subclipped(start, end)
            segment_filename = os.path.join(output_folder, f"segment_{i+1:03d}.mp4")
            segment.write_videofile(
                segment_filename,
                codec="libx264",
                audio_codec="aac",
                threads=4
            )
            segment.close()

    print(f"✅ Découpage terminé ! Segments dans : {output_folder}")
