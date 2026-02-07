"""
Retail Theft Detection System using Azure AI Vision
====================================================

This comprehensive system uses Azure AI Vision to detect potential theft in retail stores.

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
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import cv2
import numpy as np

# Azure AI Vision imports
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class DetectionZone:
    """
    Defines a monitoring zone in the retail store.
    
    Zones are used to:
    - Detect unauthorized access to restricted areas
    - Monitor high-value merchandise areas
    - Track customer flow
    - Detect unusual dwell times
    """
    name: str
    coordinates: List[Tuple[int, int]]  # Polygon vertices [(x1,y1), (x2,y2), ...]
    is_restricted: bool = False         # True for employee-only areas
    alert_on_loitering: bool = False    # Generate alert for extended presence
    max_loiter_seconds: int = 120       # Maximum allowed time in zone


@dataclass
class TheftAlert:
    """Represents a detected suspicious activity."""
    timestamp: datetime
    alert_type: str                     # Type of suspicious activity
    confidence: float                   # Confidence score (0.0 - 1.0)
    location: str                       # Zone or area name
    description: str                    # Human-readable description
    image_path: str                     # Path to evidence image
    bounding_boxes: List[Dict]          # Detected objects/people locations
    severity: str = "MEDIUM"            # LOW, MEDIUM, HIGH, CRITICAL


# =============================================================================
# MAIN DETECTION CLASS
# =============================================================================

class RetailTheftDetector:
    """
    Main theft detection system using Azure AI Vision.
    
    This class orchestrates the detection pipeline:
    1. Image acquisition from cameras
    2. Azure AI Vision analysis
    3. Pattern recognition
    4. Alert generation
    5. Evidence logging
    """
    
    def __init__(self, endpoint: str, key: str):
        """
        Initialize the theft detection system.
        
        Args:
            endpoint: Azure AI Vision endpoint URL
                     Example: "https://myresource.cognitiveservices.azure.com/"
            key: Azure AI Vision subscription key (32-character hex string)
        """
        # Initialize Azure AI Vision client
        # This client handles all API calls to Azure
        self.vision_client = ImageAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
        
        # Store credentials for potential future use
        self.endpoint = endpoint
        self.key = key
        
        # Person tracking across frames
        # Key: person_id, Value: tracking data including position history
        self.tracked_people = {}
        
        # Alert history to prevent duplicate alerts
        self.recent_alerts = []
        
        # Define monitoring zones (store layout specific)
        self.zones = self._initialize_zones()
        
        # Configuration thresholds
        self.confidence_threshold = 0.6      # Minimum confidence for detections
        self.loiter_threshold_seconds = 180  # 3 minutes triggers loitering alert
        self.rapid_movement_threshold = 500  # Pixels per second
        
        print(f"✓ Theft Detection System Initialized")
        print(f"  Endpoint: {endpoint}")
        print(f"  Zones: {len(self.zones)}")
    
    
    def _initialize_zones(self) -> List[DetectionZone]:
        """
        Initialize store monitoring zones.
        
        In production, load from configuration file or database.
        Coordinates should match your camera FOV and be calibrated.
        
        Returns:
            List of DetectionZone objects
        """
        return [
            # Checkout area - monitor for theft at point of sale
            DetectionZone(
                name="Checkout_Counter",
                coordinates=[(0, 0), (300, 0), (300, 200), (0, 200)],
                alert_on_loitering=True,
                max_loiter_seconds=180
            ),
            
            # High-value electronics section
            DetectionZone(
                name="Electronics_Display",
                coordinates=[(300, 0), (600, 0), (600, 300), (300, 300)],
                alert_on_loitering=True,
                max_loiter_seconds=120  # Shorter threshold for high-value area
            ),
            
            # Store exit - monitor for unpaid merchandise
            DetectionZone(
                name="Exit_Zone",
                coordinates=[(700, 0), (1000, 0), (1000, 200), (700, 200)],
                alert_on_loitering=False
            ),
            
            # Restricted employee area
            DetectionZone(
                name="Employee_Storage",
                coordinates=[(0, 400), (200, 400), (200, 600), (0, 600)],
                is_restricted=True  # Customers should never be here
            )
        ]
    
    
    def analyze_frame(self, image_path: str, frame_number: int = 0) -> List[TheftAlert]:
        """
        Analyze a single frame for suspicious activity.
        
        This is the main analysis pipeline that:
        1. Calls Azure AI Vision to detect people and objects
        2. Tracks people across frames
        3. Checks for zone violations
        4. Detects suspicious behaviors
        5. Generates alerts
        
        Args:
            image_path: Path to image file
            frame_number: Frame number for tracking (0 for single images)
            
        Returns:
            List of TheftAlert objects
        """
        alerts = []
        
        print(f"\n{'='*70}")
        print(f"Analyzing: {image_path}")
        print(f"{'='*70}")
        
        try:
            # STEP 1: Call Azure AI Vision API
            # This returns people, objects, tags, and caption
            analysis_result = self._call_azure_vision(image_path)
            
            # STEP 2: Detect and track people
            people_alerts = self._detect_people(
                analysis_result, 
                image_path, 
                frame_number
            )
            alerts.extend(people_alerts)
            
            # STEP 3: Detect suspicious objects
            object_alerts = self._detect_suspicious_objects(
                analysis_result, 
                image_path
            )
            alerts.extend(object_alerts)
            
            # STEP 4: Check zone violations
            zone_alerts = self._check_zones(
                analysis_result, 
                image_path
            )
            alerts.extend(zone_alerts)
            
            # STEP 5: Analyze behavior patterns (if tracking)
            if frame_number > 0:
                behavior_alerts = self._analyze_behaviors(
                    analysis_result, 
                    frame_number, 
                    image_path
                )
                alerts.extend(behavior_alerts)
            
            # STEP 6: Detect concealment attempts
            concealment_alerts = self._detect_concealment(
                analysis_result, 
                image_path
            )
            alerts.extend(concealment_alerts)
            
            print(f"✓ Analysis complete: {len(alerts)} alert(s)")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            # In production, log to monitoring system
        
        return alerts
    
    
    def _call_azure_vision(self, image_path: str):
        """
        Call Azure AI Vision API to analyze image.
        
        Uses Image Analysis 4.0 API which provides:
        - PEOPLE: Detect people with bounding boxes
        - OBJECTS: Detect objects with labels and locations
        - TAGS: Scene understanding tags
        - CAPTION: Natural language scene description
        
        Args:
            image_path: Path to image file
            
        Returns:
            ImageAnalysisResult object from Azure
        """
        print(f"→ Calling Azure AI Vision...")
        
        # Read image file as binary
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Define what features we want to extract
        # Each feature costs API credits, so only request what you need
        visual_features = [
            VisualFeatures.PEOPLE,   # Detect people and locations
            VisualFeatures.OBJECTS,  # Detect objects (bags, items, etc.)
            VisualFeatures.TAGS,     # Get scene understanding tags
            VisualFeatures.CAPTION   # Get natural language description
        ]
        
        # Make API call
        # This is synchronous - consider async for real-time processing
        result = self.vision_client.analyze(
            image_data=image_data,
            visual_features=visual_features
        )
        
        # Log what was detected
        people_count = len(result.people.list) if result.people else 0
        object_count = len(result.objects.list) if result.objects else 0
        
        print(f"  ✓ People: {people_count}")
        print(f"  ✓ Objects: {object_count}")
        if result.caption:
            print(f"  ✓ Scene: {result.caption.text}")
        
        return result
    
    
    def _detect_people(self, result, image_path: str, frame_number: int) -> List[TheftAlert]:
        """
        Detect people and analyze for suspicious patterns.
        
        This function:
        - Identifies all people in frame
        - Tracks them across frames (for video)
        - Checks if they're in restricted zones
        - Monitors dwell time for loitering
        
        Args:
            result: Azure AI Vision analysis result
            image_path: Path to analyzed image
            frame_number: Current frame number
            
        Returns:
            List of alerts related to people
        """
        alerts = []
        
        if not result.people:
            return alerts
        
        people_count = len(result.people.list)
        print(f"\n→ Analyzing {people_count} person/people")
        
        for idx, person in enumerate(result.people.list):
            # Extract bounding box
            # Bounding box format: x (left), y (top), width, height
            bbox = person.bounding_box
            location = {
                'x': bbox.x,
                'y': bbox.y,
                'width': bbox.width,
                'height': bbox.height
            }
            
            # Confidence score for this detection
            confidence = person.confidence
            
            print(f"  Person {idx + 1}: ({bbox.x}, {bbox.y}) confidence={confidence:.2%}")
            
            # Track this person (for video sequences)
            person_id = self._track_person(location, frame_number)
            
            # Check if in restricted zone
            zone = self._get_zone_for_location(bbox.x + bbox.width//2, bbox.y + bbox.height//2)
            
            if zone:
                # ALERT: Restricted area access
                if zone.is_restricted:
                    alert = TheftAlert(
                        timestamp=datetime.now(),
                        alert_type="RESTRICTED_AREA_VIOLATION",
                        confidence=confidence,
                        location=zone.name,
                        description=f"Unauthorized person in {zone.name}",
                        image_path=image_path,
                        bounding_boxes=[location],
                        severity="CRITICAL"
                    )
                    alerts.append(alert)
                    print(f"    ⚠ CRITICAL: Restricted area violation!")
                
                # ALERT: Loitering detection
                if zone.alert_on_loitering and person_id in self.tracked_people:
                    dwell_time = self._calculate_dwell_time(person_id, frame_number)
                    
                    if dwell_time > zone.max_loiter_seconds:
                        alert = TheftAlert(
                            timestamp=datetime.now(),
                            alert_type="LOITERING",
                            confidence=0.85,
                            location=zone.name,
                            description=f"Person loitering {dwell_time:.0f}s in {zone.name}",
                            image_path=image_path,
                            bounding_boxes=[location],
                            severity="MEDIUM"
                        )
                        alerts.append(alert)
                        print(f"    ⚠ MEDIUM: Loitering detected ({dwell_time:.0f}s)")
        
        return alerts
    
    
    def _detect_suspicious_objects(self, result, image_path: str) -> List[TheftAlert]:
        """
        Detect suspicious objects or item handling.
        
        Looks for:
        - High-value items near exits
        - Bags/containers that could conceal items
        - Items being handled near restricted areas
        
        Args:
            result: Azure AI Vision result
            image_path: Image being analyzed
            
        Returns:
            List of object-related alerts
        """
        alerts = []
        
        if not result.objects:
            return alerts
        
        object_count = len(result.objects.list)
        print(f"\n→ Analyzing {object_count} object(s)")
        
        # Define items to monitor
        high_value_items = [
            'laptop', 'phone', 'tablet', 'camera', 
            'jewelry', 'watch', 'electronics'
        ]
        
        concealment_items = [
            'bag', 'backpack', 'purse', 'jacket', 'coat', 'luggage'
        ]
        
        for obj in result.objects.list:
            # Get object name and confidence
            obj_name = obj.tags[0].name.lower() if obj.tags else "unknown"
            confidence = obj.tags[0].confidence if obj.tags else 0.0
            
            # Skip low confidence detections
            if confidence < self.confidence_threshold:
                continue
            
            bbox = obj.bounding_box
            location = {
                'x': bbox.x,
                'y': bbox.y,
                'width': bbox.width,
                'height': bbox.height
            }
            
            print(f"  Object: {obj_name} (confidence={confidence:.2%})")
            
            # Check zone location
            zone = self._get_zone_for_location(bbox.x + bbox.width//2, bbox.y + bbox.height//2)
            
            # ALERT: High-value item near exit
            if any(item in obj_name for item in high_value_items):
                if zone and 'exit' in zone.name.lower():
                    alert = TheftAlert(
                        timestamp=datetime.now(),
                        alert_type="UNPAID_ITEM_AT_EXIT",
                        confidence=confidence * 0.9,
                        location=zone.name,
                        description=f"High-value {obj_name} detected at exit",
                        image_path=image_path,
                        bounding_boxes=[location],
                        severity="HIGH"
                    )
                    alerts.append(alert)
                    print(f"    ⚠ HIGH: High-value item at exit!")
            
            # INFO: Concealment item detected
            if any(item in obj_name for item in concealment_items):
                print(f"    ⓘ Concealment item: {obj_name}")
                # Could correlate with person locations for enhanced detection
        
        return alerts
    
    
    def _detect_concealment(self, result, image_path: str) -> List[TheftAlert]:
        """
        Detect potential item concealment behavior.
        
        Uses scene tags to identify suspicious combinations:
        - Person + bag + merchandise = potential concealment
        - Person + reaching motion = suspicious interaction
        
        Args:
            result: Azure AI Vision result
            image_path: Image path
            
        Returns:
            List of concealment alerts
        """
        alerts = []
        
        if not result.tags:
            return alerts
        
        print(f"\n→ Checking concealment patterns")
        
        # Extract tags with sufficient confidence
        tags = [tag.name.lower() for tag in result.tags.list 
                if tag.confidence > self.confidence_threshold]
        
        tag_string = ' '.join(tags)
        
        # Define suspicious tag combinations
        suspicious_patterns = [
            (['person', 'bag', 'clothing'], "Person with bag near clothing"),
            (['person', 'backpack', 'electronics'], "Person with backpack near electronics"),
            (['person', 'reaching'], "Person reaching for items"),
        ]
        
        for pattern_tags, description in suspicious_patterns:
            if all(tag in tag_string for tag in pattern_tags):
                alert = TheftAlert(
                    timestamp=datetime.now(),
                    alert_type="CONCEALMENT_PATTERN",
                    confidence=0.70,
                    location="Unknown",
                    description=description,
                    image_path=image_path,
                    bounding_boxes=[],
                    severity="MEDIUM"
                )
                alerts.append(alert)
                print(f"  ⚠ MEDIUM: {description}")
        
        return alerts
    
    
    def _check_zones(self, result, image_path: str) -> List[TheftAlert]:
        """
        Check for zone-based violations.
        
        Args:
            result: Azure AI Vision result
            image_path: Image path
            
        Returns:
            List of zone violation alerts
        """
        alerts = []
        print(f"\n→ Checking zone violations")
        
        # This is where you'd implement sophisticated zone checking
        # For now, it's handled in _detect_people
        
        return alerts
    
    
    def _analyze_behaviors(self, result, frame_number: int, image_path: str) -> List[TheftAlert]:
        """
        Analyze behavioral patterns across frames.
        
        Detects:
        - Rapid movements (rushing, fleeing)
        - Erratic paths (avoiding cameras/staff)
        - Repeated visits to same area
        
        Args:
            result: Current frame analysis
            frame_number: Current frame number
            image_path: Image path
            
        Returns:
            List of behavior alerts
        """
        alerts = []
        
        print(f"\n→ Analyzing behavior patterns (frame {frame_number})")
        
        # Analyze movement patterns for tracked people
        for person_id, tracking_data in self.tracked_people.items():
            if len(tracking_data['history']) >= 5:
                # Get recent positions
                recent = tracking_data['history'][-5:]
                
                # Calculate movement speed
                distance = self._calc_total_distance(recent)
                time_span = 5 / 30  # 5 frames at 30 FPS = ~0.17 seconds
                speed = distance / time_span if time_span > 0 else 0
                
                # ALERT: Rapid movement detected
                if speed > self.rapid_movement_threshold:
                    print(f"  ⚠ Rapid movement: person_{person_id} ({speed:.0f} px/s)")
                    # Could generate alert if needed
        
        return alerts
    
    
    def _track_person(self, location: Dict, frame_number: int) -> str:
        """
        Simple person tracking across frames.
        
        Production systems should use:
        - SORT (Simple Online Realtime Tracking)
        - DeepSORT (with appearance features)
        - ByteTrack
        - FairMOT
        
        Args:
            location: Bounding box dict
            frame_number: Current frame
            
        Returns:
            Person ID string
        """
        person_id = f"person_{len(self.tracked_people)}"
        
        # Match with existing tracks
        for existing_id, data in self.tracked_people.items():
            if data['last_frame'] == frame_number - 1:
                last_loc = data['history'][-1]
                dist = self._calc_distance(location, last_loc)
                
                # If close enough, same person
                if dist < 100:  # 100 pixel threshold
                    person_id = existing_id
                    break
        
        # Update tracking data
        if person_id not in self.tracked_people:
            self.tracked_people[person_id] = {
                'first_frame': frame_number,
                'last_frame': frame_number,
                'history': [location]
            }
        else:
            self.tracked_people[person_id]['last_frame'] = frame_number
            self.tracked_people[person_id]['history'].append(location)
        
        return person_id
    
    
    def _calculate_dwell_time(self, person_id: str, current_frame: int) -> float:
        """Calculate how long person has been present (in seconds)."""
        if person_id not in self.tracked_people:
            return 0.0
        
        data = self.tracked_people[person_id]
        frames = current_frame - data['first_frame']
        
        # Assume 30 FPS
        return frames / 30.0
    
    
    def _get_zone_for_location(self, x: int, y: int) -> Optional[DetectionZone]:
        """
        Find which zone a point belongs to.
        
        Args:
            x, y: Coordinates
            
        Returns:
            DetectionZone or None
        """
        for zone in self.zones:
            if self._point_in_polygon((x, y), zone.coordinates):
                return zone
        return None
    
    
    def _point_in_polygon(self, point: Tuple[int, int], 
                         polygon: List[Tuple[int, int]]) -> bool:
        """
        Ray casting algorithm for point-in-polygon test.
        
        Args:
            point: (x, y) to test
            polygon: List of (x, y) vertices
            
        Returns:
            True if point inside polygon
        """
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    
    def _calc_distance(self, loc1: Dict, loc2: Dict) -> float:
        """Calculate Euclidean distance between bounding box centers."""
        x1 = loc1['x'] + loc1['width'] / 2
        y1 = loc1['y'] + loc1['height'] / 2
        x2 = loc2['x'] + loc2['width'] / 2
        y2 = loc2['y'] + loc2['height'] / 2
        
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    
    def _calc_total_distance(self, positions: List[Dict]) -> float:
        """Calculate total path distance."""
        total = 0.0
        for i in range(len(positions) - 1):
            total += self._calc_distance(positions[i], positions[i + 1])
        return total
    
    
    def process_video(self, video_path: str, output_dir: str = "./alerts"):
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
        
        os.makedirs(output_dir, exist_ok=True)
        
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"✗ Cannot open video: {video_path}")
            return
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"FPS: {fps}")
        print(f"Frames: {total_frames}")
        
        # Process every Nth frame to reduce API costs
        frame_skip = 30  # ~1 frame per second for 30fps video
        
        frame_num = 0
        processed = 0
        alert_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    print("\n✓ Video complete")
                    break
                
                # Only process selected frames
                if frame_num % frame_skip == 0:
                    # Save frame temporarily
                    temp_file = f"{output_dir}/temp_frame.jpg"
                    cv2.imwrite(temp_file, frame)
                    
                    # Analyze frame
                    alerts = self.analyze_frame(temp_file, frame_num)
                    processed += 1
                    
                    # Handle alerts
                    if alerts:
                        alert_count += len(alerts)
                        
                        for alert in alerts:
                            # Save annotated image
                            alert_file = f"{output_dir}/alert_{alert.alert_type}_{frame_num}.jpg"
                            self._save_alert_image(frame, alert, alert_file)
                            
                            # Log alert
                            self._log_alert(alert)
                    
                    # Clean up
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                
                frame_num += 1
                
                # Progress update
                if frame_num % 300 == 0:
                    progress = (frame_num / total_frames * 100) if total_frames > 0 else 0
                    print(f"Progress: {progress:.1f}% (frame {frame_num})")
        
        except KeyboardInterrupt:
            print("\n✗ Interrupted by user")
        
        finally:
            cap.release()
            
            print(f"\n{'='*70}")
            print(f"PROCESSING SUMMARY")
            print(f"{'='*70}")
            print(f"Total frames: {frame_num}")
            print(f"Analyzed: {processed}")
            print(f"Alerts: {alert_count}")
            print(f"Output: {output_dir}")
            print(f"{'='*70}\n")
    
    
    def _save_alert_image(self, frame: np.ndarray, alert: TheftAlert, path: str):
        """Save annotated alert image."""
        annotated = frame.copy()
        
        # Draw bounding boxes
        for bbox in alert.bounding_boxes:
            x, y, w, h = bbox['x'], bbox['y'], bbox['width'], bbox['height']
            cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 0, 255), 2)
        
        # Add text overlay
        cv2.putText(annotated, f"{alert.alert_type} - {alert.severity}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(annotated, alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                   (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imwrite(path, annotated)
    
    
    def _log_alert(self, alert: TheftAlert):
        """Log alert to console and storage."""
        print(f"\n{'='*70}")
        print(f"🚨 {alert.severity} ALERT")
        print(f"{'='*70}")
        print(f"Type: {alert.alert_type}")
        print(f"Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Location: {alert.location}")
        print(f"Confidence: {alert.confidence:.1%}")
        print(f"Description: {alert.description}")
        print(f"{'='*70}\n")
        
        self.recent_alerts.append(alert)
        
        # Keep last 100 alerts
        if len(self.recent_alerts) > 100:
            self.recent_alerts = self.recent_alerts[-100:]
    
    
    def generate_report(self, output_file: str = "theft_report.json"):
        """Generate JSON report of all alerts."""
        report = {
            'generated': datetime.now().isoformat(),
            'total_alerts': len(self.recent_alerts),
            'by_type': {},
            'by_severity': {},
            'alerts': []
        }
        
        for alert in self.recent_alerts:
            # Count by type
            report['by_type'][alert.alert_type] = \
                report['by_type'].get(alert.alert_type, 0) + 1
            
            # Count by severity
            report['by_severity'][alert.severity] = \
                report['by_severity'].get(alert.severity, 0) + 1
            
            # Add details
            report['alerts'].append({
                'timestamp': alert.timestamp.isoformat(),
                'type': alert.alert_type,
                'severity': alert.severity,
                'confidence': alert.confidence,
                'location': alert.location,
                'description': alert.description
            })
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✓ Report saved: {output_file}")


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def main():
    """Demonstration of the theft detection system."""
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║           RETAIL THEFT DETECTION SYSTEM                      ║
║           Powered by Azure AI Vision                         ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Get credentials from environment
    endpoint = os.getenv("AZURE_VISION_ENDPOINT")
    key = os.getenv("AZURE_VISION_KEY")
    
    if not endpoint or not key:
        print("⚠️  ERROR: Azure credentials not set!\n")
        print("Set environment variables:")
        print("  export AZURE_VISION_ENDPOINT='https://your-resource.cognitiveservices.azure.com/'")
        print("  export AZURE_VISION_KEY='your-32-char-key'\n")
        print("Or get them from Azure Portal:")
        print("  1. Create Computer Vision resource")
        print("  2. Go to Keys and Endpoint")
        print("  3. Copy Key 1 and Endpoint\n")
        return
    
    # Initialize detector
    detector = RetailTheftDetector(endpoint, key)
    
    # Example 1: Analyze single image
    print("\nExample 1: Single Image Analysis")
    print("="*70)
    
    test_image = "store_frame.jpg"
    if os.path.exists(test_image):
        alerts = detector.analyze_frame(test_image)
        print(f"\nResult: {len(alerts)} alert(s) generated")
    else:
        print(f"⚠️  Test image not found: {test_image}")
    
    # Example 2: Process video
    print("\nExample 2: Video Processing")
    print("="*70)
    
    video_file = "store_footage.mp4"
    if os.path.exists(video_file):
        detector.process_video(video_file, "./theft_alerts")
        detector.generate_report("theft_report.json")
    else:
        print(f"⚠️  Video not found: {video_file}")
        print("  Use 0 to test with webcam")
    
    print("\n" + "="*70)
    print("Demo Complete")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
