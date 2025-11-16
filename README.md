# Smart parking lot
This repository conrtains the code and wiring diagram for the smart parking lot model
The parking lot is monitored and controlled through a user interface that communicates with the microcontroller

### Features
- Controlled/Automatic gate
- Automatic vehicle elevator
- Automatic lighting system
- Fire detection and alarm
- Rain detection and automatic canopy system

### Parts used
- Microcontroller: Arduino Nano
- Building material: foam paper
- IR sensor for flame detection
- Humidity sensor for rain detection
- Servos for the main gate
- DC motors for the elevator and canopy system
- LED strips for the lighting system

### Wiring diagram
TBD

## Installation and Setup

### Prerequisites
- [Conda](https://docs.conda.io/en/latest/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- An Arduino or Arduino compatible microcontroller
- [Git](https://git-scm.com/)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd CS2
```

### Step 2: Create the Conda Environment
Create a new conda environment with all required dependencies using the provided `environment.yml` file:

```bash
conda env create -f config/environment.yml
```

### Step 3: Activate the Environment
Activate the environment:

```bash
conda activate smart-parking-lot
```

### Step 4: Install the Project as a Package
Install the project in editable mode so imports work correctly:

```bash
pip install -e .
```

### Step 5: Run the Application

```bash
python main.py
```

> The password of each user can be found in the database/user.txt file

### Alternative Installation (Using requirements.txt)
If you prefer to use pip directly or manage your own virtual environment, run line by line:

```bash
# Create and activate a virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r config/requirements.txt

# Install the project as a package (required for imports to work)
pip install -e .

# Run the application
python main.py
```

### Arduino Connection
To connect the application to your Arduino:

1. Upload the appropriate Arduino sketch to your microcontroller
2. Connect the Arduino to your computer via USB
3. In the application, select the correct COM port from the available ports
4. Click "Connect" to establish serial communication

**Troubleshooting:**
- If no COM ports appear, ensure your Arduino is properly connected and drivers are installed
- Default baud rate is 115200 (change it according to your Arduino sketch)
- Check that the serial port is not being used by another application (e.g., Arduino IDE Serial Monitor)

### Deactivating the Environment
When you're done working on the project:

```bash
conda deactivate
```
