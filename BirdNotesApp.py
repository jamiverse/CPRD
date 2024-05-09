import tkinter as tk
import tkinter.messagebox
import customtkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from scipy.io import wavfile
from scipy.signal import spectrogram
import numpy as np
import os
import json
import sys
import subprocess
import glob
import shutil
# Si Song_fucntions est dans le même dossier, sinon il faut modifier en import Song_functions from ""
import Song_functions




customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("dark-blue")
customtkinter.set_widget_scaling(1.0) #permets de régler la taille des widgets

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Bird Song Recognition")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        #frame pour le spectrogramme (régler les problèmes de dimensions)
        self.spectrogram_canvas = customtkinter.CTkFrame(self, width=960, height=250, corner_radius=0, border_width=1, border_color="black")
        self.spectrogram_canvas.grid(row=0, column=1, padx=(20, 10), pady=(20, 0), sticky="nsew")
        self.spectrogram_canvas.grid_columnconfigure(1, weight=1)


        #frame à gauche pour les boutons
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.save_button = customtkinter.CTkButton(self.sidebar_frame, text="Save spectrogram", command=self.save_spectrogram)
        self.save_button.grid(row=3, column=0, padx=(20, 20), pady=(10, 10), sticky="ew")
        
        #nom de l'interface
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Bird Song Recognition", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        #ajout des boutons dans le sidebar
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.fetch_audio_file, text= "Fetch audio file")
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
       
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.save_annotations, text="Save annotations")
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        # Bouton pour séparer les silences (path = current directory) il faut que le dossier source (Raw_songs) soit dans le même dossier que le code
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=lambda: self.split_silences(os.path.dirname(os.path.abspath(__file__))), text="Clean audio files")
        self.sidebar_button_3.grid(row=4, column=0, padx=20, pady=10)

        
        #label des boutons
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        
        # Ajout de l'option de scaling
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))


        #frame d'en bas
        self.low_frame = customtkinter.CTkFrame(self)
        self.low_frame.grid(row=1, column=1, padx=(20, 10), pady=(20, 10), sticky="nsew") 
        self.low_frame.grid_columnconfigure(1, weight=1)
        
        #pr les annotations automatiques (hvc) (pas encore implémenté)
        automatic_annotations_button = customtkinter.CTkOptionMenu(self.low_frame, values=["HVC"]) #mettre la commande
        automatic_annotations_button.grid(row=0, column=1, padx=(20, 10), pady=(10, 20), sticky="ew")
        automatic_annotations_label = customtkinter.CTkLabel(self.low_frame, text="Automatic annotations: ", anchor="center") #anchor="w" aligne le texte à gauche, pour
        automatic_annotations_label.grid(row=0, column=0, padx=(20, 10), pady=(10, 20), sticky="ew")

        # Add button to adjust amplitude threshold
        adjust_threshold_button = customtkinter.CTkButton(self.low_frame, text="Adjust Amplitude Threshold", command=self.adjust_amplitude_threshold)
        adjust_threshold_button.grid(row=0, column=2, padx=(20, 10), pady=(10, 10), sticky="nsew") 

        #pr des notes qui sait (à modifier en tant que fenètre permettant l'affichage des spectrogrammes)
        self.textbox = customtkinter.CTkTextbox(self.low_frame, width=250)
        self.textbox.grid(row=1, column=2, padx=(20, 10), pady=(10, 0), sticky="nsew")
        self.textbox.insert("0.0", "Ceci est un exemple de note")
        
        # Store annotations
        self.annotations = []

        # Store text objects for annotations
        self.annotation_texts = []

        # Store ax for accessing in other methods
        self.ax = None

        #pour stocker audio_data et sample_rate
        self.audio_data = None
        self.sample_rate = None

        # bouton pour déclencher la fonction de division des enregistrements (à implémenter)

        self.last_added_annotation = None

        #ctrl Z pour enlever les annotations (à implémenter)
        #self.bind("<Control-z>", self.undo_annotation)
        #self.bind("<Command-z>", self.undo_annotation)


    def split_silences(self, folder_path):
        print('Splitting silences...')
        window =('hamming')
        overlap = 64
        nperseg = 1024
        noverlap = nperseg-overlap
        colormap = "jet"
        smooth_win = 10

        #IMPORTANT -> Threshold params
        parameters      =   json.load(open('parameters.json'))
        threshold       =   parameters['threshold']
        min_syl_dur     =   parameters['min_syl_dur']
        min_silent_dur  =   parameters['min_silent_dur']

        #Contains the labels of the syllables from a single .wav file
        labels = []
        syl_counter=0
        Nb_syls=0
        keep_song =''
        #rec_system = 'Alpha_omega' # or 'Neuralynx' or 'Other'
        rec_system = parameters['rec_system']


        folder_name = folder_path
        if os.path.isdir(folder_name) is False:
            raise ValueError("Not a folder.")

        print(folder_name)
        source_path = folder_name + '/Raw_songs'
        target_path_noise = folder_name + '/No_songs'
        target_path_clean = folder_name + '/Clean_songs'
        if not os.path.exists(source_path):
            raise ValueError('Raw_songs folder does not exist.')
        if not os.path.exists(target_path_noise):
            os.mkdir(target_path_noise)
            print('Created folder No_songs.')
        if not os.path.exists(target_path_clean):
            os.mkdir(target_path_clean)
            print('Created folder Clean.')

        filetype = '.wav' # '.txt'
        if rec_system == 'Alpha_omega':
            fs = 22321.4283
        elif rec_system == 'Neuralynx':
            fs = 32000
        elif rec_system == 'Neuropixel':
            fs = 32723.037368
            
        print('fs:',fs)
        songfiles_list = glob.glob(source_path + '/*' + filetype)
        lsl = len(songfiles_list)

        for file_num, songfile in enumerate(songfiles_list):
            print('File no:', file_num, 'from ', lsl)
            base_filename = os.path.basename(songfile)
            
            #Read song file
            print('File name: %s' % songfile)
            if filetype == '.txt':
                rawsong = np.loadtxt(songfile)
            elif filetype == '.npy':
                rawsong = np.load(songfile)
            elif filetype == '.wav':
                fs, rawsong = wavfile.read(songfile)

            
            #Bandpass filter, square and lowpass filter
            #cutoffs : 1000, 8000
            try:
                amp = Song_functions.smooth_data(rawsong,fs,freq_cutoffs=(1000, 8000))
            except ValueError:
                print('Moving file to noise because length of rawsong is not greater than padlen.')
                file_path_target_noise = target_path_noise+'/'+base_filename
                os.rename(songfile, file_path_target_noise)
                continue

            
            #Segment song
            (onsets, offsets) = Song_functions.segment_song(amp,segment_params={'threshold': threshold, 'min_syl_dur': min_syl_dur, 'min_silent_dur': min_silent_dur},samp_freq=fs)
            shpe = len(onsets)
            if shpe < 1:
                file_path_target_noise = target_path_noise+'/'+base_filename
                shutil.copy2(songfile, file_path_target_noise)
            else:
                file_path_target_clean = target_path_clean+'/'+base_filename
                shutil.copy2(songfile, file_path_target_clean)

            print("All files processed.")


    

    #fonction pour récupérer le fichier audio
    def fetch_audio_file(self):
        file_path = tkinter.filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav")])
        if file_path:
            self.display_spectrogram(file_path)

    #fonction pour afficher le spectrogramme
    def display_spectrogram(self, file_path):
        self.sample_rate, self.audio_data = wavfile.read(file_path)
        _, _, Sxx = spectrogram(self.audio_data, fs=self.sample_rate)

        # Définir les dimensions de la figure en fonction des dimensions du cadre spectrogram_canvas
        fig_width = self.spectrogram_canvas.winfo_width() / 100  # Convertir en pouces
        fig_height = self.spectrogram_canvas.winfo_height() / 100 # Convertir en pouces

        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        im = ax.specgram(self.audio_data, Fs=self.sample_rate)[3]  # Obtenez l'objet image seulement
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (Hz)')
        ax.set_title('Spectrogram of Audio File')

        # Incorporer la figure dans le widget Canvas
        canvas = FigureCanvasTkAgg(fig, master=self.spectrogram_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        #Ajouter la barre d'outils matplotlib (si besoin pour zoomer ect)
        #toolbar = NavigationToolbar2Tk(canvas, self.spectrogram_canvas)
        #toolbar.update()

        self.ax = ax  # Store ax for accessing later
        
        # Bind left-click event to the spectrogram (simulate double-click)
        canvas.mpl_connect('button_press_event', lambda event: self.on_spectrogram_double_click(event, file_path))

    #fonction pour ajouter des annotations au boucle clic sur le spectrogramme (suivi d'un simple clic pour terminer l'annotation)
    def on_spectrogram_double_click(self, event, file_path):
        if event.button == 1 and event.dblclick:
            #coordinates of double-click
            x, y = event.xdata, event.ydata

            #enter annotation
            annotation = tk.simpledialog.askstring("Annotation", "Enter annotation:")
            if not annotation:
                return
            
            #vertical line at the double-click location
            self.ax.axvline(x=x, color='r', linestyle='-')
        
            #Store annotation with coordinates
            self.temp_annotation = (x, y, annotation)
            print("Temp annotation set:", self.temp_annotation)

            #Add annotation text next to the red line
            text = self.ax.text(x + 0.1, y, annotation, color='red', fontsize=8)
            self.annotation_texts.append(text)

            plt.draw()

        else:
            #coordinates of single click
            x, y = event.xdata, event.ydata
            
            if self.temp_annotation is not None:
                #second vertical line at the click location
                self.ax.axvline(x=x, color='b', linestyle='-')
                
                # Add the second bar to the annotation
                self.temp_annotation = (self.temp_annotation[0], x, self.temp_annotation[2])
                self.annotations.append(self.temp_annotation)
                print("Annotation added:", self.temp_annotation)

                text = self.ax.text(x + 0.1, y, self.temp_annotation[2], color='blue', fontsize=8)
                self.annotation_texts.append(text)

                self.last_added_annotation = self.temp_annotation
                
                # Remove temporary annotation
                self.temp_annotation = None
                
                # Update the plot
                plt.draw()

    #fonction pour ajuster le seuil d'amplitude
    def adjust_amplitude_threshold(self):
        #enter the amplitude threshold
        threshold = tk.simpledialog.askfloat("Amplitude Threshold", "Enter Amplitude Threshold:")
        if threshold is not None:
            #ajuster amplitude threshold for spectrogram display
            self.ax.set_ylim(0, threshold)
            plt.draw()
    
    #fonction pour enregistrer les annotations
    def save_annotations(self):
        #save dans csv
        annotation_file_path = tk.filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Excel Files", "*.csv")])
        if annotation_file_path:
            with open(annotation_file_path, "w") as f:
                # Write headers
                f.write("Start Time (s), End Time (s), Annotation Label\n")
                
                # Write annotations
                for annotation in self.annotations:
                    f.write(f"{annotation[0]}, {annotation[1]}, {annotation[2]}\n")
            
            tk.messagebox.showinfo("File Saved", f"Annotations saved to {annotation_file_path}")

    #fonction pour enregistrer le spectrogramme
    def save_spectrogram(self):
        # Vérifier s'il y a des annotations à sauvegarder
        if not self.annotations:
            tk.messagebox.showwarning("Aucune annotation", "Il n'y a aucune annotation à sauvegarder.")
            return

        # Récupérer les données du spectrogramme actuellement affiché
        Sxx, _, _, _ = self.ax.specgram(self.audio_data, Fs=self.sample_rate)
        spectrogram_data = Sxx

        # Enregistrer les annotations avec le spectrogramme
        annotated_spectrogram = {
            "spectrogram_data": spectrogram_data,
            "annotations": self.annotations
        }

        #choisir un emplacement pour enregistrer le fichier .npy
        file_path = tk.filedialog.asksaveasfilename(defaultextension=".npy", filetypes=[("NumPy Files", "*.npy")])
        if file_path:
            #enregistrer les données au format .npy
            np.save(file_path, annotated_spectrogram)

            tk.messagebox.showinfo("Spectrogramme Enregistré", f"Le spectrogramme annoté a été enregistré sous: {file_path}")

        
    #fonction pour changer le mode d'apparence
    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    #fonction pour changer le scaling
    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)


if __name__ == "__main__":
    app = App()
    app.mainloop()

