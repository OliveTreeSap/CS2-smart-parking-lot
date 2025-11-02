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

        # Background image for the login screen only
        self.background_img = ctk.CTkImage(dark_image=Image.open("assets/minecraft_night_1_gradient.png"),
                                           size=(1920, 1080))
        self.background_img_label = ctk.CTkLabel(self, image=self.background_img, text="")
        self.background_img_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Initialize frames (all will be placed at the same location, stacked)
        self.login_frame = login_frame.LoginFrame(self)
        self.main_frame = main_frame.MainFrame(self)

        # Show login frame by default
        self.show_login()

    def show_frame(self, frame_to_show, show_background=True, center=False):
        """Generic method to switch between frames"""
        # Hide all frames
        self.login_frame.place_forget()
        self.main_frame.place_forget()
        
        # Show or hide background
        if show_background:
            self.background_img_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.background_img_label.place_forget()
        
        # Show the requested frame
        if center:
            # Center the frame (for login with background visible)
            frame_to_show.place(relx=1-0.3/2, rely=0.5, relwidth=0.3, relheight=1, anchor="center")
        else:
            # Full screen frame (for main content)
            frame_to_show.place(x=0, y=0, relwidth=1, relheight=1)

    def show_login(self):
        """Show the login frame with background"""
        self.current_user = None
        self.show_frame(self.login_frame, show_background=True, center=True)

    def show_main(self, username):
        """Show the main frame after successful login"""
        self.current_user = username
        self.main_frame.update_welcome(username)
        self.show_frame(self.main_frame, show_background=False)


if __name__ == "__main__":
    app = App()
    app.mainloop()