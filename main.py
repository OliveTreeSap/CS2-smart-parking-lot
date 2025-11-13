import customtkinter as ctk
import tkinter as tk
from PIL import Image
from frames import login_frame, main_frame
from authentication.perm_manager import PermissionManager


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.perm_manager = PermissionManager()
        self.current_user = None

        self.title("Parking Lot Manager")
        self.geometry("1920x1080")

        # Initialize frames (all will be placed at the same location, stacked)
        self.login_frame = login_frame.LoginFrame(self)
        self.main_frame = main_frame.MainFrame(self)

        # Show login frame by default
        self.show_login()

    def show_frame(self, frame_to_show):
        """Generic method to switch between frames"""
        # Hide all frames
        self.login_frame.place_forget()
        self.main_frame.place_forget()
        
        # Show the requested frame (full screen)
        frame_to_show.place(x=0, y=0, relwidth=1, relheight=1)

    def show_login(self):
        """Show the login frame"""
        self.current_user = None
        self.show_frame(self.login_frame)

    def show_main(self, username):
        """Show the main frame after successful login"""
        self.current_user = username
        self.main_frame.update_welcome(username)
        self.show_frame(self.main_frame)


if __name__ == "__main__":
    app = App()
    app.mainloop()