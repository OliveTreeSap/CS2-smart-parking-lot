import os
import customtkinter as ctk
import CTkMessagebox as ctkmb
import pywinstyles
from PIL import Image
from ctk_addons import IconEntry


class PasswordDialog(ctk.CTkToplevel):
    """A password dialog that appears when a user is selected"""
    def __init__(self, parent, username, on_success_callback):
        super().__init__(parent)
        self.username = username
        self.on_success_callback = on_success_callback
        self.perm_manager = parent.master.perm_manager
        
        # Configure window
        self.title("Enter Password")
        self.geometry("400x300")
        self.resizable(False, False)
        self.configure(fg_color="#000000")
        
        # Center the window
        self.transient(parent)
        self.grab_set()
        
        # Username label
        self.username_label = ctk.CTkLabel(
            self, 
            text=f"Welcome, {username}!",
            font=ctk.CTkFont("Tw Cen MT Condensed Extra Bold", size=24)
        )
        self.username_label.pack(pady=(30, 10))
        
        # Instruction label
        self.instruction_label = ctk.CTkLabel(
            self,
            text="Please enter your password",
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=18)
        )
        self.instruction_label.pack(pady=(0, 20))
        
        # Password entry
        self.password_entry = IconEntry(
            self, icon=ctk.CTkImage(Image.open("assets/password_icon.png"), size=(34, 34)),
            placeholder_text="Password",
            corner_radius=15,
            border_width=2, border_color="#FFFFFF",
            fg_color="#000000"
        )
        self.password_entry.entry.configure(show="*")
        self.password_entry.entry.bind('<Return>', lambda e: self.verify_password())
        self.password_entry.pack(padx=34, pady=(10, 30))
        self.password_entry.focus()
        
        # Button frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=(0, 20))
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancel", font=ctk.CTkFont("Bahnschrift Light Condensed", size=18),
            command=self.destroy,
            width=120,
            height=35,
            fg_color="red",
            hover_color="darkgray"
        )
        self.cancel_button.pack(side="left", padx=5)
        
        # Submit button
        self.submit_button = ctk.CTkButton(
            self.button_frame,
            text="Submit", text_color="#000000", font=ctk.CTkFont("Bahnschrift Light Condensed", size=18),
            command=self.verify_password,
            width=120,
            height=35,
            fg_color="#FFFFFF"
        )
        self.submit_button.pack(side="left", padx=5)
    
    def verify_password(self):
        """Verify the entered password"""
        password = self.password_entry.get()
        if self.perm_manager.authenticator(self.username, password):
            self.destroy()
            self.on_success_callback(self.username)
        else:
            ctkmb.CTkMessagebox(
                title="Error",
                message="Invalid password!",
                icon="cancel"
            )
            self.password_entry.delete(0, ctk.END)
            self.password_entry.focus()


class UserSelectFrame(ctk.CTkFrame):
    """A Netflix-style user selection screen"""
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Background image
        self.background_img = ctk.CTkImage(
            dark_image=Image.open("assets/user_select_background.png"),
            size=(1920, 1080)
        )
        self.background_label = ctk.CTkLabel(self, image=self.background_img, text="")
        self.background_label.place(x=0, y=0)
        
        # Get users from database (User objects with profile pics)
        self.users = master.perm_manager.get_user_objects()[:3]  # First 3 users

        # Logo
        self.logo = ctk.CTkLabel(
            self,
            text="SPKL",
            font=ctk.CTkFont("Broadway", size=50, weight="bold"),
            text_color="white",
            bg_color='#000001'
        )
        self.logo.place(relx=0.04, rely=0.02)
        pywinstyles.set_opacity(self.logo, color="#000001")
        
        # Title
        self.title = ctk.CTkLabel(
            self,
            text="Who's managing?",
            font=ctk.CTkFont("Tw Cen MT Condensed Extra Bold", size=80),
            text_color="white",
            bg_color='#000001'
        )
        self.title.pack(pady=(80, 10))
        pywinstyles.set_opacity(self.title, color="#000001")
        
        # Create user cards directly on self
        self.user_cards = []
        # Calculate positioning for horizontal layout
        num_users = len(self.users)
        card_width = 470  # 300 + padding
        total_width = num_users * card_width + (num_users - 1) * 40  # cards + spacing
        start_x = (1920 - total_width) / 2  # Center horizontally
        
        for i, user_obj in enumerate(self.users):
            card = self.create_user_card(self, user_obj)
            x_pos = start_x + i * (card_width + 40)
            card.place(x=x_pos, y=300)
            self.user_cards.append(card)
        
        # "Other User" button
        self.other_user_button = ctk.CTkButton(
            self,
            text="Not here?",
            command=self.show_login,
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=20),
            width=200,
            height=50,
            fg_color="transparent",
            hover_color=("#404040", "#303030"),
            border_width=2,
            border_color="white",
            bg_color='#000001'
        )
        self.other_user_button.place(x=960-100, y=850)
        pywinstyles.set_opacity(self.other_user_button, color="#000001")

        self.exit_button = ctk.CTkButton(self, text="Exit", 
                        command=master.destroy,
                        fg_color="red", bg_color="#000001",
                        text_color="black",
                        hover_color=("#E0E0E0", "#D0D0D0"),
                        font=ctk.CTkFont("Bahnschrift Condensed", size=14),
                        corner_radius=25,
                        width=100, height=50)
        self.exit_button.place(x=960-50, y=1000)
        pywinstyles.set_opacity(self.exit_button, color="#000001")
    
    def create_user_card(self, parent, user_obj):
        """Create a user profile card in its own styled frame"""
        # Main card frame - similar to dashboard cards
        card_frame = ctk.CTkFrame(
            parent,
            corner_radius=15,
            fg_color="#000000",
            bg_color="#000001",
            cursor="hand2"
        )
        pywinstyles.set_opacity(card_frame, color="#000001")
        
        # Profile image container
        image_container = ctk.CTkFrame(
            card_frame,
            width=450,
            height=450,
            fg_color="transparent",
            corner_radius=10
        )
        image_container.pack()
        image_container.pack_propagate(False)
        
        # Try to load profile picture or use letter avatar
        if user_obj.profile_pic and os.path.exists(user_obj.profile_pic):
            # Load and display profile picture
            try:
                profile_img = ctk.CTkImage(
                    Image.open(user_obj.profile_pic),
                    size=(450, 450)
                )
                profile_label = ctk.CTkLabel(
                    image_container,
                    image=profile_img,
                    text="",
                    cursor="hand2"
                )
                profile_label.place(x=0, y=0)
                profile_label.image = profile_img  # Keep reference
                
                # Bind click event to image
                profile_label.bind("<Button-1>", lambda e: self.on_user_select(user_obj.name))
                
                # Store for hover effects
                image_element = profile_label
            except Exception as e:
                # If image load fails, use letter avatar
                print(f"Failed to load profile picture for {user_obj.name}: {e}")
                image_element = self._create_letter_avatar(image_container, user_obj.name)
        else:
            # Use letter avatar
            image_element = self._create_letter_avatar(image_container, user_obj.name)
        
        # Username label
        username_label = ctk.CTkLabel(
            card_frame,
            text=user_obj.name,
            font=ctk.CTkFont("Tw Cen MT Condensed Bold", size=28),
            text_color="white",
            cursor="hand2"
        )
        username_label.pack(padx=10, pady=(5, 10))
        
        # Bind click events to all elements
        card_frame.bind("<Button-1>", lambda e: self.on_user_select(user_obj.name))
        image_container.bind("<Button-1>", lambda e: self.on_user_select(user_obj.name))
        username_label.bind("<Button-1>", lambda e: self.on_user_select(user_obj.name))
        
        # Hover effects for the card frame
        def on_enter(e):
            card_frame.configure(fg_color="#858585")  # Lighter gray on hover
        
        def on_leave(e):
            card_frame.configure(fg_color="#000000")  # Original gray
        
        card_frame.bind("<Enter>", on_enter)
        card_frame.bind("<Leave>", on_leave)
        
        return card_frame
    
    def _create_letter_avatar(self, container, username):
        """Create a letter avatar for users without profile pictures"""
        letter_label = ctk.CTkLabel(
            container,
            text=username[0].upper(),  # First letter of username
            font=ctk.CTkFont(size=120, weight="bold"),
            text_color="white",
            cursor="hand2"
        )
        letter_label.place(relx=0.5, rely=0.5, anchor="center")
        return letter_label
    
    def on_user_select(self, username):
        """Handle user card click"""
        # Show password dialog
        PasswordDialog(self, username, self.on_authentication_success)
    
    def on_authentication_success(self, username):
        """Called when authentication is successful"""
        self.master.show_main(username)
    
    def show_login(self):
        """Show the traditional login frame"""
        self.master.show_login()

