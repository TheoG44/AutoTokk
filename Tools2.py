import os

#============================================================================
#
#
#         Renamme des fichiers dans le dossier Videos2
#
#
#============================================================================

def renommer_fichiers(dossier, prefix="Mc", extension=".mp4"):
    """
    Renomme tous les fichiers d'un dossier en prefix_01, prefix_02, ...
    
    :param dossier: chemin du dossier contenant les fichiers
    :param prefix: préfixe pour les nouveaux fichiers
    :param extension: extension des fichiers à renommer
    """
    if not os.path.exists(dossier):
        print(f"❌ Le dossier '{dossier}' n'existe pas.")
        return

    fichiers = sorted([f for f in os.listdir(dossier) if f.endswith(extension)])
    
    if not fichiers:
        print(f"⚠️ Aucun fichier '{extension}' trouvé dans {dossier}")
        return

    for i, fichier in enumerate(fichiers, start=1):
        nouveau_nom = f"{prefix}_{i:02d}{extension}"
        ancien_chemin = os.path.join(dossier, fichier)
        nouveau_chemin = os.path.join(dossier, nouveau_nom)
        os.rename(ancien_chemin, nouveau_chemin)
        print(f"✅ {fichier} → {nouveau_nom}")

    print("🎉 Tous les fichiers ont été renommés.")

# Exemple d'utilisation
if __name__ == "__main__":
    dossier = "Videos2"  # changer le chemin du dossier
    renommer_fichiers(dossier)
