# CPRD
J'ai rajouté ça au débuts de la fonction display_smooth_amplitude_plot :

        self.spectrogram_canvas.destroy()
        self.spectrogram_canvas = customtkinter.CTkFrame(self, width=960, height=250, corner_radius=0, border_width=1, border_color="black")
        self.spectrogram_canvas.grid(row=0, column=1, padx=(20, 10), pady=(20, 0), sticky="nsew")
        self.spectrogram_canvas.grid_columnconfigure(1, weight=1)
        self.spectrogram_canvas.update()
        
En gros ça détruit la frame ou se trouve le spectrogramme puis la recrée mais vierge puis la fonction redessine par dessus
(c'était tarpin dur de tyrouver comment faire mon QI fais la température de la pièce)
