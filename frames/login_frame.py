from tkinter import CENTER
import customtkinter as ctk
import CTkMessagebox as ctkmb


class LoginFrame(ctk.CTkFrame):
    """A class that handles the login user interface"""
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Logo
        self.logo = ctk.CTkLabel(self, text="SPL", font=ctk.CTkFont("Broadway", size=75, weight="bold"), text_color="#E2725B")
        self.logo.place(relx=0.067, rely=0.0369)

        # Smaller frame to fit the login widgets
        self.widget_frame = ctk.CTkFrame(self)
        self.widget_frame.place(relx=0.5, rely=0.5, relwidth=0.75, anchor="center")

        # Expands the widgets to fit the frame
        self.widget_frame.grid_columnconfigure(0, weight=1)

        # Labels for the title and welcome text
        self.title = ctk.CTkLabel(self.widget_frame, text="Login", font=ctk.CTkFont(size=40))
        self.title.grid(row=0, column=0,  padx=20, pady=(30, 5), sticky="nsw")

        self.welcome_text = ctk.CTkLabel(self.widget_frame, text="Welcome back! Please enter your credentials.")
        self.welcome_text.grid(row=1, column=0, padx=20, pady=(5, 15), sticky="nsw")

        # Entries for username and password, both are bound to the Enter key
        self.name_entry = ctk.CTkEntry(self.widget_frame, placeholder_text="Your username")
        self.name_entry.bind('<Return>', lambda e: self.get_info())
        self.name_entry.grid(row=2, column=0, padx=20, pady=(15, 10), sticky="nsew")

        # use a consistent attribute name for the password entry
        self.password_entry = ctk.CTkEntry(self.widget_frame, placeholder_text="Your password", show="*")
        self.password_entry.bind('<Return>', lambda e: self.get_info())
        self.password_entry.grid(row=3, column=0, padx=20, pady=(10, 10), sticky="nsew")

        # Login button
        self.login_button = ctk.CTkButton(self.widget_frame, text="Login", command=self.get_info)
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