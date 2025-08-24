import os
import moviepy

# Dossiers contenant les vidéos
folder1 = r'C:\Users\danie\OneDrive\Documents\Thomas\Argents\Tik tok perso\Essai\video-content\l-EVEREST - facile-'
folder2 = r'C:\Users\danie\OneDrive\Documents\Thomas\Argents\Tik tok perso\Essai\video-content\\13 Minutes Minecraft Parkour Gameplay -Free to Use- -Map Download-'
output_folder = r'C:\Users\danie\OneDrive\Documents\Thomas\Argents\Tik tok perso\Essai\video-content\output'

# Vérifier si les dossiers existent
if not os.path.exists(folder1):
    raise FileNotFoundError(f"Le dossier {folder1} n'existe pas.")
if not os.path.exists(folder2):
    raise FileNotFoundError(f"Le dossier {folder2} n'existe pas.")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Récupérer les noms des fichiers vidéo dans chaque dossier
videos1 = sorted([os.path.join(folder1, f) for f in os.listdir(folder1) if f.endswith(('.mp4', '.mov', '.avi'))])
videos2 = sorted([os.path.join(folder2, f) for f in os.listdir(folder2) if f.endswith(('.mp4', '.mov', '.avi'))])

# S'assurer qu'il y a le même nombre de vidéos dans chaque dossier
if len(videos1) != len(videos2):
    raise ValueError("Les dossiers ne contiennent pas le même nombre de vidéos.")

for i in range(len(videos1)):
    # Charger les vidéos
    clip1 = VideoFileClip(videos1[i])
    clip2 = VideoFileClip(videos2[i])
    
    # Redimensionner les vidéos pour s'assurer qu'elles ont la même largeur
    width = max(clip1.w, clip2.w)
    clip1 = clip1.resize(width=width)
    clip2 = clip2.resize(width=width)
    
    # Déterminer la hauteur totale de la vidéo composite
    height = clip1.h + clip2.h
    
    # Créer une vidéo composite avec clip1 au-dessus de clip2
    final_clip = CompositeVideoClip([clip1.set_position(("center", "top")),
                                  clip2.set_position(("center", "bottom"))],
                                  size=(width, height))
    
    # Sauvegarder la vidéo assemblée
    output_path = os.path.join(output_folder, f'output_{i+1}.mp4')
    final_clip.write_videofile(output_path, codec='libx264')

print("Les vidéos ont été assemblées avec succès.")
