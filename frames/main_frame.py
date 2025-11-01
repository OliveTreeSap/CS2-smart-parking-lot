import customtkinter as ctk


class MainFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Configure grid layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header section
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        self.header_frame.grid_columnconfigure(0, weight=1)

        # Welcome message
        self.welcome_label = ctk.CTkLabel(
            self.header_frame,
            text="Welcome!",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.welcome_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")

        # Logout button
        self.logout_button = ctk.CTkButton(
            self.header_frame,
            text="Logout",
            command=self.logout,
            width=100
        )
        self.logout_button.grid(row=0, column=1, padx=20, pady=20, sticky="e")

        # Content area (placeholder for future features)
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Placeholder content
        self.placeholder_label = ctk.CTkLabel(
            self.content_frame,
            text="Main application content will go here",
            font=ctk.CTkFont(size=18)
        )
        self.placeholder_label.grid(row=0, column=0, padx=20, pady=20)

    def update_welcome(self, username):
        """Update the welcome message with the logged-in username"""
        self.welcome_label.configure(text=f"Welcome, {username}!")

    def logout(self):
        """Handle logout and return to login screen"""
        self.master.show_login()

