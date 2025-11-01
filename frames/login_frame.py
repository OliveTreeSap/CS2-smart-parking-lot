import customtkinter as ctk
import CTkMessagebox as ctkmb
from authentication.perm_manager import PermissionManager


# A class for the login frame
class LoginFrame(ctk.CTkFrame):
    def __init__(self, master):
        # initialize the CTkFrame with the master only
        super().__init__(master, fg_color="transparent")

        # Expands the widgets to fit the frame
        # self.grid_rowconfigure([0, 2, 3, 4], weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Labels for the title and welcome text
        self.title = ctk.CTkLabel(self, text="Login", font=ctk.CTkFont(size=40))
        self.title.grid(row=0, column=0,  padx=20, pady=(30, 5), sticky="nsw")

        self.welcome_text = ctk.CTkLabel(self, text="Welcome back! Please enter your credentials.")
        self.welcome_text.grid(row=1, column=0, padx=20, pady=(5, 15), sticky="nsw")

        # Entries for username and password, both are bound to the Enter key
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Your username")
        self.name_entry.bind('<Return>', lambda e: self.get_info())
        self.name_entry.grid(row=2, column=0, padx=20, pady=(15, 10), sticky="nsew")

        # use a consistent attribute name for the password entry
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Your password", show="*")
        self.password_entry.bind('<Return>', lambda e: self.get_info())
        self.password_entry.grid(row=3, column=0, padx=20, pady=(10, 10), sticky="nsew")

        # Login button
        self.login_button = ctk.CTkButton(self, text="Login", command=self.get_info)
        self.login_button.grid(row=4, column=0, padx=20, pady=(10, 30), sticky="nsew")

    def get_info(self):
        """Get username and password and check if any corresponding name, password exists"""
        name = self.name_entry.get()
        password = self.password_entry.get()
        if self.master.perm_manager.authenticator(name, password):
            self.name_entry.delete(0, ctk.END)
            self.password_entry.delete(0, ctk.END)
            # Switch to main frame on successful login
            self.master.show_main(name)
        else:
            self.password_entry.delete(0, ctk.END)
            ctkmb.CTkMessagebox(title="Error", message="Invalid username or password!", icon="cancel")