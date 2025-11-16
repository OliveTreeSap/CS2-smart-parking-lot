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
        
        # Track elevator floor state
        self.current_floor = 0
        self.floor_var = ctk.IntVar(value=0)
        
        # Sensor data popup tracking
        self.sensor_popup = None
        self.sensor_update_job = None
        
        # Operation mode tracking
        self.mode_var = ctk.StringVar(value="AUTO")
        
        # Background image
        self.background_img = ctk.CTkImage(
            dark_image=Image.open("assets/main_background.png"),
            size=(1920, 1080)
        )
        self.background_label = ctk.CTkLabel(self, image=self.background_img, text="")
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Configure grid layout for self - 2 column split layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Top bar
        self.grid_rowconfigure(1, weight=0)  # Connection bar
        self.grid_rowconfigure(2, weight=1)  # Main content (expandable)
        self.grid_rowconfigure(3, weight=0)  # Welcome message
        
        # Create UI components
        self.create_top_bar()
        self.create_connection_bar()
        self.create_isometric_view()
        self.create_control_panel()
        self.create_bottom_section()
    
    def create_top_bar(self):
        """Create the top bar with branding and logout button"""
        # Logo (directly on self, not in a frame)
        self.logo = ctk.CTkLabel(
            self,
            text="SPKL",
            font=ctk.CTkFont("Broadway", size=50, weight="bold"),
            text_color="white",
            bg_color='#000001'
        )
        # self.logo.grid(row=0, column=0, columnspan=2, padx=50, pady=(50, 20), sticky="w")
        self.logo.place(relx=0.04, rely=0.02)
        pywinstyles.set_opacity(self.logo, color="#000001")
        
        # Logout button
        self.logout_button = ctk.CTkButton(
            self,
            text="Logout",
            command=self.logout,
            font=ctk.CTkFont("Bahnschrift Condensed", size=24),
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
            font=ctk.CTkFont("Tw Cen MT Condensed Extra Bold", size=24),
            text_color="red"
        )
        self.status_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # COM Port label
        ctk.CTkLabel(
            self.connection_bar,
            text="COM port:",
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=24),
            text_color="white"
        ).grid(row=0, column=1, padx=5, pady=20, sticky="e")
        
        # COM Port dropdown
        self.port_var = ctk.StringVar(value="No ports found")
        self.port_dropdown = ctk.CTkOptionMenu(
            self.connection_bar,
            variable=self.port_var,
            values=self.get_available_ports(),
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=24),
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
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=24),
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
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=24, weight="bold"),
            width=140,
            height=40,
            fg_color=("#4CAF50", "#45a049"),
            hover_color=("#45a049", "#3d8b40")
        )
        self.connect_button.grid(row=0, padx=(5, 20), pady=20, column=4, sticky="e")
    
    def create_isometric_view(self):
        """Create the left side isometric parking lot view"""
        # Load parking lot overview image
        self.parking_lot_img = ctk.CTkImage(
            dark_image=Image.open("assets/parking_lot_overview.png"),
            size=(1280, 720)
        )
        
        # Create image label
        self.parking_lot_label = ctk.CTkLabel(
            self,
            image=self.parking_lot_img,
            text="",
            bg_color='#000001'
        )
        self.parking_lot_label.place(x=50, y=240)
        pywinstyles.set_opacity(self.parking_lot_label, color="#000001")
    
    def create_control_panel(self):
        """Create the right side control panel with all controls"""
        # Main control panel frame (now scrollable)
        self.control_panel = ctk.CTkFrame(
            self,
            fg_color="#757575",
            bg_color='#000001',
            corner_radius=15,
            width=490, height=720,
        )
        # self.control_panel.grid(row=2, column=2, padx=(25, 50), pady=20, sticky="nsew")
        self.control_panel.place(x=1380, y=240)
        self.control_panel.grid_propagate(False)  # Prevent child widgets from overriding width/height
        pywinstyles.set_opacity(self.control_panel, color="#000001")
        
        # Configure grid for control panel
        self.control_panel.grid_columnconfigure(0, weight=1)
        
        # Track current row for grid layout
        self.current_row = 0
        
        # Control panel header
        header = ctk.CTkLabel(
            self.control_panel,
            text="CONTROL PANEL",
            font=ctk.CTkFont("Tw Cen MT Condensed Extra Bold", size=36, weight="bold"),
            text_color="white"
        )
        header.grid(row=self.current_row, column=0, pady=(20, 10), sticky="ew")
        self.current_row += 1
        
        # Separator line
        separator = ctk.CTkFrame(self.control_panel, height=2, fg_color="white")
        separator.grid(row=self.current_row, column=0, sticky="ew", padx=40, pady=(0, 20))
        self.current_row += 1
        
        # Create mode toggle section
        self.create_mode_toggle()
        
        # Create control sections directly in control_panel
        self.create_barrier_controls()
        self.create_elevator_controls()
        self.create_rain_shelter_controls()
        self.create_light_controls()
        self.create_overview_button_in_panel()
    
    def create_mode_toggle(self):
        """Create Auto/Manual mode toggle"""
        # Mode section header
        mode_label = ctk.CTkLabel(
            self.control_panel,
            text="● Operation Mode",
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=30, weight="bold"),
            text_color="white",
            anchor="w"
        )
        mode_label.grid(row=self.current_row, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.current_row += 1
        
        # Mode toggle frame
        mode_frame = ctk.CTkFrame(self.control_panel, fg_color="transparent")
        mode_frame.grid(row=self.current_row, column=0, sticky="ew", padx=15, pady=5)
        self.current_row += 1
        
        mode_frame.grid_columnconfigure(0, weight=0)
        mode_frame.grid_columnconfigure(1, weight=1)
        
        # Mode label (shows current mode)
        self.mode_status_label = ctk.CTkLabel(
            mode_frame,
            text="AUTO",
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=24, weight="bold"),
            text_color="#4CAF50",
            width=100,
            anchor="w"
        )
        self.mode_status_label.grid(row=0, column=0, padx=(30, 20), sticky="w")
        
        # Mode switch button
        self.mode_switch = ctk.CTkSwitch(
            mode_frame,
            text="MANUAL",
            progress_color=("#FF9800", "#F57C00"),
            variable=ctk.BooleanVar(value=False),
            command=self.toggle_mode,
            width=60,
            height=28,
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=20)
        )
        self.mode_switch.grid(row=0, column=1, sticky="w")
        
        # Add spacing after mode section
        spacing = ctk.CTkFrame(self.control_panel, height=10, fg_color="transparent")
        spacing.grid(row=self.current_row, column=0)
        self.current_row += 1
    
    def create_barrier_controls(self):
        """Create barrier IN/OUT toggle controls"""
        # Barriers section header
        barrier_label = ctk.CTkLabel(
            self.control_panel,
            text="● Barriers",
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=30, weight="bold"),
            text_color="white",
            anchor="w"
        )
        barrier_label.grid(row=self.current_row, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.current_row += 1
        
        # IN Barrier control
        in_frame = ctk.CTkFrame(self.control_panel, fg_color="transparent")
        in_frame.grid(row=self.current_row, column=0, sticky="ew", padx=15, pady=5)
        self.current_row += 1
        
        in_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            in_frame,
            text="IN",
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=24),
            text_color="white",
            width=80,
            anchor="w"
        ).grid(row=0, column=0, padx=(30, 20), sticky="w")
        
        self.barrier_in_var = ctk.BooleanVar(value=False)
        self.barrier_in_switch = ctk.CTkSwitch(
            in_frame,
            text="ON" if self.barrier_in_var.get() else "OFF",
            progress_color=("#4CAF50", "#45a049"),
            variable=self.barrier_in_var,
            command=self.toggle_barrier_in,
            width=60,
            height=28,
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=20)
        )
        self.barrier_in_switch.grid(row=0, column=1, sticky="w")
        
        # OUT Barrier control
        out_frame = ctk.CTkFrame(self.control_panel, fg_color="transparent")
        out_frame.grid(row=self.current_row, column=0, sticky="ew", padx=15, pady=5)
        self.current_row += 1
        
        out_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            out_frame,
            text="OUT",
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=24),
            text_color="white",
            width=80,
            anchor="w"
        ).grid(row=0, column=0, padx=(30, 20), sticky="w")
        
        self.barrier_out_var = ctk.BooleanVar(value=False)
        self.barrier_out_switch = ctk.CTkSwitch(
            out_frame,
            text="ON" if self.barrier_out_var.get() else "OFF",
            progress_color=("#4CAF50", "#45a049"),
            variable=self.barrier_out_var,
            command=self.toggle_barrier_out,
            width=60,
            height=28,
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=20)
        )
        self.barrier_out_switch.grid(row=0, column=1, sticky="w")
    
    def create_elevator_controls(self):
        """Create elevator floor selection radio buttons"""
        # Elevator section header
        elevator_label = ctk.CTkLabel(
            self.control_panel,
            text="● Elevator",
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=30, weight="bold"),
            text_color="white",
            anchor="w"
        )
        elevator_label.grid(row=self.current_row, column=0, sticky="ew", padx=10, pady=(20, 5))
        self.current_row += 1
        
        # Radio buttons for floors
        floors = [
            ("Ground floor", 0),
            ("1st floor", 1),
            ("2nd floor", 2)
        ]
        
        for floor_name, floor_num in floors:
            radio_btn = ctk.CTkRadioButton(
                self.control_panel,
                text=floor_name,
                fg_color=("#4CAF50", "#45a049"),
                variable=self.floor_var,
                value=floor_num,
                command=lambda f=floor_num: self.select_floor(f),
                font=ctk.CTkFont("Bahnschrift Light Condensed", size=24),
                text_color="white"
            )
            radio_btn.grid(row=self.current_row, column=0, sticky="w", padx=40, pady=5)
            self.current_row += 1
    
    def create_rain_shelter_controls(self):
        """Create rain shelter toggle control"""
        # Rain shelter section header
        shelter_label = ctk.CTkLabel(
            self.control_panel,
            text="● Rain shelter",
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=30, weight="bold"),
            text_color="white",
            anchor="w"
        )
        shelter_label.grid(row=self.current_row, column=0, sticky="ew", padx=10, pady=(20, 5))
        self.current_row += 1
        
        # Rain shelter toggle
        shelter_frame = ctk.CTkFrame(self.control_panel, fg_color="transparent")
        shelter_frame.grid(row=self.current_row, column=0, sticky="ew", padx=30, pady=5)
        self.current_row += 1
        
        self.rain_shelter_var = ctk.BooleanVar(value=False)
        self.rain_shelter_switch = ctk.CTkSwitch(
            shelter_frame,
            text="OFF",
            progress_color=("#4CAF50", "#45a049"),
            variable=self.rain_shelter_var,
            command=self.toggle_rain_shelter,
            width=60,
            height=28,
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=20)
        )
        self.rain_shelter_switch.grid(row=0, column=0, padx=15, sticky="w")
    
    def create_light_controls(self):
        """Create light toggle control"""
        # Light section header
        light_label = ctk.CTkLabel(
            self.control_panel,
            text="● Lights",
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=30, weight="bold"),
            text_color="white",
            anchor="w"
        )
        light_label.grid(row=self.current_row, column=0, sticky="ew", padx=10, pady=(20, 5))
        self.current_row += 1
        
        # Light toggle
        light_frame = ctk.CTkFrame(self.control_panel, fg_color="transparent")
        light_frame.grid(row=self.current_row, column=0, sticky="ew", padx=30, pady=5)
        self.current_row += 1
        
        self.light_var = ctk.BooleanVar(value=False)
        self.light_switch = ctk.CTkSwitch(
            light_frame,
            text="OFF",
            progress_color=("#4CAF50", "#45a049"),
            variable=self.light_var,
            command=self.toggle_light,
            width=60,
            height=28,
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=20)
        )
        self.light_switch.grid(row=0, column=0, padx=15, sticky="w")
    
    def create_overview_button_in_panel(self):
        """Create overview button at bottom of control panel"""
        # Overview button (moved from bottom section)
        self.overview_button = ctk.CTkButton(
            self.control_panel,
            text="Sensor data",
            command=self.show_sensor_data,
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=30, weight="bold"),
            width=200,
            height=45,
            fg_color=("#505050", "#404040"),
            hover_color=("#606060", "#505050"),
            corner_radius=10
        )
        self.overview_button.grid(row=self.current_row, column=0, pady=(30, 10))
        self.current_row += 1
    
    def create_bottom_section(self):
        """Create the welcome message"""
        # Welcome message
        self.welcome_label = ctk.CTkLabel(
            self,
            text="WELCOME BACK, KHANH",
            font=ctk.CTkFont("Tw Cen MT Condensed Extra Bold", size=72),
            text_color="white",
            bg_color='#000001'
        )
        self.welcome_label.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 20))
        pywinstyles.set_opacity(self.welcome_label, color="#000001")
    
    # Control handler methods
    def toggle_mode(self):
        """Toggle between AUTO and MANUAL mode"""
        is_manual = self.mode_switch.get()
        
        if is_manual:
            # Switch to MANUAL mode
            self.mode_var.set("MANUAL")
            self.mode_status_label.configure(text="MANUAL", text_color="#FF9800")
            self.send_command("MODE_MANUAL")
            print("Switched to MANUAL mode")
        else:
            # Switch to AUTO mode
            self.mode_var.set("AUTO")
            self.mode_status_label.configure(text="AUTO", text_color="#4CAF50")
            self.send_command("MODE_AUTO")
            print("Switched to AUTO mode")
    
    def toggle_barrier_in(self):
        """Toggle IN barrier"""
        state = self.barrier_in_var.get()
        command = "BARRIER_IN_OPEN" if state else "BARRIER_IN_CLOSE"
        self.barrier_in_switch.configure(text="ON" if state else "OFF")
        self.send_command(command)
    
    def toggle_barrier_out(self):
        """Toggle OUT barrier"""
        state = self.barrier_out_var.get()
        command = "BARRIER_OUT_OPEN" if state else "BARRIER_OUT_CLOSE"
        self.barrier_out_switch.configure(text="ON" if state else "OFF")
        self.send_command(command)
    
    def select_floor(self, floor_num):
        """Send elevator to selected floor"""
        self.current_floor = floor_num
        command = f"ELEVATOR_FLOOR_{floor_num}"
        self.send_command(command)
    
    def toggle_rain_shelter(self):
        """Toggle rain shelter"""
        state = self.rain_shelter_var.get()
        command = "RAIN_SHELTER_ON" if state else "RAIN_SHELTER_OFF"
        self.rain_shelter_switch.configure(text="ON" if state else "OFF")
        self.send_command(command)
    
    def toggle_light(self):
        """Toggle light system"""
        state = self.light_var.get()
        command = "LED_ALL_ON" if state else "LED_ALL_OFF"
        self.light_switch.configure(text="ON" if state else "OFF")
        self.send_command(command)
    
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
        # Close sensor popup if open
        if self.sensor_popup is not None:
            self.close_sensor_popup()
        
        # Disconnect Arduino before logging out
        if self.arduino.is_connected():
            self.disconnect_arduino()
        
        self.master.show_login()
    
    def show_sensor_data(self):
        """Display sensor data in a popup window"""
        # Check if Arduino is connected
        if not self.arduino.is_connected():
            self.show_error("Arduino is not connected. Please connect first.")
            return
        
        # If popup already exists, bring it to front
        if self.sensor_popup is not None and self.sensor_popup.winfo_exists():
            self.sensor_popup.focus()
            return
        
        # Create popup window
        self.sensor_popup = ctk.CTkToplevel(self)
        self.sensor_popup.title("Sensor Data Overview")
        self.sensor_popup.geometry("600x400")
        self.sensor_popup.resizable(False, False)
        
        # Center the window
        self.sensor_popup.update_idletasks()
        x = (self.sensor_popup.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.sensor_popup.winfo_screenheight() // 2) - (400 // 2)
        self.sensor_popup.geometry(f"600x400+{x}+{y}")
        
        # Make it stay on top initially
        self.sensor_popup.attributes('-topmost', True)
        self.sensor_popup.after(100, lambda: self.sensor_popup.attributes('-topmost', False))
        
        # Header
        header = ctk.CTkLabel(
            self.sensor_popup,
            text="SENSOR DATA",
            font=ctk.CTkFont("Tw Cen MT Condensed Extra Bold", size=32, weight="bold"),
            text_color="white"
        )
        header.pack(pady=(20, 10))
        
        # Separator
        separator = ctk.CTkFrame(self.sensor_popup, height=2, fg_color="gray")
        separator.pack(fill="x", padx=40, pady=(0, 20))
        
        # Data display area (using CTkTextbox for better formatting)
        self.sensor_data_display = ctk.CTkTextbox(
            self.sensor_popup,
            font=ctk.CTkFont("Consolas", size=18),
            width=540,
            height=220,
            fg_color=("#2b2b2b", "#1a1a1a"),
            text_color="white",
            wrap="none"
        )
        self.sensor_data_display.pack(pady=10, padx=30)
        
        # Close button
        close_button = ctk.CTkButton(
            self.sensor_popup,
            text="Close",
            command=self.close_sensor_popup,
            font=ctk.CTkFont("Bahnschrift Light Condensed", size=20, weight="bold"),
            width=150,
            height=40,
            fg_color=("#f44336", "#da190b"),
            hover_color=("#da190b", "#b71c1c")
        )
        close_button.pack(pady=(10, 20))
        
        # Bind window close event
        self.sensor_popup.protocol("WM_DELETE_WINDOW", self.close_sensor_popup)
        
        # Start updating sensor data
        self.update_sensor_display()
    
    def update_sensor_display(self):
        """Continuously read and update sensor data display"""
        # Check if popup still exists
        if self.sensor_popup is None or not self.sensor_popup.winfo_exists():
            self.sensor_update_job = None
            return
        
        # Read available data from Arduino buffer
        # With Arduino sending at reasonable rate (100-200ms), read a few times
        # to ensure we get the latest data
        data_read = False
        for _ in range(10):  # Read up to 10 times to get latest data
            if self.arduino.read_data():
                data_read = True
            else:
                break  # No more data available
        
        # Get all sensor values
        sensor_values = self.arduino.get_all_values()
        
        # Format the data for display
        if sensor_values:
            display_text = ""
            for label, value in sensor_values.items():
                display_text += f"{label}: {value}\n"
            
            # Update the textbox
            self.sensor_data_display.delete("1.0", "end")
            self.sensor_data_display.insert("1.0", display_text)
        else:
            # No data available yet
            self.sensor_data_display.delete("1.0", "end")
            self.sensor_data_display.insert("1.0", "Waiting for sensor data...\n\nMake sure Arduino is:\n1. Connected\n2. Sending sensor data")
        
        # Schedule next update (200ms for smooth updates)
        self.sensor_update_job = self.after(200, self.update_sensor_display)
    
    def close_sensor_popup(self):
        """Close the sensor data popup and stop updates"""
        # Cancel scheduled updates
        if self.sensor_update_job is not None:
            self.after_cancel(self.sensor_update_job)
            self.sensor_update_job = None
        
        # Close popup window
        if self.sensor_popup is not None and self.sensor_popup.winfo_exists():
            self.sensor_popup.destroy()
        
        self.sensor_popup = None

