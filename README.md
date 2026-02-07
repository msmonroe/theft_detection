# Theft Detection Project

## Overview
This project is designed to detect theft using advanced algorithms and logging instrumentation. It includes Python scripts for logging, theft detection, and a test suite to ensure the functionality of the system. Additionally, it integrates Azure AI Vision for advanced computer vision capabilities, making it suitable for retail theft detection scenarios.

## Features

✅ **Real-time People Detection** - Detects and tracks people across video frames  
✅ **Zone Monitoring** - Monitors restricted areas, exits, and high-value zones  
✅ **Suspicious Behavior Detection** - Identifies loitering, rapid movements, and unusual patterns  
✅ **Object Detection** - Tracks high-value items and potential concealment objects  
✅ **Alert Generation** - Creates severity-based alerts with evidence images  
✅ **Report Generation** - Produces JSON reports of all detected incidents  
✅ **Multi-Camera Support** - Processes video streams from multiple sources  

## Architecture

```
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

## Prerequisites

1. **Azure Account**  
   - Active Azure subscription ([Create free account](https://azure.microsoft.com/free/))

2. **Azure AI Vision Resource**  
   - Create Computer Vision resource in Azure Portal  
   - Note your Endpoint and Key

3. **Python Environment**  
   - Python 3.8 or higher  
   - pip package manager

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd theft_detection
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the main script to start the theft detection system:
```
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
```
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
