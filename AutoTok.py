import tkinter
from pytube import YouTube
from moviepy import *
import os
import math
import shutil

# Functions for the application
def decouper_video(url):
    try:
        # Téléchargement de la vidéo
        youtube_video = YouTube(url)
        video_stream = youtube_video.streams.filter(file_extension='mp4').first()
        video_path = video_stream.download(output_path='video-content') # type: ignore

        # Création d'un nouveau dossier pour les découpes de la vidéo
        titre_video = youtube_video.title.replace(".mp4", "")
        titre_video = ''.join(e if e.isalnum() or e.isspace() else '-' for e in titre_video)
        dossier_decoupes = os.path.join("video-content", titre_video)
        os.makedirs(dossier_decoupes, exist_ok=True)

        # Durée de chaque segment en secondes
        duree_segment = 60

        # Découpage de la vidéo en segments de 1 minute
        video_duration = youtube_video.length  # Durée totale de la vidéo en secondes
        nombre_segments = math.ceil(video_duration / duree_segment)  # Nombre total de segments

        for i in range(nombre_segments):
            start_time = i * duree_segment
            end_time = min(start_time + duree_segment, video_duration)

            if i == nombre_segments - 1:
                if end_time - start_time < duree_segment:
                    start_time = (nombre_segments - 2) * duree_segment

            if i == nombre_segments - 2:
                continue

            for file in os.listdir("video-content"):
                if file.endswith(".mp4"):
                    file_path = os.path.join("video-content", file)
                    output_file_name = f"segment_{start_time}_{end_time}.mp4"
                    output_file_path = os.path.join(dossier_decoupes, output_file_name)
                    ffmpeg_extract_subclip(file_path, start_time, end_time, targetname=output_file_path)
                    break
        messagebox.showinfo("Succès", "La vidéo a été découpée avec succès!")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

def vider_corbeille():
    corbeille_path = os.path.join("video-content", "bin")
    if not os.path.exists(corbeille_path):
        messagebox.showinfo("Information", "La corbeille est déjà vide.")
        return

    confirmation = messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir vider la corbeille ?")
    if not confirmation:
        messagebox.showinfo("Information", "La corbeille n'a pas été vidée.")
        return

    for file in os.listdir(corbeille_path):
        file_path = os.path.join(corbeille_path, file)
        os.remove(file_path)
    os.rmdir(corbeille_path)
    messagebox.showinfo("Succès", "La corbeille a été vidée.")

def renommer_fichiers():
    def move_file_to_bin(file_path, bin_path):
        if not os.path.exists(bin_path):
            os.makedirs(bin_path)
        shutil.move(file_path, bin_path)
        messagebox.showinfo("Succès", f"Le fichier {os.path.basename(file_path)} a été déplacé dans la corbeille.")

    dossier = filedialog.askdirectory(title="Choisissez un dossier")
    if not dossier:
        return

    fichiers_mp4 = [file for file in os.listdir(dossier) if file.endswith(".mp4")]
    if not fichiers_mp4:
        messagebox.showinfo("Information", "Aucun fichier .mp4 trouvé dans ce dossier.")
        return

    bin_path = os.path.join(dossier, "../bin")
    for file in fichiers_mp4:
        file_path = os.path.join(dossier, file)
        response = messagebox.askyesno("Déplacer le fichier", f"Voulez-vous déplacer {file} dans la corbeille ?")
        if response:
            move_file_to_bin(file_path, bin_path)

# GUI Application
class VideoApp(tkinter.Tk):
    def __init__(self):
        super().__init__()

        self.title("Gestionnaire de Vidéos")
        self.geometry("800x600")

        # Title
        self.title_label = tkinter.Label(self, text="Gestionnaire de Vidéos", font=("Arial", 24, "bold"), bg="black", fg="white")
        self.title_label.pack(pady=20)

        # Buttons
        self.button_frame = tkinter.Frame(self, bg="black")
        self.button_frame.pack(pady=50)

        self.cut_video_button = tkinter.Button(self.button_frame, text="Découper une vidéo", command=self.cut_video, font=("Arial", 14))
        self.cut_video_button.grid(row=0, column=0, padx=20, pady=10)

        self.manage_files_button = tkinter.Button(self.button_frame, text="Gestionnaire de fichiers", command=self.manage_files, font=("Arial", 14))
        self.manage_files_button.grid(row=1, column=0, padx=20, pady=10)

        self.empty_bin_button = tkinter.Button(self.button_frame, text="Vider la corbeille", command=vider_corbeille, font=("Arial", 14))
        self.empty_bin_button.grid(row=2, column=0, padx=20, pady=10)

    def cut_video(self):
        url = simpledialog.askstring("URL de la vidéo", "Insérez le lien de votre vidéo YouTube : ")
        if url:
            decouper_video(url)

    def manage_files(self):
        renommer_fichiers()


# Fonction de démarrage
if __name__ == "__main__":
    app = VideoApp()
    app.mainloop()
