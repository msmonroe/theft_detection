"""
Behavior Analyzer Module
========================

Analyzes behavior patterns for suspicious activity detection following SRP.

Author: AI-102 Study Implementation
"""

from typing import List, Dict, Optional

try:
    from .config import (
        ItemCategories, 
        BehaviorPatterns, 
        DetectionThresholds,
        AlertConfig,
        TrackingConfig
    )
    from .geometry_utils import calculate_movement_speed
    from .person_tracker import PersonTracker, PersonTrackingData
except ImportError:
    from config import (
        ItemCategories, 
        BehaviorPatterns, 
        DetectionThresholds,
        AlertConfig,
        TrackingConfig
    )
    from geometry_utils import calculate_movement_speed
    from person_tracker import PersonTracker, PersonTrackingData


class BehaviorAnalyzer:
    """
    Analyzes behavior patterns to detect suspicious activities.
    
    Responsibilities:
    - Detect suspicious object combinations
    - Identify rapid/erratic movements
    - Detect concealment patterns
    - Analyze dwell time violations
    """
    
    def __init__(self):
        """Initialize the behavior analyzer."""
        print("✓ Behavior Analyzer initialized")
    
    def analyze_object_for_high_value(self, object_name: str, zone_name: str) -> bool:
        """
        Check if object is high-value and in suspicious location (like exit).
        
        Args:
            object_name: Name of detected object
            zone_name: Name of zone where object is located
            
        Returns:
            True if high-value object is in suspicious location
        """
        is_high_value = any(
            item in object_name.lower() 
            for item in ItemCategories.HIGH_VALUE_ITEMS
        )
        
        is_near_exit = 'exit' in zone_name.lower()
        
        return is_high_value and is_near_exit
    
    def is_concealment_item(self, object_name: str) -> bool:
        """
        Check if object could be used for concealment.
        
        Args:
            object_name: Name of detected object
            
        Returns:
            True if object is a concealment item
        """
        return any(
            item in object_name.lower() 
            for item in ItemCategories.CONCEALMENT_ITEMS
        )
    
    def detect_concealment_patterns(self, tags: List[str]) -> Optional[str]:
        """
        Detect suspicious tag combinations that suggest concealment.
        
        Args:
            tags: List of scene tags from Azure AI Vision
            
        Returns:
            Description of pattern if detected, None otherwise
        """
        normalized_tags = ' '.join(tag.lower() for tag in tags)
        
        for pattern_tags, description in BehaviorPatterns.SUSPICIOUS_PATTERNS:
            if all(tag in normalized_tags for tag in pattern_tags):
                return description
        
        return None
    
    def analyze_person_movement(self, 
                                tracking_data: PersonTrackingData,
                                current_frame: int) -> Dict[str, any]:
        """
        Analyze movement patterns of a tracked person.
        
        Args:
            tracking_data: PersonTrackingData object
            current_frame: Current frame number
            
        Returns:
            Dictionary with movement analysis:
                - is_rapid: bool
                - speed: float (pixels per second)
                - frames_tracked: int
        """
        result = {
            'is_rapid': False,
            'speed': 0.0,
            'frames_tracked': 0
        }
        
        positions = tracking_data.get_recent_positions(
            TrackingConfig.POSITION_HISTORY_SIZE
        )
        
        if len(positions) < 2:
            return result
        
        # Calculate timespan in seconds
        frames_used = len(positions)
        time_span = frames_used / TrackingConfig.DEFAULT_FPS
        
        # Calculate speed
        speed = calculate_movement_speed(positions, time_span)
        
        result['speed'] = speed
        result['frames_tracked'] = len(tracking_data.position_history)
        result['is_rapid'] = speed > TrackingConfig.RAPID_MOVEMENT_THRESHOLD
        
        return result
    
    def should_alert_for_loitering(self,
                                   tracking_data: PersonTrackingData,
                                   current_frame: int,
                                   max_loiter_seconds: int) -> bool:
        """
        Determine if person has been loitering too long.
        
        Args:
            tracking_data: PersonTrackingData object
            current_frame: Current frame number
            max_loiter_seconds: Maximum allowed loitering time
            
        Returns:
            True if loitering threshold exceeded
        """
        dwell_time = tracking_data.calculate_dwell_time(current_frame)
        return dwell_time > max_loiter_seconds
    
    def calculate_confidence_for_high_value_exit(self, base_confidence: float) -> float:
        """
        Calculate adjusted confidence for high-value item at exit.
        
        Args:
            base_confidence: Base confidence from object detection
            
        Returns:
            Adjusted confidence score
        """
        return base_confidence * AlertConfig.HIGH_VALUE_EXIT_CONFIDENCE_MULTIPLIER
