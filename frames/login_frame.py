import customtkinter as ctk
import CTkMessagebox as ctkmb
import pywinstyles
from PIL import Image
from ctk_addons import IconEntry


class LoginFrame(ctk.CTkFrame):
    """A class that handles the login user interface"""
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Background image
        self.background_img = ctk.CTkImage(dark_image=Image.open("assets/login_background.png"),
                                          size=(2167, 1080))
        self.background_label = ctk.CTkLabel(self, image=self.background_img, text="")
        self.background_label.place(x=0, y=0)

        # Logo
        self.logo = ctk.CTkLabel(self, text="SPKL", font=ctk.CTkFont("Broadway", size=50, weight="bold"), 
                                text_color="white", bg_color='#000001')
        self.logo.place(relx=0.04, rely=0.02)
        pywinstyles.set_opacity(self.logo, color="#000001")

        # Login title
        self.title = ctk.CTkLabel(self, text="LOGIN", 
                                   font=ctk.CTkFont(size=75, weight="bold"),
                                   text_color="white", bg_color='#000001')
        self.title.place(relx=0.05, rely=0.15)
        pywinstyles.set_opacity(self.title, color="#000001")

        # Welcome back subtitle
        self.welcome_text = ctk.CTkLabel(self, text="Welcome back", 
                                        font=ctk.CTkFont(size=24),
                                        text_color="white", bg_color="#000001")
        self.welcome_text.place(relx=0.05, rely=0.25)
        pywinstyles.set_opacity(self.welcome_text, color="#000001")

        # Please enter your information text
        self.info_text = ctk.CTkLabel(self, text="Please enter your information",
                                      font=ctk.CTkFont(size=24),
                                      text_color="white", bg_color="#000001")
        self.info_text.place(relx=0.05, rely=0.28)
        pywinstyles.set_opacity(self.info_text, color="#000001")

        # Load icons for the entry fields
        self.user_icon = ctk.CTkImage(Image.open("assets/user_icon.png"), size=(34, 34))
        self.password_icon = ctk.CTkImage(Image.open("assets/password_icon.png"), size=(34, 34))

        # Username entry with icon
        self.name_entry = IconEntry(self, icon=self.user_icon, 
                                    placeholder_text="Username",
                                    corner_radius=10,
                                    height=50)
        self.name_entry.entry.bind('<Return>', lambda e: self.get_info())
        self.name_entry.place(relx=0.05, rely=0.34)

        # Password entry with icon
        self.password_entry = IconEntry(self, icon=self.password_icon,
                                       placeholder_text="Password",
                                       corner_radius=10,
                                       height=50)
        self.password_entry.entry.configure(show="*")
        self.password_entry.entry.bind('<Return>', lambda e: self.get_info())
        self.password_entry.place(relx=0.05, rely=0.44)


        # Sign up link (left)
        self.signup_link = ctk.CTkLabel(self, text="Sign up",
                                       font=ctk.CTkFont(size=20),
                                       text_color="white", bg_color="#000001",
                                       cursor="hand2")
        self.signup_link.place(relx=0.05, rely=0.522)
        pywinstyles.set_opacity(self.signup_link, color="#000001")

        # Forgot password link (right)
        self.forgot_link = ctk.CTkLabel(self, text="Forgot password?",
                                       font=ctk.CTkFont(size=20),
                                       text_color="white", bg_color="#000001",
                                       cursor="hand2")
        self.forgot_link.place(relx=0.314, rely=0.522)
        pywinstyles.set_opacity(self.forgot_link, color="#000001")

        # Sign in button with white background
        self.login_button = ctk.CTkButton(self, text="Sign in", 
                                         command=self.get_info,
                                         fg_color="white", bg_color="#000001",
                                         text_color="black",
                                         hover_color=("#E0E0E0", "#D0D0D0"),
                                         font=ctk.CTkFont(size=24, weight="bold"),
                                         corner_radius=25,
                                         width=660, height=75)
        self.login_button.place(relx=0.05, rely=0.57)
        pywinstyles.set_opacity(self.login_button, color="#000001")

        # Back button to return to user selection
        self.back_button = ctk.CTkButton(self, text="← Back", 
                        command=master.show_user_select,
                        fg_color="gray", bg_color="#000001",
                        text_color="white",
                        hover_color=("#505050", "#404040"),
                        font=ctk.CTkFont(size=14, weight="bold"),
                        corner_radius=25,
                        width=100, height=40)
        self.back_button.place(relx=0.015, rely=0.9)
        pywinstyles.set_opacity(self.back_button, color="#000001")

        # Exit button to exit the app
        self.exit_button = ctk.CTkButton(self, text="Exit", 
                        command=master.destroy,
                        fg_color="red", bg_color="#000001",
                        text_color="black",
                        hover_color=("#E0E0E0", "#D0D0D0"),
                        font=ctk.CTkFont(size=14, weight="bold"),
                        corner_radius=25,
                        width=100, height=40)
        self.exit_button.place(relx=0.015, rely=0.95)
        pywinstyles.set_opacity(self.exit_button, color="#000001")

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