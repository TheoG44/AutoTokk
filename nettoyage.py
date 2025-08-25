import os
import shutil

def nettoyage_test():
    video_finale = os.path.join("VideoFinis", "VideoFinale1080p.mp4")
    folder_path1 = os.path.join("VideoFinis", "segments")
    folder_path2 = os.path.join("VideoFinis", "segments")

    try:
        # Supprimer la vidéo finale
        if os.path.exists(video_finale):
            os.remove(video_finale)
            print("🗑️ VideoFinale1080p.mp4 supprimée.")

        # Supprimer les segments
        if os.path.exists(folder_path1):
            shutil.rmtree(folder_path1)
            print(f"🗑️ Segments supprimés dans {folder_path1}.")
        if os.path.exists(folder_path2) and folder_path2 != folder_path1:
            shutil.rmtree(folder_path2)
            print(f"🗑️ Segments supprimés dans {folder_path2}.")

    except Exception as e:
        print(f"⚠️ Erreur lors du nettoyage : {e}")

if __name__ == "__main__":
    nettoyage_test()
