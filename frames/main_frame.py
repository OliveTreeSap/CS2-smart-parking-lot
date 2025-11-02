import customtkinter as ctk
import CTkMessagebox as ctkmb
from arduino_comm import ArduinoController
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class MainFrame(ctk.CTkFrame):
    """A class that handles the main user interface which displays information from the Arduino"""
    
    # Configuration constants
    NUM_LEDS = 5
    MAX_HISTORY = 100
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        # Initialize Arduino controller
        self.arduino = ArduinoController()
        self.update_job = None  # Store the after() job ID for cleanup
        self.sensor_labels = {}  # Store sensor value labels for updating
        self.sensor_history = {}  # Store sensor history for charts
        self.led_checkboxes = {}  # Store LED checkbox widgets
        self.motor_var = ctk.StringVar(value="STOP")  # Motor control state

        # Expands the widgets to fit the frame
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
            font=ctk.CTkFont(size=14),
            fg_color="red",
            width=120
        )
        self.logout_button.grid(row=0, column=1, padx=40, pady=20, sticky="e")

        # Arduino contents
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(2, weight=1)
        
        # Arduino connection
        self.connection_frame = ctk.CTkFrame(self.content_frame)
        self.connection_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=20)
        self.connection_frame.grid_columnconfigure(1, weight=1)
        
        # Connection status
        self.status_label = ctk.CTkLabel(
            self.connection_frame,
            text="● Disconnected",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="red"
        )
        self.status_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.connection_frame.grid_columnconfigure(0, weight=1)
        
        # COM Port combobox
        ctk.CTkLabel(
            self.connection_frame,
            text="COM Port:",
            font=ctk.CTkFont(size=14)
        ).grid(row=0, column=1, padx=(20, 5), pady=10, sticky="e")
        
        self.port_var = ctk.StringVar(value="Select Port")
        self.port_dropdown = ctk.CTkOptionMenu(
            self.connection_frame,
            variable=self.port_var,
            values=self.get_available_ports(),
            font=ctk.CTkFont(size=14),
            width=150
        )
        self.port_dropdown.grid(row=0, column=2, padx=5, pady=10)
        
        # Refresh ports button
        self.refresh_button = ctk.CTkButton(
            self.connection_frame,
            text="⟳",
            command=self.refresh_ports,
            font=ctk.CTkFont(size=14),
            width=40
        )
        self.refresh_button.grid(row=0, column=3, padx=5, pady=10)
        
        # Baudrate combobox
        ctk.CTkLabel(
            self.connection_frame,
            text="Baudrate:",
            font=ctk.CTkFont(size=14)
        ).grid(row=0, column=4, padx=(20, 5), pady=10, sticky="e")
        
        self.baudrate_var = ctk.StringVar(value="115200")
        self.baudrate_dropdown = ctk.CTkOptionMenu(
            self.connection_frame,
            variable=self.baudrate_var,
            values=["9600", "19200", "38400", "57600", "115200"],
            font=ctk.CTkFont(size=14),
            width=120
        )
        self.baudrate_dropdown.grid(row=0, column=5, padx=5, pady=10)
        
        # Connect/Disconnect button
        self.connect_button = ctk.CTkButton(
            self.connection_frame,
            text="Connect",
            command=self.toggle_connection,
            font=ctk.CTkFont(size=14),
            width=120,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.connect_button.grid(row=0, column=6, padx=20, pady=10)
        
        # Command Input Section
        self.command_frame = ctk.CTkFrame(self.content_frame)
        self.command_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.command_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.command_frame,
            text="Send Command:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.command_entry = ctk.CTkEntry(
            self.command_frame,
            placeholder_text="Enter command to send to Arduino...",
            font=ctk.CTkFont(size=14),
            width=490
        )
        self.command_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.command_entry.bind('<Return>', lambda e: self.send_command())
        
        self.send_button = ctk.CTkButton(
            self.command_frame,
            text="Send",
            command=self.send_command,
            font=ctk.CTkFont(size=14),
            width=120,
            state="disabled"
        )
        self.send_button.grid(row=0, column=2, padx=20, pady=10)
        
        # Sensor Data Display Section - Split Layout
        self.sensor_frame = ctk.CTkFrame(self.content_frame)
        self.sensor_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.sensor_frame.grid_columnconfigure(0, weight=12)
        self.sensor_frame.grid_columnconfigure(1, weight=1)
        self.sensor_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel for sensors data and data chart
        self.left_panel = ctk.CTkFrame(self.sensor_frame)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.left_panel.grid_rowconfigure(1, weight=1)  # Sensor scroll expands
        self.left_panel.grid_rowconfigure(2, weight=0)  # Chart frame fixed size
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Left panel title
        ctk.CTkLabel(
            self.left_panel,
            text="Sensor Data & Charts",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Scrollable frame for sensors only
        self.sensor_scroll = ctk.CTkScrollableFrame(self.left_panel)
        self.sensor_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Chart frame at bottom of left panel (stretched horizontally)
        self.chart_frame = ctk.CTkFrame(self.left_panel)
        self.chart_frame.grid(row=2, column=0, sticky="ew", padx=(0,70), pady=(0, 10))
        
        # Initialize matplotlib chart
        self.figure = None
        self.canvas = None
        self.ax = None
        self.init_chart()
        
        # Raw data display at very bottom of left panel
        self.raw_data_label = ctk.CTkLabel(
            self.left_panel,
            text="Raw Data: (none)",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=400,
            justify="left"
        )
        self.raw_data_label.grid(row=3, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Right panel used for leds and motor controls
        self.right_panel = ctk.CTkFrame(self.sensor_frame)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.right_panel.grid_rowconfigure(0, weight=1)  # Upper section (LED controls)
        self.right_panel.grid_rowconfigure(1, weight=1)  # Lower section (Motor controls)
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        # Upper right frame for LEDs control
        self.led_control_frame = ctk.CTkFrame(self.right_panel)
        self.led_control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=(5, 2.5))
        self.led_control_frame.grid_rowconfigure(1, weight=1)
        self.led_control_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.led_control_frame,
            text="LED Controls",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Scrollable frame for LED checkboxes
        self.led_scroll = ctk.CTkScrollableFrame(self.led_control_frame)
        self.led_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        # Create LED checkboxes dynamically
        for i in range(1, self.NUM_LEDS + 1):
            led_var = ctk.BooleanVar(value=False)
            checkbox = ctk.CTkCheckBox(
                self.led_scroll,
                text=f"LED {i}",
                variable=led_var,
                command=lambda led_num=i, var=led_var: self.toggle_led(led_num, var),
                font=ctk.CTkFont(size=14)
            )
            checkbox.pack(anchor="w", padx=10, pady=5)
            self.led_checkboxes[i] = {"var": led_var, "widget": checkbox}
        
        # Lower right frame for motor controll
        self.motor_control_frame = ctk.CTkFrame(self.right_panel)
        self.motor_control_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(2.5, 5))
        self.motor_control_frame.grid_rowconfigure(1, weight=1)
        self.motor_control_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.motor_control_frame,
            text="Motor Controls",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        # Scrollable frame for motor radio buttons
        self.motor_scroll = ctk.CTkScrollableFrame(self.motor_control_frame)
        self.motor_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        # Create motor control radio buttons
        motor_options = [
            ("Forward", "MOTOR_FORWARD"),
            ("Reverse", "MOTOR_REVERSE"),
            ("Stop", "MOTOR_STOP")
        ]
        
        for label, command in motor_options:
            radio = ctk.CTkRadioButton(
                self.motor_scroll,
                text=label,
                variable=self.motor_var,
                value=command,
                command=lambda cmd=command: self.send_motor_command(cmd),
                font=ctk.CTkFont(size=14)
            )
            radio.pack(anchor="w", padx=10, pady=5)

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
    
    def init_chart(self):
        """Initialize the matplotlib chart for sensor data visualization"""
        # Create figure with dark background to match CustomTkinter theme
        self.figure = Figure(figsize=(6, 4), dpi=80, facecolor='#2b2b2b')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#1e1e1e')
        self.ax.set_xlabel('Time (samples)', color='white')
        self.ax.set_ylabel('Value', color='white')
        self.ax.set_title('Sensor Data History', color='white', fontsize=12, fontweight='bold')
        self.ax.tick_params(colors='white')
        self.ax.grid(True, alpha=0.3, color='gray')
        
        # Adjust layout to prevent label cutoff
        self.figure.tight_layout()
        
        # Create canvas and embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def update_charts(self):
        """Update the charts with current sensor history"""
        if not self.sensor_history or self.ax is None:
            return
        
        # Clear previous plot
        self.ax.clear()
        self.ax.set_facecolor('#1e1e1e')
        self.ax.set_xlabel('Time (samples)', color='white')
        self.ax.set_ylabel('Value', color='white')
        self.ax.set_title('Sensor Data History', color='white', fontsize=12, fontweight='bold')
        self.ax.tick_params(colors='white')
        self.ax.grid(True, alpha=0.3, color='gray')
        
        # Plot each sensor's history
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        color_idx = 0
        
        for label, history in self.sensor_history.items():
            if len(history) > 0:
                # Convert deque to list for plotting
                values = list(history)
                x_values = list(range(len(values)))
                
                # Plot with label
                self.ax.plot(x_values, values, 
                           label=label, 
                           color=colors[color_idx % len(colors)],
                           linewidth=2,
                           marker='o',
                           markersize=3)
                color_idx += 1
        
        # Add legend if there are any lines
        if self.sensor_history:
            legend = self.ax.legend(loc='upper left', 
                                   facecolor='#2b2b2b', 
                                   edgecolor='white',
                                   fontsize=9)
            for text in legend.get_texts():
                text.set_color('white')
        
        # Redraw canvas
        self.canvas.draw()
    
    def create_or_update_sensor_display(self, label: str, value):
        """Create or update a sensor display for a given label"""
        if label not in self.sensor_labels:
            # Create new sensor display
            frame = ctk.CTkFrame(self.sensor_scroll)
            frame.pack(fill="x", padx=10, pady=5)
            
            label_widget = ctk.CTkLabel(
                frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=14, weight="bold"),
                width=150,
                anchor="w"
            )
            label_widget.pack(side="left", padx=10, pady=10)
            
            value_label = ctk.CTkLabel(
                frame,
                text="---",
                font=ctk.CTkFont(size=14),
                width=150,
                anchor="w"
            )
            value_label.pack(side="left", padx=10, pady=10)
            
            self.sensor_labels[label] = value_label
            
            # Initialize history tracking for this sensor
            self.sensor_history[label] = deque(maxlen=self.MAX_HISTORY)
        
        # Update the value
        value_label = self.sensor_labels[label]
        if value is not None:
            if isinstance(value, float):
                value_label.configure(text=f"{value:.2f}")
                # Add numeric value to history
                self.sensor_history[label].append(value)
            elif isinstance(value, (int, complex)):
                value_label.configure(text=str(value))
                # Add numeric value to history
                self.sensor_history[label].append(float(value))
            else:
                value_label.configure(text=str(value))
        else:
            value_label.configure(text="---")
    
    def send_command(self):
        """Send a command to the Arduino"""
        if not self.arduino.is_connected():
            self.show_error("Not connected to Arduino")
            return
        
        command = self.command_entry.get().strip()
        if not command:
            self.show_error("Please enter a command")
            return
        
        if self.arduino.write(command):
            self.command_entry.delete(0, 'end')
            # Show success briefly
            old_text = self.status_label.cget("text")
            old_color = self.status_label.cget("text_color")
            self.status_label.configure(
                text=f"● Sent: {command}",
                text_color="#029CFE"
            )
            self.after(2000, lambda: self.status_label.configure(
                text=old_text,
                text_color=old_color
            ))
        else:
            self.show_error("Failed to send command")
    
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
            baudrate = int(self.baudrate_var.get())
            
            if self.arduino.connect(port, baudrate):
                # Update UI
                self.status_label.configure(
                    text="● Connected",
                    text_color="green"
                )
                self.connect_button.configure(
                    text="Disconnect",
                    fg_color="red",
                    hover_color="darkred"
                )
                
                # Disable port/baudrate selection
                self.port_dropdown.configure(state="disabled")
                self.baudrate_dropdown.configure(state="disabled")
                self.refresh_button.configure(state="disabled")
                
                # Enable command input
                self.send_button.configure(state="normal")
                
                # Start reading data
                self.update_sensor_data()
            else:
                self.show_error(f"Failed to connect to {port}")
        
        except Exception as e:
            self.show_error(f"Connection error: {str(e)}")
    
    def disconnect_arduino(self):
        """Disconnect from Arduino"""
        # Stop data updates
        self.stop_data_updates()
        
        # Disconnect
        self.arduino.disconnect()
        
        # Update UI
        self.status_label.configure(
            text="● Disconnected",
            text_color="red"
        )
        self.connect_button.configure(
            text="Connect",
            fg_color="green",
            hover_color="darkgreen"
        )
        
        # Enable port/baudrate selection
        self.port_dropdown.configure(state="normal")
        self.baudrate_dropdown.configure(state="normal")
        self.refresh_button.configure(state="normal")
        
        # Disable command input
        self.send_button.configure(state="disabled")
        
        # Reset sensor displays
        self.reset_sensor_displays()
    
    def stop_data_updates(self):
        """Stop periodic data updates"""
        if self.update_job is not None:
            self.after_cancel(self.update_job)
            self.update_job = None
    
    def update_sensor_data(self):
        """Read and display sensor data from Arduino"""
        if not self.arduino.is_connected():
            return
        
        # Read data from Arduino
        self.arduino.read_data()
        
        # Update displays for all values
        all_values = self.arduino.get_all_values()
        
        for label, value in all_values.items():
            self.create_or_update_sensor_display(label, value)
        
        # Update raw data display
        raw_data = self.arduino.get_last_raw_data()
        if raw_data:
            self.raw_data_label.configure(text=f"Raw Data: {raw_data}")
        
        # Update charts (every 5 updates to reduce CPU usage)
        if not hasattr(self, '_update_counter'):
            self._update_counter = 0
        self._update_counter += 1
        if self._update_counter >= 5:
            self.update_charts()
            self._update_counter = 0
        
        # Schedule next update (100ms = 10 updates per second)
        self.update_job = self.after(100, self.update_sensor_data)
    
    def reset_sensor_displays(self):
        """Reset all sensor displays to default state"""
        # Clear all sensor display widgets in the scrollable frame
        for widget in self.sensor_scroll.winfo_children():
            widget.destroy()
        
        # Clear the sensor labels dictionary
        self.sensor_labels.clear()
        
        # Clear sensor history
        self.sensor_history.clear()
        
        # Reset the chart
        if self.ax is not None:
            self.ax.clear()
            self.ax.set_facecolor('#1e1e1e')
            self.ax.set_xlabel('Time (samples)', color='white')
            self.ax.set_ylabel('Value', color='white')
            self.ax.set_title('Sensor Data History', color='white', fontsize=12, fontweight='bold')
            self.ax.tick_params(colors='white')
            self.ax.grid(True, alpha=0.3, color='gray')
            if self.canvas:
                self.canvas.draw()
        
        # Reset raw data display
        self.raw_data_label.configure(text="Raw Data: (none)")
        
        # Reset update counter
        if hasattr(self, '_update_counter'):
            self._update_counter = 0
    
    def show_error(self, message):
        """Display an error message to the user"""
        ctkmb.CTkMessagebox(title="Error", message=message, icon="warning")
    
    def toggle_led(self, led_num, var):
        """Toggle LED on/off and send command to Arduino"""
        if not self.arduino.is_connected():
            self.show_error("Not connected to Arduino")
            # Revert checkbox state
            var.set(not var.get())
            return
        
        # Determine command based on checkbox state
        state = "ON" if var.get() else "OFF"
        command = f"LED_{led_num}_{state}"
        
        # Send command to Arduino
        if self.arduino.write(command):
            # Update status briefly
            old_text = self.status_label.cget("text")
            old_color = self.status_label.cget("text_color")
            self.status_label.configure(
                text=f"● LED {led_num}: {state}",
                text_color="#029CFE"
            )
            self.after(1500, lambda: self.status_label.configure(
                text=old_text,
                text_color=old_color
            ))
        else:
            self.show_error(f"Failed to send LED {led_num} command")
            # Revert checkbox state
            var.set(not var.get())
    
    def send_motor_command(self, command):
        """Send motor control command to Arduino"""
        if not self.arduino.is_connected():
            self.show_error("Not connected to Arduino")
            # Revert radio button state
            self.motor_var.set("MOTOR_STOP")
            return
        
        # Send command to Arduino
        if self.arduino.write(command):
            # Update status briefly
            old_text = self.status_label.cget("text")
            old_color = self.status_label.cget("text_color")
            motor_state = command.replace("MOTOR_", "").title()
            self.status_label.configure(
                text=f"● Motor: {motor_state}",
                text_color="#029CFE"
            )
            self.after(1500, lambda: self.status_label.configure(
                text=old_text,
                text_color=old_color
            ))
        else:
            self.show_error("Failed to send motor command")
            # Revert to stop state
            self.motor_var.set("MOTOR_STOP")

    def update_welcome(self, username):
        """Update the welcome message with the logged-in username"""
        self.welcome_label.configure(text=f"Welcome, {username}!")

    def logout(self):
        """Handle logout and return to login screen"""
        # Disconnect Arduino before logging out
        if self.arduino.is_connected():
            self.disconnect_arduino()
        
        self.master.show_login()

