import customtkinter as ctk
import tkinter as tk
from PIL import Image
from frames.login_frame import LoginFrame


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Parking Lot Manager")
        self.geometry("1920x1080")
        # Expands the row and column so that they fit perfectly
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Creates and displays the login image
        self.login_image = ctk.CTkImage(dark_image=Image.open("assets/minecraft_night_2.jpg"),
                                     size=(1280, 1080))
        self.login_image_label = ctk.CTkLabel(self, image=self.login_image, text="")
        self.login_image_label.grid(row=0, column=0, sticky="we")

        # Initializes the login frame
        self.login_frame = LoginFrame(self)
        self.login_frame.grid(row=0, column=1, padx=50, pady=200, sticky="ew")


if __name__ == "__main__":
    app = App()
    app.mainloop()