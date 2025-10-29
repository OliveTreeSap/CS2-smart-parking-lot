import customtkinter as ctk


# A class for the login frame
class LoginFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Expands the widgets to fit the frame
        self.grid_columnconfigure(0, weight=1)

        # Labels for the title and welcome text
        self.title = ctk.CTkLabel(self, text="Login", font=ctk.CTkFont(size=32))
        self.title.grid(row=0, column=0,  padx=20, pady=(20, 5), sticky="w")

        self.welcome_text = ctk.CTkLabel(self, text="Welcome back! Please enter your credentials.")
        self.welcome_text.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="w")

        # Entries for username and password
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Your username")
        self.name_entry.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="ew")

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Your password", show="*")
        self.password_entry.grid(row=3, column=0, padx=20, pady=(5, 10), sticky="ew")

        # Login button
        self.login_button = ctk.CTkButton(self, text="Login")
        self.login_button.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="ew")


if __name__ == "__main__":
    LoginFrame()