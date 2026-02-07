# Retail Theft Detection System

A comprehensive retail theft detection system using Azure AI Vision, refactored following Clean Code principles and SOLID design patterns.

## 📁 Project Structure

```
theft_detection/
│
├── src/                              # Source code (refactored)
│   ├── __init__.py
│   ├── config.py                     # Configuration constants
│   ├── validators.py                 # Input validation
│   ├── geometry_utils.py             # Geometric calculations
│   ├── vision_analyzer.py            # Azure AI Vision integration
│   ├── person_tracker.py             # Person tracking logic
│   ├── zone_monitor.py               # Zone monitoring
│   ├── alert_manager.py              # Alert management
│   ├── behavior_analyzer.py          # Behavior analysis
│   ├── detection_orchestrator.py     # Detection coordination
│   ├── retail_theft_detection.py     # Main system (refactored)
│   └── demo_mock.py                  # Mock client for testing
│
├── tests/                            # Test files
│   ├── __init__.py
│   └── test_theft_detection.py
│
├── utils/                            # Utility modules
│   ├── __init__.py
│   └── logging_instrumentation.py    # Logging and monitoring
│
├── legacy/                           # Original code (archived)
│   └── retail_theft_detection_original.py
│
├── docs/                             # Documentation
│   ├── REFACTORING_COMPLETE.md       # Quick start guide
│   ├── REFACTORING_SUMMARY.md        # Detailed refactoring overview
│   ├── MODULE_GUIDE.md               # Module usage guide
│   ├── BEFORE_AFTER_EXAMPLES.md      # Code comparison examples
│   ├── LOGGING_GUIDE.md              # Logging documentation
│   └── ENHANCEMENTS.md               # Enhancement ideas
│
├── logs/                             # Log files (generated)
├── __pycache__/                      # Python cache (generated)
│
├── main.py                           # Main entry point
├── README.md                         # This file
├── QUICKSTART.md                     # Quick start guide
├── requirements.txt                  # Python dependencies
└── demo_report.json                  # Demo output

```

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the System

#### Option 1: Demo Mode (No Azure credentials needed)
```bash
python main.py
```

#### Option 2: With Azure AI Vision
```bash
# Set environment variables
export AZURE_VISION_ENDPOINT="https://your-resource.cognitiveservices.azure.com/"
export AZURE_VISION_KEY="your-32-character-key"

python main.py
```

#### Option 3: Programmatic Usage
```python
from src import RetailTheftDetector

# Initialize detector
detector = RetailTheftDetector(
    endpoint="https://your-endpoint.cognitiveservices.azure.com/",
    key="your-key"
)

# Analyze an image
alerts = detector.analyze_frame("store_image.jpg")

# Process a video
detector.process_video("store_footage.mp4", output_dir="./alerts")

# Generate report
detector.generate_report("theft_report.json")
```

## Features

✅ **Real-time People Detection** - Detects and tracks people across video frames  
✅ **Zone Monitoring** - Monitors restricted areas, exits, and high-value zones  
✅ **Suspicious Behavior Detection** - Identifies loitering, rapid movements, and unusual patterns  
✅ **Object Detection** - Tracks high-value items and potential concealment objects  
✅ **Alert Generation** - Creates severity-based alerts with evidence images  
✅ **Report Generation** - Produces JSON reports of all detected incidents  
✅ **Multi-Camera Support** - Processes video streams from multiple sources  

## Architecture

```text
┌─────────────────┐
│ Video Source    │ (Camera/File)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Frame Capture   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ Azure AI Vision Analysis    │
│  • People Detection         │
│  • Object Detection         │
│  • Scene Understanding      │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Theft Detection Logic       │
│  • Zone Violations          │
│  • Loitering Detection      │
│  • Behavior Analysis        │
│  • Object Tracking          │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Alert Generation & Logging  │
│  • Evidence Capture         │
│  • Notification System      │
│  • Report Generation        │
└─────────────────────────────┘
```

## Project Structure

- **logging_instrumentation.py**: Contains the main logging instrumentation code for theft detection.
- **retail_theft_detection.py**: Implements the core theft detection logic.
- **test_theft_detection.py**: Includes test cases to validate the functionality of the theft detection system.
- **requirements.txt**: Lists the dependencies required to run the project.
- **LOGGING_GUIDE.md**: Provides guidelines and documentation for the logging instrumentation.
- **.env.example**: Template for environment variables configuration.
- **.gitignore**: Git ignore file to prevent committing sensitive data.

## Prerequisites

1. **Python Environment**  
   - Python 3.8 or higher  
   - pip package manager

2. **Azure Account (Optional for Demo)**  
   - Active Azure subscription ([Create free account](https://azure.microsoft.com/free/))
   - Create Computer Vision resource in Azure Portal  
   - Note your Endpoint and Key

**Note:** You can run the system in demo mode without Azure credentials!

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   ```

2. Navigate to the project directory:

   ```bash
   cd theft_detection
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Azure Credentials (Optional)**:

   Create a `.env` file from the template:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Azure credentials:

   ```ini
   AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   AZURE_VISION_KEY=your-32-character-key-here
   DEMO_MODE=false
   ```

   **Or run in demo mode** (no Azure keys needed):

   ```ini
   DEMO_MODE=true
   ```

## Quick Start

### Demo Mode (No Azure Required)

Run the system immediately without any Azure credentials:

```bash
python retail_theft_detection.py
```

The system will:
- Automatically detect missing Azure credentials
- Switch to demo mode
- Create a sample store image
- Run mock analysis with simulated detections
- Generate a demo report

### Production Mode (With Azure AI Vision)

1. Set up your `.env` file with Azure credentials (see Installation step 4)

2. Run the system:

   ```bash
   python retail_theft_detection.py
   ```

## Usage

Run the main script to start the theft detection system:

```bash
python retail_theft_detection.py
```

### Process Video File

```python
# Process entire video
detector.process_video(
    video_path="store_footage.mp4",
    output_dir="./alerts"
)

# Generate report
detector.generate_report("incident_report.json")
```

### Process Live Camera Stream

```python
# Use webcam (camera index 0)
detector.process_video(
    video_path=0,
    output_dir="./live_alerts"
)

# Or use IP camera RTSP stream
detector.process_video(
    video_path="rtsp://camera-ip:port/stream",
    output_dir="./alerts"
)
```

## Testing

To run the test suite, execute the following command:

```bash
pytest test_theft_detection.py
```

## Configuration

### Configure Store Zones

Edit the `_initialize_zones()` method to match your store layout:

```python
def _initialize_zones(self) -> List[DetectionZone]:
    return [
        DetectionZone(
            name="Jewelry_Counter",
            coordinates=[(100, 50), (400, 50), (400, 300), (100, 300)],
            is_restricted=False,
            alert_on_loitering=True,
            max_loiter_seconds=120  # 2 minutes
        ),
        DetectionZone(
            name="Employee_Only",
            coordinates=[(0, 400), (200, 400), (200, 600), (0, 600)],
            is_restricted=True  # Customers forbidden
        ),
        # Add more zones...
    ]
```

## License

This project is licensed under the MIT License.
