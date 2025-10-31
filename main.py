import customtkinter as ctk
import tkinter as tk
from PIL import Image
from frames import login_frame
from authentication.perm_manager import PermissionManager


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.perm_manager = PermissionManager()

        self.title("Parking Lot Manager")
        self.geometry("1920x1080")
        # Expands the row and column so that they fit perfectly
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Transparent image to offset the login frame
        self.offset_image = ctk.CTkImage(dark_image=Image.open("CS2/assets/login_offset.png"),
                                     size=(1280, 1080))
        self.offset_image_label = ctk.CTkLabel(self, image=self.offset_image, text="")
        self.offset_image_label.grid(row=0, column=0, sticky="we")

        # Background image for the login frame
        self.background_img = ctk.CTkImage(dark_image=Image.open("CS2/assets/minecraft_night_1_gradient.png"),
                                           size=(1920, 1080))
        self.background_img_label = ctk.CTkLabel(self, image=self.background_img, text="")
        self.background_img_label.place(x=0, y=0)

        # Initializes the login frame
        self.login_frame = login_frame.LoginFrame(self)
        self.login_frame.grid(row=0, column=1, padx=50, sticky="ew")


if __name__ == "__main__":
    app = App()
    app.mainloop()