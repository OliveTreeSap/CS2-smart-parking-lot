import customtkinter as ctk
import pywinstyles
from PIL import Image
from arduino_comm import ArduinoController


class MainFrameDashboard(ctk.CTkFrame):
    """A modern dashboard frame for managing building systems"""
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Initialize Arduino controller
        self.arduino = ArduinoController()
        self.current_user = ""
        
        # Track detail panel state
        self.detail_overlay = None
        self.detail_panel = None
        
        # Background image
        self.background_img = ctk.CTkImage(
            dark_image=Image.open("assets/main_background.png"),
            size=(1920, 1080)
        )
        self.background_label = ctk.CTkLabel(self, image=self.background_img, text="")
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Configure grid layout for self
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Top bar
        self.grid_rowconfigure(1, weight=0)  # Connection bar
        self.grid_rowconfigure(2, weight=1)  # Cards (expandable)
        self.grid_rowconfigure(3, weight=0)  # Overview button
        self.grid_rowconfigure(4, weight=0)  # Welcome message
        
        # Create UI components
        self.create_top_bar()
        self.create_connection_bar()
        self.create_module_cards()
        self.create_bottom_section()
    
    def create_top_bar(self):
        """Create the top bar with branding and logout button"""
        # Logo (directly on self, not in a frame)
        self.company_name = ctk.CTkLabel(
            self,
            text="SPKL",
            font=ctk.CTkFont("Broadway", size=50, weight="bold"),
            text_color="white",
            bg_color='#000001'
        )
        self.company_name.grid(row=0, column=0, columnspan=2, padx=50, pady=(50, 20), sticky="w")
        pywinstyles.set_opacity(self.company_name, color="#000001")
        
        # Logout button
        self.logout_button = ctk.CTkButton(
            self,
            text="Logout",
            command=self.logout,
            font=ctk.CTkFont(size=24, weight="bold"),
            fg_color="transparent",
            text_color="white",
            hover_color=("#404040", "#303030"),
            width=120,
            height=40,
            border_width=2,
            border_color="white",
            bg_color='#000001'
        )
        self.logout_button.grid(row=0, column=2, padx=70, pady=(50, 20), sticky="e")
        pywinstyles.set_opacity(self.logout_button, color="#000001")
    
    def create_connection_bar(self):
        """Create the connection interface bar"""
        # Connection bar frame
        self.connection_bar = ctk.CTkFrame(
            self,
            fg_color="#757575", bg_color="#000001",
            corner_radius=15,
            height=80
        )
        self.connection_bar.grid(row=1, column=0, columnspan=3, sticky="ew", padx=50, pady=(10, 20))
        self.connection_bar.grid_columnconfigure(0, weight=1)
        pywinstyles.set_opacity(self.connection_bar, color="#000001")
        
        # Status indicator
        self.status_label = ctk.CTkLabel(
            self.connection_bar,
            text="● Disconnected",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="red"
        )
        self.status_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # COM Port label
        ctk.CTkLabel(
            self.connection_bar,
            text="COM port:",
            font=ctk.CTkFont(size=24),
            text_color="white"
        ).grid(row=0, column=1, padx=5, pady=20, sticky="e")
        
        # COM Port dropdown
        self.port_var = ctk.StringVar(value="No ports found")
        self.port_dropdown = ctk.CTkOptionMenu(
            self.connection_bar,
            variable=self.port_var,
            values=self.get_available_ports(),
            font=ctk.CTkFont(size=24),
            width=250,
            height=40,
            fg_color=("#505050", "#404040"),
            button_color=("#606060", "#505050")
        )
        self.port_dropdown.grid(row=0, column=2, padx=5, pady=20, sticky="e")
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.connection_bar,
            text="⟳",
            command=self.refresh_ports,
            font=ctk.CTkFont(size=24),
            width=50,
            height=40,
            fg_color=("#505050", "#404040"),
            hover_color=("#606060", "#505050")
        )
        self.refresh_button.grid(row=0, column=3, padx=5, pady=20, sticky="e")
        
        # Connect/Disconnect button
        self.connect_button = ctk.CTkButton(
            self.connection_bar,
            text="Connect",
            command=self.toggle_connection,
            font=ctk.CTkFont(size=24, weight="bold"),
            width=140,
            height=40,
            fg_color=("#4CAF50", "#45a049"),
            hover_color=("#45a049", "#3d8b40")
        )
        self.connect_button.grid(row=0, padx=(5, 20), pady=20, column=4, sticky="e")
    
    def create_module_cards(self):
        """Create the three module cards (Barriers, Elevator, LED)"""
        # Load images
        self.barriers_img = ctk.CTkImage(
            dark_image=Image.open("assets/gates.jpg"),
            size=(450, 450)
        )
        self.elevator_img = ctk.CTkImage(
            dark_image=Image.open("assets/elevator.jpg"),
            size=(450, 450)
        )
        self.led_img = ctk.CTkImage(
            dark_image=Image.open("assets/lights.jpg"),
            size=(450, 450)
        )
        
        # Card configurations
        cards = [
            {"name": "Barriers", "image": self.barriers_img, "column": 0},
            {"name": "Elevator", "image": self.elevator_img, "column": 1},
            {"name": "LED", "image": self.led_img, "column": 2}
        ]
        
        for card_info in cards:
            self.create_card(
                card_info["name"],
                card_info["image"],
                card_info["column"]
            )
    
    def create_card(self, title, image, column):
        """Create a single module card"""
        # Card frame
        card_frame = ctk.CTkFrame(
            self,
            corner_radius=15,
            fg_color="#757575", bg_color="#000001",
            cursor="hand2"
        )
        card_frame.grid(row=2, column=column, padx=50, pady=20, sticky="nsew")
        pywinstyles.set_opacity(card_frame, color="#000001")
        
        # Make card clickable
        card_frame.bind("<Button-1>", lambda e, t=title: self.show_detail_panel(t))
        
        # Image
        img_label = ctk.CTkLabel(
            card_frame,
            image=image,
            text="",
            cursor="hand2"
        )
        img_label.pack(padx=10, pady=(10, 5), expand=True, fill="both")
        img_label.bind("<Button-1>", lambda e, t=title: self.show_detail_panel(t))
        
        # Title
        title_label = ctk.CTkLabel(
            card_frame,
            text=title,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white",
            cursor="hand2"
        )
        title_label.pack(padx=10, pady=(5, 10))
        title_label.bind("<Button-1>", lambda e, t=title: self.show_detail_panel(t))
    
    def create_bottom_section(self):
        """Create the Overview button and welcome message"""
        # Overview button
        self.overview_button = ctk.CTkButton(
            self,
            text="Overview",
            font=ctk.CTkFont(size=24, weight="bold"),
            width=200,
            height=50,
            fg_color=("#505050", "#404040"),
            hover_color=("#606060", "#505050"),
            corner_radius=25,
            bg_color='#000001'
        )
        self.overview_button.grid(row=3, column=0, columnspan=3, padx=20, pady=(10, 20))
        pywinstyles.set_opacity(self.overview_button, color="#000001")
        
        # Welcome message
        self.welcome_label = ctk.CTkLabel(
            self,
            text="WELCOME BACK, KHANH",
            font=ctk.CTkFont(size=72, weight="bold"),
            text_color="white",
            bg_color='#000001'
        )
        self.welcome_label.grid(row=4, column=0, columnspan=3, padx=20, pady=(10, 20))
        pywinstyles.set_opacity(self.welcome_label, color="#000001")
    
    def show_detail_panel(self, module_name):
        """Show detail panel overlay for a specific module"""
        # Create semi-transparent overlay
        self.detail_overlay = ctk.CTkFrame(
            self,
            fg_color=("#000000", "#000000")
        )
        self.detail_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        pywinstyles.set_opacity(self.detail_overlay, 0.7)
        
        # Make overlay dismissible
        self.detail_overlay.bind("<Button-1>", lambda e: self.close_detail_panel())
        
        # Create detail panel
        self.detail_panel = ctk.CTkFrame(
            self.detail_overlay,
            fg_color=("#2b2b2b", "#1e1e1e"),
            corner_radius=20,
            border_width=2,
            border_color="white"
        )
        self.detail_panel.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.5, relheight=0.5)
        
        # Prevent clicks on panel from closing it
        self.detail_panel.bind("<Button-1>", lambda e: "break")
        
        # Close button
        close_btn = ctk.CTkButton(
            self.detail_panel,
            text="✕",
            command=self.close_detail_panel,
            font=ctk.CTkFont(size=24, weight="bold"),
            width=50,
            height=50,
            fg_color="transparent",
            hover_color=("#404040", "#303030"),
            text_color="white"
        )
        close_btn.place(relx=0.95, rely=0.02, anchor="ne")
        
        # Panel title
        title = ctk.CTkLabel(
            self.detail_panel,
            text=f"{module_name} Control",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="white"
        )
        title.place(relx=0.5, rely=0.08, anchor="center")
        
        # Module-specific controls
        self.create_module_controls(module_name, self.detail_panel)
    
    def create_module_controls(self, module_name, parent):
        """Create controls specific to each module"""
        controls_frame = ctk.CTkFrame(parent, fg_color="transparent")
        controls_frame.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.9, relheight=0.75)
        
        if module_name == "Barriers":
            # Barrier controls
            ctk.CTkLabel(
                controls_frame,
                text="Control the parking barrier gates",
                font=ctk.CTkFont(size=18),
                text_color="gray"
            ).pack(pady=20)
            
            ctk.CTkButton(
                controls_frame,
                text="Open Barrier",
                command=lambda: self.send_command("BARRIER_OPEN"),
                font=ctk.CTkFont(size=20, weight="bold"),
                width=300,
                height=60,
                fg_color=("#4CAF50", "#45a049")
            ).pack(pady=15)
            
            ctk.CTkButton(
                controls_frame,
                text="Close Barrier",
                command=lambda: self.send_command("BARRIER_CLOSE"),
                font=ctk.CTkFont(size=20, weight="bold"),
                width=300,
                height=60,
                fg_color=("#f44336", "#da190b")
            ).pack(pady=15)
            
            ctk.CTkButton(
                controls_frame,
                text="Stop Barrier",
                command=lambda: self.send_command("BARRIER_STOP"),
                font=ctk.CTkFont(size=20, weight="bold"),
                width=300,
                height=60,
                fg_color=("#FF9800", "#F57C00")
            ).pack(pady=15)
            
        elif module_name == "Elevator":
            # Elevator controls
            ctk.CTkLabel(
                controls_frame,
                text="Control the building elevator",
                font=ctk.CTkFont(size=18),
                text_color="gray"
            ).pack(pady=20)
            
            ctk.CTkButton(
                controls_frame,
                text="Move Up",
                command=lambda: self.send_command("ELEVATOR_UP"),
                font=ctk.CTkFont(size=20, weight="bold"),
                width=300,
                height=60,
                fg_color=("#2196F3", "#0b7dda")
            ).pack(pady=15)
            
            ctk.CTkButton(
                controls_frame,
                text="Move Down",
                command=lambda: self.send_command("ELEVATOR_DOWN"),
                font=ctk.CTkFont(size=20, weight="bold"),
                width=300,
                height=60,
                fg_color=("#9C27B0", "#7B1FA2")
            ).pack(pady=15)
            
            ctk.CTkButton(
                controls_frame,
                text="Stop Elevator",
                command=lambda: self.send_command("ELEVATOR_STOP"),
                font=ctk.CTkFont(size=20, weight="bold"),
                width=300,
                height=60,
                fg_color=("#FF9800", "#F57C00")
            ).pack(pady=15)
            
        elif module_name == "LED":
            # LED controls
            ctk.CTkLabel(
                controls_frame,
                text="Control the building lighting system",
                font=ctk.CTkFont(size=18),
                text_color="gray"
            ).pack(pady=20)
            
            # LED toggles
            self.led_switches = {}
            for i in range(1, 6):
                switch_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
                switch_frame.pack(pady=10, fill="x")
                
                ctk.CTkLabel(
                    switch_frame,
                    text=f"LED {i}:",
                    font=ctk.CTkFont(size=18),
                    text_color="white"
                ).pack(side="left", padx=20)
                
                switch_var = ctk.BooleanVar(value=False)
                switch = ctk.CTkSwitch(
                    switch_frame,
                    text="",
                    variable=switch_var,
                    command=lambda num=i, var=switch_var: self.toggle_led(num, var),
                    width=80,
                    height=35
                )
                switch.pack(side="left", padx=20)
                self.led_switches[i] = switch_var
            
            # All on/off buttons
            btn_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
            btn_frame.pack(pady=20)
            
            ctk.CTkButton(
                btn_frame,
                text="All ON",
                command=self.all_leds_on,
                font=ctk.CTkFont(size=18, weight="bold"),
                width=150,
                height=50,
                fg_color=("#4CAF50", "#45a049")
            ).pack(side="left", padx=10)
            
            ctk.CTkButton(
                btn_frame,
                text="All OFF",
                command=self.all_leds_off,
                font=ctk.CTkFont(size=18, weight="bold"),
                width=150,
                height=50,
                fg_color=("#f44336", "#da190b")
            ).pack(side="left", padx=10)
    
    def close_detail_panel(self):
        """Close the detail panel overlay"""
        if self.detail_overlay:
            self.detail_overlay.destroy()
            self.detail_overlay = None
        if self.detail_panel:
            self.detail_panel = None
    
    def get_available_ports(self):
        """Get list of available COM ports"""
        ports = ArduinoController.list_available_ports()
        return ports if ports else ["No ports found"]
    
    def refresh_ports(self):
        """Refresh the list of available COM ports"""
        ports = self.get_available_ports()
        self.port_dropdown.configure(values=ports)
        if ports and ports[0] != "No ports found":
            self.port_var.set(ports[0])
        else:
            self.port_var.set("No ports found")
    
    def toggle_connection(self):
        """Connect or disconnect from Arduino"""
        if self.arduino.is_connected():
            self.disconnect_arduino()
        else:
            self.connect_arduino()
    
    def connect_arduino(self):
        """Connect to Arduino on selected port"""
        port = self.port_var.get()
        
        if port == "Select Port" or port == "No ports found":
            self.show_error("Please select a valid COM port")
            return
        
        try:
            baudrate = 115200  # Default baudrate
            
            if self.arduino.connect(port, baudrate):
                # Update UI
                self.status_label.configure(
                    text="● Connected",
                    text_color="green"
                )
                self.connect_button.configure(
                    text="Disconnect",
                    fg_color=("#f44336", "#da190b"),
                    hover_color=("#da190b", "#b71c1c")
                )
                
                # Disable port selection
                self.port_dropdown.configure(state="disabled")
                self.refresh_button.configure(state="disabled")
            else:
                self.show_error(f"Failed to connect to {port}")
        
        except Exception as e:
            self.show_error(f"Connection error: {str(e)}")
    
    def disconnect_arduino(self):
        """Disconnect from Arduino"""
        self.arduino.disconnect()
        
        # Update UI
        self.status_label.configure(
            text="● Disconnected",
            text_color="red"
        )
        self.connect_button.configure(
            text="Connect",
            fg_color=("#4CAF50", "#45a049"),
            hover_color=("#45a049", "#3d8b40")
        )
        
        # Enable port selection
        self.port_dropdown.configure(state="normal")
        self.refresh_button.configure(state="normal")
    
    def send_command(self, command):
        """Send a command to the Arduino"""
        if not self.arduino.is_connected():
            self.show_error("Not connected to Arduino")
            return
        
        if self.arduino.write(command):
            # Show brief feedback
            print(f"Command sent: {command}")
        else:
            self.show_error("Failed to send command")
    
    def toggle_led(self, led_num, var):
        """Toggle LED on/off"""
        if not self.arduino.is_connected():
            self.show_error("Not connected to Arduino")
            var.set(not var.get())
            return
        
        state = "ON" if var.get() else "OFF"
        command = f"LED_{led_num}_{state}"
        self.send_command(command)
    
    def all_leds_on(self):
        """Turn all LEDs on"""
        if not self.arduino.is_connected():
            self.show_error("Not connected to Arduino")
            return
        
        for i in range(1, 6):
            self.send_command(f"LED_{i}_ON")
            if i in self.led_switches:
                self.led_switches[i].set(True)
    
    def all_leds_off(self):
        """Turn all LEDs off"""
        if not self.arduino.is_connected():
            self.show_error("Not connected to Arduino")
            return
        
        for i in range(1, 6):
            self.send_command(f"LED_{i}_OFF")
            if i in self.led_switches:
                self.led_switches[i].set(False)
    
    def show_error(self, message):
        """Display an error message"""
        # Simple error display - could use CTkMessagebox
        print(f"Error: {message}")
    
    def update_welcome(self, username):
        """Update the welcome message with the logged-in username"""
        self.current_user = username
        self.welcome_label.configure(text=f"WELCOME BACK, {username.upper()}")
    
    def logout(self):
        """Handle logout and return to login screen"""
        # Disconnect Arduino before logging out
        if self.arduino.is_connected():
            self.disconnect_arduino()
        
        # Close any open detail panels
        self.close_detail_panel()
        
        self.master.show_login()

