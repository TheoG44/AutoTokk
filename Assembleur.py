import os
from moviepy import *  # type: ignore

# Dossiers contenant les vidéos

folder_path1 = "VideoFinis/segments"
folder_path2 = "VideoFinis/segments"

output_folder = os.path.join("VideoFinis", "VideoMonte")
os.makedirs(output_folder, exist_ok=True)

# Vérifier si les dossiers existent
if not os.path.exists(folder_path1):
    raise FileNotFoundError(f"Le dossier {folder_path1} n'existe pas.")
if not os.path.exists(folder_path2):
    raise FileNotFoundError(f"Le dossier {folder_path2} n'existe pas.")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Récupérer les noms des fichiers vidéo dans chaque dossier
videos1 = sorted([os.path.join(folder_path1, f) for f in os.listdir(folder_path1) if f.endswith(('.mp4', '.mov', '.avi'))])
videos2 = sorted([os.path.join(folder_path2, f) for f in os.listdir(folder_path2) if f.endswith(('.mp4', '.mov', '.avi'))])

# S'assurer qu'il y a le même nombre de vidéos dans chaque dossier
if len(videos1) != len(videos2):
    raise ValueError("Les dossiers ne contiennent pas le même nombre de vidéos.")

for i in range(len(videos1)):
    # Charger les vidéos
    clip1 = VideoFileClip(videos1[i])
    clip2 = VideoFileClip(videos2[i])
    
    # Redimensionner les vidéos pour s'assurer qu'elles ont la même largeur
    width = max(clip1.w, clip2.w)
    clip1 = clip1.resized(width=width)
    clip2 = clip2.resized(width=width)
    
    # Déterminer la hauteur totale de la vidéo composite
    height = clip1.h + clip2.h # type: ignore
    
    # Créer une vidéo composite avec clip1 au-dessus de clip2
    final_clip = CompositeVideoClip([clip1.with_position(("center", "top")), # type: ignore
                                  clip2.with_position(("center", "bottom"))], # type: ignore
                                  size=(width, height))
    
    # Sauvegarder la vidéo assemblée
    output_path = os.path.join(output_folder, f'segment{i+1}.mp4')
    final_clip.write_videofile(output_path, codec='libx264')

print("Les vidéos ont été assemblées avec succès.")
