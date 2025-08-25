import os
import logging
from moviepy import VideoFileClip, CompositeVideoClip
import shutil

# ---- Setup Logging ---- #
logging.basicConfig(
    level=logging.INFO,
    filename=".log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def assembler_videos(folder_path1: str, folder_path2: str, output_folder: str):
    """
    Assemble les vidéos de deux dossiers en une seule vidéo (clip1 au-dessus de clip2).

    Args:
        folder_path1 (str): Chemin du premier dossier contenant les vidéos.
        folder_path2 (str): Chemin du deuxième dossier contenant les vidéos.
        output_folder (str): Dossier où sauvegarder les vidéos assemblées.
    """
    os.makedirs(output_folder, exist_ok=True)

    # Vérifier si les dossiers existent
    if not os.path.exists(folder_path1):
        logging.error(f"Le dossier {folder_path1} n'existe pas.")
        raise FileNotFoundError(f"Le dossier {folder_path1} n'existe pas.")
    if not os.path.exists(folder_path2):
        logging.error(f"Le dossier {folder_path2} n'existe pas.")
        raise FileNotFoundError(f"Le dossier {folder_path2} n'existe pas.")

    # Récupérer les fichiers vidéos
    videos1 = sorted([os.path.join(folder_path1, f) for f in os.listdir(folder_path1) if f.endswith(('.mp4', '.mov', '.avi'))])
    videos2 = sorted([os.path.join(folder_path2, f) for f in os.listdir(folder_path2) if f.endswith(('.mp4', '.mov', '.avi'))])

    # Vérifier que les deux dossiers ont le même nombre de vidéos
    if len(videos1) != len(videos2):
        raise ValueError("Les dossiers ne contiennent pas le même nombre de vidéos.")

    for i in range(len(videos1)):
        # Charger les vidéos
        clip1 = VideoFileClip(videos1[i])
        clip2 = VideoFileClip(videos2[i])

        # Redimensionner à la même largeur
        width = max(clip1.w, clip2.w)
        clip1 = clip1.resized(width=width)
        clip2 = clip2.resized(width=width)

        # Déterminer la hauteur totale
        height = clip1.h + clip2.h # type: ignore

        # Créer une vidéo composite
        final_clip = CompositeVideoClip([
            clip1.with_position(("center", "top")), # type: ignore
            clip2.with_position(("center", "bottom")) # type: ignore
        ], size=(width, height))

        # Sauvegarder la vidéo assemblée
        output_path = os.path.join(output_folder, f'AutoTok_video_0{i+1}.mp4')
        final_clip.write_videofile(output_path, codec='libx264')

        # Libérer mémoire
        clip1.close()
        clip2.close()
        final_clip.close()

    print("✅ Les vidéos ont été assemblées avec succès.")
    logging.info("Les vidéos ont été assemblées avec succès.")
    
    # ---- Nettoyage des fichiers intermédiaires ---- #
    try:
        # Supprimer le fichier vidéo finale avant découpage
        video_finale = os.path.join("VideoFinis", "VideoFinale1080p.mp4")
        if os.path.exists(video_finale):
            os.remove(video_finale)
            print("🗑️ VideoFinale1080p.mp4 supprimée.")

        # Supprimer tout le dossier segments
        if os.path.exists(folder_path1):
            shutil.rmtree(folder_path1)
            print("🗑️ Segments supprimés.")

    except Exception as e:
        logging.error(f"Erreur lors du nettoyage : {e}")
        print(f"⚠️ Erreur lors du nettoyage : {e}")