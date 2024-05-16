import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import json
import BirdSongApp

class ChangeParamApp(ctk.CTk):
    def __init__(self, parameters_file):
        super().__init__()

        self.title("Change Parameters")
        self.geometry(f"{400}x{400}")
        self.parameters_file = parameters_file
        self.parameters = self.load_parameters()
        self.create_widgets()

        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=1, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.save_button = ctk.CTkButton(self.sidebar_frame, text="Save", command=self.save_changes)
        self.save_button.grid(row=0, column=0, padx=(20, 20), pady=(10, 10), sticky="ew")

    def load_parameters(self):
        try:
            with open(self.parameters_file, "r") as file:
                parameters = json.load(file)
            return parameters
        except FileNotFoundError:
            messagebox.showerror("Error", "File not found")

    def create_widgets(self):
        self.parameter_entries = {}
        row = 1
        for parameter, value in self.parameters.items():
            label = ctk.CTkLabel(self, text=parameter)
            label.grid(row=row, column=0, padx=5, pady=5, sticky="w")
            entry = ctk.CTkEntry(self)
            entry.insert(0, str(value))
            entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
            self.parameter_entries[parameter] = entry
            row += 1
        
    def save_changes(self):
        for parameter, entry in self.parameter_entries.items():
            try:
                value = float(entry.get())
                self.parameters[parameter] = value
            except ValueError:
                print(f"Invalid value for parameter '{parameter}': {entry.get()}")
        with open(self.parameters_file, "w") as file:
            json.dump(self.parameters, file, indent=4)
        print("Parameters updated and saved.")


if __name__ == "__main__":
    parameters_file = "parameters.json"
    app = ChangeParamApp(parameters_file)
    app.mainloop()
