"""
Retail Theft Detection System using Azure AI Vision (Refactored)
=================================================================

This comprehensive system uses Azure AI Vision to detect potential theft in retail stores.

This file serves as the main entry point and facade, delegating responsibilities
to specialized components following Clean Code principles.

Features:
- Real-time people detection and tracking
- Suspicious behavior pattern recognition
- Zone violation detection (restricted areas, exits)
- Item concealment detection
- Loitering detection
- Multi-camera support
- Alert generation and logging

Requirements:
    pip install azure-ai-vision-imageanalysis opencv-python numpy

Author: AI-102 Study Implementation
"""

import os
import cv2
import numpy as np
from typing import List
from datetime import datetime

# Support both package and direct imports
try:
    from .vision_analyzer import VisionAnalyzer
    from .zone_monitor import ZoneMonitor, DetectionZone
    from .alert_manager import AlertManager, TheftAlert, ThreatLevel
    from .detection_orchestrator import DetectionOrchestrator
    from .config import TrackingConfig, FilePaths
    from .validators import validate_directory_exists
except ImportError:
    from vision_analyzer import VisionAnalyzer
    from zone_monitor import ZoneMonitor, DetectionZone
    from alert_manager import AlertManager, TheftAlert, ThreatLevel
    from detection_orchestrator import DetectionOrchestrator
    from config import TrackingConfig, FilePaths
    from validators import validate_directory_exists


# =============================================================================
# MAIN DETECTION CLASS (Refactored with Clean Architecture)
# =============================================================================

class RetailTheftDetector:
    """
    Main theft detection system using Azure AI Vision.
    
    This class now acts as a facade, coordinating specialized components
    that each have a single, well-defined responsibility.
    """
    
    def __init__(self, endpoint: str, key: str, zones: List[DetectionZone] = None):
        """
        Initialize the theft detection system.
        
        Args:
            endpoint: Azure AI Vision endpoint URL
            key: Azure AI Vision subscription key
            zones: Optional list of DetectionZone objects (uses defaults if None)
        """
        print(f"\n{'='*70}")
        print("RETAIL THEFT DETECTION SYSTEM")
        print("Powered by Azure AI Vision")
        print(f"{'='*70}\n")
        
        # Initialize components following Dependency Injection pattern
        self._vision_analyzer = VisionAnalyzer(endpoint, key)
        self._zone_monitor = ZoneMonitor(zones)
        self._alert_manager = AlertManager()
        
        # Create the orchestrator that coordinates detection
        self._orchestrator = DetectionOrchestrator(
            vision_analyzer=self._vision_analyzer,
            zone_monitor=self._zone_monitor,
            alert_manager=self._alert_manager
        )
        
        print(f"\n{'='*70}")
        print("[OK] System Initialized Successfully")
        print(f"{'='*70}\n")
    
    def analyze_frame(self, image_path: str, frame_number: int = 0) -> List[TheftAlert]:
        """
        Analyze a single frame for suspicious activity.
        
        Args:
            image_path: Path to image file
            frame_number: Frame number for tracking (0 for single images)  
            
        Returns:
            List of TheftAlert objects
        """
        return self._orchestrator.analyze_frame(image_path, frame_number)
    
    def process_video(self, video_path: str, output_dir: str = FilePaths.DEFAULT_ALERT_DIR) -> None:
        """
        Process video stream for theft detection.
        
        Args:
            video_path: Path to video file or camera index (0 for webcam)
            output_dir: Directory to save alert images
        """
        print(f"\n{'='*70}")
        print(f"VIDEO PROCESSING")
        print(f"{'='*70}")
        print(f"Source: {video_path}")
        print(f"Output: {output_dir}\n")
        
        validate_directory_exists(output_dir)
        
        video_processor = VideoProcessor(
            orchestrator=self._orchestrator,
            output_dir=output_dir
        )
        
        video_processor.process(video_path)
    
    def generate_report(self, output_file: str = FilePaths.DEFAULT_REPORT_FILE) -> dict:
        """
        Generate JSON report of all alerts.
        
        Args:
            output_file: Path to output JSON file
            
        Returns:
            Report dictionary
        """
        return self._alert_manager.generate_report(output_file)
    
    @property
    def zones(self) -> List[DetectionZone]:
        """Get all monitoring zones."""
        return self._zone_monitor.get_all_zones()
    
    @property
    def recent_alerts(self) -> List[TheftAlert]:
        """Get recent alerts."""
        return self._alert_manager.get_recent_alerts()


# =============================================================================
# VIDEO PROCESSING (Extracted to separate class)
# =============================================================================

class VideoProcessor:
    """
    Processes video streams for theft detection.
    
    Separated from main detector class following Single Responsibility Principle.
    """
    
    def __init__(self, orchestrator: DetectionOrchestrator, output_dir: str):
        """
        Initialize video processor.
        
        Args:
            orchestrator: DetectionOrchestrator instance
            output_dir: Directory to save alert images
        """
        self._orchestrator = orchestrator
        self._output_dir = output_dir
    
    def process(self, video_path: str) -> None:
        """
        Process a video file or camera stream.
        
        Args:
            video_path: Path to video file or camera index
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"✗ Cannot open video: {video_path}")
            return
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"FPS: {fps}")
        print(f"Frames: {total_frames}")
        
        stats = self._process_frames(cap, total_frames)
        
        cap.release()
        
        self._print_summary(stats)
    
    def _process_frames(self, cap: cv2.VideoCapture, total_frames: int) -> dict:
        """
        Process all frames in the video.
        
        Args:
            cap: OpenCV video capture object
            total_frames: Total number of frames
            
        Returns:
            Processing statistics dictionary
        """
        frame_num = 0
        processed = 0
        alert_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    print("\n[OK] Video complete")
                    break
                
                # Process selected frames only to reduce API costs
                if frame_num % TrackingConfig.FRAME_SKIP_INTERVAL == 0:
                    alert_count += self._process_single_frame(
                        frame, 
                        frame_num
                    )
                    processed += 1
                
                frame_num += 1
                
                # Progress update
                if frame_num % 300 == 0:
                    self._print_progress(frame_num, total_frames)
        
        except KeyboardInterrupt:
            print("\n✗ Interrupted by user")
        
        return {
            'total_frames': frame_num,
            'processed': processed,
            'alert_count': alert_count
        }
    
    def _process_single_frame(self, frame: np.ndarray, frame_num: int) -> int:
        """
        Process a single video frame.
        
        Args:
            frame: Frame image array
            frame_num: Frame number
            
        Returns:
            Number of alerts generated
        """
        # Save frame temporarily
        temp_file = os.path.join(self._output_dir, FilePaths.TEMP_FRAME_FILE)
        cv2.imwrite(temp_file, frame)
        
        # Analyze frame
        alerts = self._orchestrator.analyze_frame(temp_file, frame_num)
        
        # Handle alerts
        for alert in alerts:
            self._save_alert_image(frame, alert, frame_num)
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return len(alerts)
    
    def _save_alert_image(self, 
                         frame: np.ndarray, 
                         alert: TheftAlert,
                         frame_num: int) -> None:
        """
        Save annotated alert image.
        
        Args:
            frame: Frame image array
            alert: TheftAlert object
            frame_num: Frame number
        """
        annotated = self._annotate_frame(frame, alert)
        
        alert_file = os.path.join(
            self._output_dir,
            f"alert_{alert.alert_type}_{frame_num}.jpg"
        )
        
        cv2.imwrite(alert_file, annotated)
    
    def _annotate_frame(self, frame: np.ndarray, alert: TheftAlert) -> np.ndarray:
        """
        Add annotations to frame for alert visualization.
        
        Args:
            frame: Frame image array
            alert: TheftAlert object
            
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        
        # Draw bounding boxes
        for bbox in alert.bounding_boxes:
            x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
            cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 0, 255), 2)
        
        # Add text overlay
        cv2.putText(
            annotated, 
            f"{alert.alert_type} - {alert.severity}", 
            (10, 30), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, 
            (0, 0, 255), 
            2
        )
        
        cv2.putText(
            annotated, 
            alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            (10, 70), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.7, 
            (255, 255, 255), 
            2
        )
        
        return annotated
    
    def _print_progress(self, frame_num: int, total_frames: int) -> None:
        """Print processing progress."""
        progress = (frame_num / total_frames * 100) if total_frames > 0 else 0
        print(f"Progress: {progress:.1f}% (frame {frame_num})")
    
    def _print_summary(self, stats: dict) -> None:
        """Print processing summary."""
        print(f"\n{'='*70}")
        print(f"PROCESSING SUMMARY")
        print(f"{'='*70}")
        print(f"Total frames: {stats['total_frames']}")
        print(f"Analyzed: {stats['processed']}")
        print(f"Alerts: {stats['alert_count']}")
        print(f"Output: {self._output_dir}")
        print(f"{'='*70}\n")


# =============================================================================
# EXAMPLE USAGE AND DEMO
# =============================================================================

def create_demo_image(filename: str = FilePaths.DEMO_IMAGE_FILE) -> str:
    """
    Create a demo image for testing without Azure.
    
    Args:
        filename: Path where the demo image should be saved
        
    Returns:
        Path to the created image
    """
    # Create a simple store scene
    img = np.ones((480, 640, 3), dtype=np.uint8) * 200
    
    # Add colored rectangles to simulate a store
    cv2.rectangle(img, (50, 100), (200, 400), (150, 150, 150), -1)  # Person
    cv2.rectangle(img, (300, 150), (500, 350), (100, 100, 200), 2)  # Display
    cv2.rectangle(img, (550, 50), (620, 150), (200, 100, 100), -1)  # Exit sign
    
    # Add text labels
    cv2.putText(img, "DEMO STORE", (200, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, "Person", (80, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(img, "EXIT", (555, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    cv2.imwrite(filename, img)
    
    return filename


def run_demo_mode():
    """Run system in demo mode with mock Azure client."""
    print("[DEMO MODE] - Using Mock Azure Vision\n")
    
    from demo_mock import MockVisionClient, create_mock_detector
    
    # Create demo detector with mock client
    detector = create_mock_detector()
    
    # Create demo image
    print("Creating demo store image...")
    demo_image = create_demo_image()
    print(f"[OK] Demo image created: {demo_image}\n")
    
    # Run demo analysis
    print("="*70)
    print("DEMO: Analyzing Store Scene")
    print("="*70)
    
    alerts = detector.analyze_frame(demo_image, frame_number=1)
    
    print_demo_results(alerts)
    
    # Generate demo report
    detector.generate_report("demo_report.json")
    
    print_demo_instructions()


def print_demo_results(alerts: List[TheftAlert]) -> None:
    """Print demo analysis results."""
    if alerts:
        print(f"\n🎯 Demo Results: {len(alerts)} alert(s) detected\n")
        for i, alert in enumerate(alerts, 1):
            print(f"Alert {i}:")
            print(f"  Type: {alert.alert_type}")
            print(f"  Severity: {alert.severity}")
            print(f"  Confidence: {alert.confidence:.1%}")
            print(f"  Location: {alert.location}")
            print(f"  Description: {alert.description}\n")
    else:
        print("\n[OK] No suspicious activity detected in demo\n")


def print_demo_instructions() -> None:
    """Print instructions after demo."""
    print("="*70)
    print("Demo Complete!")
    print("="*70)
    print("\nNext Steps:")
    print("  1. Check demo_store.jpg to see the analyzed image")
    print("  2. Check demo_report.json for the full report")
    print("  3. Add Azure keys to .env file to use real AI Vision")
    print("="*70 + "\n")


def run_production_mode(endpoint: str, key: str) -> None:
    """
    Run system in production mode with real Azure AI Vision.
    
    Args:
        endpoint: Azure endpoint URL
        key: Azure subscription key
    """
    print("🔑 Production Mode - Using Azure AI Vision\n")
    
    # Initialize detector
    detector = RetailTheftDetector(endpoint, key)
    
    # Example 1: Analyze single image
    test_image = "store_frame.jpg"
    if os.path.exists(test_image):
        print("\nExample 1: Single Image Analysis")
        print("="*70)
        alerts = detector.analyze_frame(test_image)
        print(f"\nResult: {len(alerts)} alert(s) generated")
    
    # Example 2: Process video
    video_file = "store_footage.mp4"
    if os.path.exists(video_file):
        print("\nExample 2: Video Processing")
        print("="*70)
        detector.process_video(video_file, "./theft_alerts")
        detector.generate_report("theft_report.json")


def main():
    """Main entry point for the theft detection system."""
    
    print("""
================================================================
          RETAIL THEFT DETECTION SYSTEM                      
          Powered by Azure AI Vision                         
          (Refactored with Clean Code Principles)            
================================================================
""")
    
    # Load environment configuration
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("[OK] Loaded configuration from .env file\n")
    except ImportError:
        print("[INFO] python-dotenv not installed\n")
    
    # Get configuration
    endpoint = os.getenv("AZURE_VISION_ENDPOINT")
    key = os.getenv("AZURE_VISION_KEY")
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    
    # Run in appropriate mode
    if demo_mode or (not endpoint or not key):
        run_demo_mode()
    else:
        run_production_mode(endpoint, key)
    
    print("\n" + "="*70)
    print("Session Complete")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
