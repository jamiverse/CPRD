    def save_and_quit(self):
        if self.file_path is not None:
            # Obtenir le contenu modifié du widget Text
            new_data = self.text_area.get(1.0, tk.END)
            
            # Charger les données d'origine du fichier
            with open(self.file_path, 'r') as f:
                original_data = f.readlines()
            
            # Remplacer les lignes modifiées dans les données d'origine
            modified_lines = new_data.split('\n')
            original_data[:len(modified_lines)] = modified_lines
            
            # Si le contenu modifié a moins de lignes que le contenu d'origine,
            # remplir le reste avec des lignes vides
            if len(modified_lines) < len(original_data):
                original_data[len(modified_lines):] = ['\n'] * (len(original_data) - len(modified_lines))
            
            # Écrire les données modifiées dans le fichier
            with open(self.file_path, 'w') as f:
                f.writelines(original_data)
            
            # Fermer la fenêtre
            self.root.destroy()