import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt

class AnnotationEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Annotation Editor")
        
        self.file_path = None
        self.annotations = None
        
        # Create widgets
        self.load_button = tk.Button(self.root, text="Load Annotations", command=self.load_annotations)
        self.load_button.pack(pady=10)
        
        self.save_button = tk.Button(self.root, text="Save and Quit", command=self.save_and_quit, state=tk.DISABLED)
        self.save_button.pack(pady=5)
        
        self.text_area = tk.Text(self.root, height=20, width=50)
        self.text_area.pack(padx=10, pady=5)
        
        self.root.mainloop()
    
    def load_annotations(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv")])
        if self.file_path:
            with open(self.file_path, 'r') as f:
                self.annotations = f.read()
            self.display_annotations()
            self.save_button.config(state=tk.NORMAL)
            self.plot_button.config(state=tk.NORMAL)

    
    def display_annotations(self):
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, self.annotations)
    

    def save_and_quit(self):
        if self.file_path is not None:
            # Obtenir le contenu modifié du widget Text
            new_data = self.text_area.get(1.0, tk.END)
            
            # Écrire le contenu modifié dans le fichier
            with open(self.file_path, 'w') as f:
                f.write(new_data)
            
            # Fermer la fenêtre
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AnnotationEditor(root)
