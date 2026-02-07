"""
Detection Orchestrator
======================

Orchestrates the theft detection pipeline using Single Responsibility components.

Author: AI-102 Study Implementation
"""

from typing import List, Dict
import os

try:
    from .vision_analyzer import VisionAnalyzer
    from .person_tracker import PersonTracker
    from .zone_monitor import ZoneMonitor, DetectionZone
    from .alert_manager import AlertManager, TheftAlert
    from .behavior_analyzer import BehaviorAnalyzer
    from .geometry_utils import calculate_bounding_box_center
    from .config import DetectionThresholds
except ImportError:
    from vision_analyzer import VisionAnalyzer
    from person_tracker import PersonTracker
    from zone_monitor import ZoneMonitor, DetectionZone
    from alert_manager import AlertManager, TheftAlert
    from behavior_analyzer import BehaviorAnalyzer
    from geometry_utils import calculate_bounding_box_center
    from config import DetectionThresholds


class DetectionOrchestrator:
    """
    Coordinates all detection components to analyze frames for suspicious activity.
    
    This class follows the Orchestrator pattern, delegating specific
    responsibilities to specialized components.
    """
    
    def __init__(self,
                 vision_analyzer: VisionAnalyzer,
                 zone_monitor: ZoneMonitor,
                 alert_manager: AlertManager):
        """
        Initialize the detection orchestrator.
        
        Args:
            vision_analyzer: VisionAnalyzer instance
            zone_monitor: ZoneMonitor instance
            alert_manager: AlertManager instance
        """
        self._vision_analyzer = vision_analyzer
        self._zone_monitor = zone_monitor
        self._alert_manager = alert_manager
        self._person_tracker = PersonTracker()
        self._behavior_analyzer = BehaviorAnalyzer()
        
        print("✓ Detection Orchestrator initialized")
    
    def analyze_frame(self, image_path: str, frame_number: int = 0) -> List[TheftAlert]:
        """
        Run complete analysis pipeline on a single frame.
        
        Args:
            image_path: Path to image file
            frame_number: Frame number for tracking (0 for single images)
            
        Returns:
            List of generated TheftAlert objects
        """
        print(f"\n{'='*70}")
        print(f"Analyzing: {image_path}")
        print(f"{'='*70}")
        
        try:
            # Step 1: Get Azure AI Vision analysis
            analysis_result = self._vision_analyzer.analyze_image(image_path)
            
            # Step 2: Analyze people
            people_alerts = self._analyze_people(
                analysis_result, 
                image_path, 
                frame_number
            )
            
            # Step 3: Analyze objects
            object_alerts = self._analyze_objects(
                analysis_result, 
                image_path
            )
            
            # Step 4: Analyze behavior patterns
            behavior_alerts = self._analyze_behavior_patterns(
                analysis_result, 
                image_path,
                frame_number
            )
            
            all_alerts = people_alerts + object_alerts + behavior_alerts
            
            print(f"✓ Analysis complete: {len(all_alerts)} alert(s)")
            
            return all_alerts
            
        except Exception as e:
            print(f"✗ Error during analysis: {str(e)}")
            return []
    
    def _analyze_people(self, 
                       result, 
                       image_path: str, 
                       frame_number: int) -> List[TheftAlert]:
        """
        Analyze detected people for suspicious activity.
        
        Args:
            result: Azure AI Vision analysis result
            image_path: Path to analyzed image
            frame_number: Current frame number
            
        Returns:
            List of people-related alerts
        """
        alerts = []
        
        if not result.people:
            return alerts
        
        people_count = len(result.people.list)
        print(f"\n→ Analyzing {people_count} person/people")
        
        for idx, person in enumerate(result.people.list):
            bbox = person.bounding_box
            bounding_box = self._create_bounding_box_dict(bbox)
            confidence = person.confidence
            
            print(f"  Person {idx + 1}: ({bbox.x}, {bbox.y}) confidence={confidence:.2%}")
            
            # Track person across frames
            person_id = self._person_tracker.track_person(bounding_box, frame_number)
            
            # Find which zone they're in
            zone = self._zone_monitor.find_zone_for_bounding_box(bounding_box)
            
            if zone:
                # Check for restricted area violation
                alert = self._check_restricted_area_violation(
                    zone, bounding_box, confidence, image_path
                )
                if alert:
                    alerts.append(alert)
                
                # Check for loitering
                alert = self._check_loitering_violation(
                    zone, person_id, bounding_box, frame_number, image_path
                )
                if alert:
                    alerts.append(alert)
        
        return alerts
    
    def _analyze_objects(self, result, image_path: str) -> List[TheftAlert]:
        """
        Analyze detected objects for suspicious activity.
        
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
        
        for obj in result.objects.list:
            obj_name = obj.tags[0].name if obj.tags else "unknown"
            confidence = obj.tags[0].confidence if obj.tags else 0.0
            
            # Skip low confidence detections
            if confidence < DetectionThresholds.MIN_CONFIDENCE:
                continue
            
            bbox = obj.bounding_box
            bounding_box = self._create_bounding_box_dict(bbox)
            
            print(f"  Object: {obj_name} (confidence={confidence:.2%})")
            
            # Find zone
            zone = self._zone_monitor.find_zone_for_bounding_box(bounding_box)
            
            if zone:
                # Check for high-value item at exit
                alert = self._check_high_value_at_exit(
                    obj_name, zone, bounding_box, confidence, image_path
                )
                if alert:
                    alerts.append(alert)
                
                # Log concealment items
                if self._behavior_analyzer.is_concealment_item(obj_name):
                    print(f"    ⓘ Concealment item: {obj_name}")
        
        return alerts
    
    def _analyze_behavior_patterns(self, 
                                   result, 
                                   image_path: str,
                                   frame_number: int) -> List[TheftAlert]:
        """
        Analyze behavior patterns from scene tags.
        
        Args:
            result: Azure AI Vision result
            image_path: Image path
            frame_number: Current frame number
            
        Returns:
            List of behavior-related alerts
        """
        alerts = []
        
        if not result.tags:
            return alerts
        
        print(f"\n→ Checking concealment patterns")
        
        # Extract high-confidence tags
        tags = [
            tag.name 
            for tag in result.tags.list 
            if tag.confidence > DetectionThresholds.MIN_CONFIDENCE
        ]
        
        # Check for concealment patterns
        pattern_description = self._behavior_analyzer.detect_concealment_patterns(tags)
        
        if pattern_description:
            alert = self._alert_manager.create_alert(
                alert_type="CONCEALMENT_PATTERN",
                confidence=DetectionThresholds.CONCEALMENT_CONFIDENCE,
                location="Unknown",
                description=pattern_description,
                image_path=image_path,
                bounding_boxes=[],
                severity="MEDIUM"
            )
            alerts.append(alert)
            print(f"  ⚠ MEDIUM: {pattern_description}")
        
        return alerts
    
    def _check_restricted_area_violation(self,
                                        zone: DetectionZone,
                                        bounding_box: Dict,
                                        confidence: float,
                                        image_path: str) -> TheftAlert:
        """Check for restricted area violation."""
        if not zone.is_restricted:
            return None
        
        alert = self._alert_manager.create_alert(
            alert_type="RESTRICTED_AREA_VIOLATION",
            confidence=confidence,
            location=zone.name,
            description=f"Unauthorized person in {zone.name}",
            image_path=image_path,
            bounding_boxes=[bounding_box],
            severity="CRITICAL"
        )
        
        print(f"    ⚠ CRITICAL: Restricted area violation!")
        
        return alert
    
    def _check_loitering_violation(self,
                                  zone: DetectionZone,
                                  person_id: str,
                                  bounding_box: Dict,
                                  frame_number: int,
                                  image_path: str) -> TheftAlert:
        """Check for loitering violation."""
        if not zone.alert_on_loitering:
            return None
        
        tracking_data = self._person_tracker.get_tracking_data(person_id)
        if not tracking_data:
            return None
        
        should_alert = self._behavior_analyzer.should_alert_for_loitering(
            tracking_data,
            frame_number,
            zone.max_loiter_seconds
        )
        
        if not should_alert:
            return None
        
        dwell_time = tracking_data.calculate_dwell_time(frame_number)
        
        alert = self._alert_manager.create_alert(
            alert_type="LOITERING",
            confidence=0.85,
            location=zone.name,
            description=f"Person loitering {dwell_time:.0f}s in {zone.name}",
            image_path=image_path,
            bounding_boxes=[bounding_box],
            severity="MEDIUM"
        )
        
        print(f"    ⚠ MEDIUM: Loitering detected ({dwell_time:.0f}s)")
        
        return alert
    
    def _check_high_value_at_exit(self,
                                 object_name: str,
                                 zone: DetectionZone,
                                 bounding_box: Dict,
                                 confidence: float,
                                 image_path: str) -> TheftAlert:
        """Check for high-value item at exit."""
        if not self._behavior_analyzer.analyze_object_for_high_value(
            object_name, 
            zone.name
        ):
            return None
        
        adjusted_confidence = self._behavior_analyzer.calculate_confidence_for_high_value_exit(
            confidence
        )
        
        alert = self._alert_manager.create_alert(
            alert_type="UNPAID_ITEM_AT_EXIT",
            confidence=adjusted_confidence,
            location=zone.name,
            description=f"High-value {object_name} detected at exit",
            image_path=image_path,
            bounding_boxes=[bounding_box],
            severity="HIGH"
        )
        
        print(f"    ⚠ HIGH: High-value item at exit!")
        
        return alert
    
    def _create_bounding_box_dict(self, bbox) -> Dict:
        """
        Create a standardized bounding box dictionary.
        
        Args:
            bbox: Azure bounding box object
            
        Returns:
            Dictionary with x, y, width, height
        """
        return {
            'x': bbox.x,
            'y': bbox.y,
            'width': bbox.width,
            'height': bbox.height
        }
    
    @property
    def person_tracker(self) -> PersonTracker:
        """Get the person tracker."""
        return self._person_tracker
    
    @property
    def alert_manager(self) -> AlertManager:
        """Get the alert manager."""
        return self._alert_manager
