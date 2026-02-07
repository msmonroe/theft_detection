"""
Configuration and Constants for Retail Theft Detection System
==============================================================

This module centralizes all configuration values and magic numbers,
following the Clean Code principle of avoiding magic numbers in code.

Author: AI-102 Study Implementation
"""

from dataclasses import dataclass
from typing import List, Tuple


# =============================================================================
# DETECTION THRESHOLDS
# =============================================================================

class DetectionThresholds:
    """Confidence and detection thresholds."""
    
    # Minimum confidence score for accepting detections (0.0 - 1.0)
    MIN_CONFIDENCE = 0.6
    
    # Confidence threshold for concealment pattern detection
    CONCEALMENT_CONFIDENCE = 0.70
    
    # Minimum confidence for object detection
    MIN_OBJECT_CONFIDENCE = 0.6


# =============================================================================
# TIME THRESHOLDS
# =============================================================================

class TimeThresholds:
    """Time-based thresholds for behavior detection."""
    
    # Default maximum loitering time in seconds (3 minutes)
    DEFAULT_LOITER_SECONDS = 180
    
    # High-value area loitering threshold in seconds (2 minutes)
    HIGH_VALUE_LOITER_SECONDS = 120
    
    # Restricted area loitering threshold in seconds (1 minute)
    RESTRICTED_LOITER_SECONDS = 60


# =============================================================================
# TRACKING CONFIGURATION
# =============================================================================

class TrackingConfig:
    """Configuration for person tracking across frames."""
    
    # Maximum distance in pixels for matching people across frames
    MAX_TRACKING_DISTANCE_PIXELS = 100
    
    # Rapid movement threshold in pixels per second
    RAPID_MOVEMENT_THRESHOLD = 500
    
    # Assumed frames per second for video processing
    DEFAULT_FPS = 30
    
    # Number of recent positions to keep for behavior analysis
    POSITION_HISTORY_SIZE = 5
    
    # Frame skip interval for video processing (process every Nth frame)
    FRAME_SKIP_INTERVAL = 30  # ~1 frame per second at 30fps


# =============================================================================
# ALERT MANAGEMENT
# =============================================================================

class AlertConfig:
    """Configuration for alert generation and management."""
    
    # Maximum number of recent alerts to keep in memory
    MAX_RECENT_ALERTS = 100
    
    # High-value item confidence multiplier for exit detection
    HIGH_VALUE_EXIT_CONFIDENCE_MULTIPLIER = 0.9


# =============================================================================
# ITEM CATEGORIES
# =============================================================================

class ItemCategories:
    """Categories of items to monitor."""
    
    # Items considered high-value that trigger alerts near exits
    HIGH_VALUE_ITEMS = [
        'laptop',
        'phone',
        'tablet',
        'camera',
        'jewelry',
        'watch',
        'electronics'
    ]
    
    # Items that could be used to conceal merchandise
    CONCEALMENT_ITEMS = [
        'bag',
        'backpack',
        'purse',
        'jacket',
        'coat',
        'luggage'
    ]


# =============================================================================
# SUSPICIOUS BEHAVIOR PATTERNS
# =============================================================================

class BehaviorPatterns:
    """Patterns that indicate suspicious behavior."""
    
    # Tuple format: (tags_list, description)
    SUSPICIOUS_PATTERNS = [
        (['person', 'bag', 'clothing'], "Person with bag near clothing"),
        (['person', 'backpack', 'electronics'], "Person with backpack near electronics"),
        (['person', 'reaching'], "Person reaching for items"),
    ]


# =============================================================================
# ZONE DEFINITIONS
# =============================================================================

@dataclass
class ZoneDefinition:
    """Template for creating detection zones."""
    
    name: str
    coordinates: List[Tuple[int, int]]
    is_restricted: bool = False
    alert_on_loitering: bool = False
    max_loiter_seconds: int = TimeThresholds.DEFAULT_LOITER_SECONDS


class DefaultZones:
    """Default zone configurations for a typical retail store."""
    
    @staticmethod
    def get_default_zones() -> List[ZoneDefinition]:
        """
        Get default monitoring zones for a retail store.
        
        Returns:
            List of ZoneDefinition objects
            
        Note:
            In production, these should be loaded from a configuration file
            or database and calibrated to match actual camera field of view.
        """
        return [
            ZoneDefinition(
                name="Checkout_Counter",
                coordinates=[(0, 0), (300, 0), (300, 200), (0, 200)],
                alert_on_loitering=True,
                max_loiter_seconds=TimeThresholds.DEFAULT_LOITER_SECONDS
            ),
            ZoneDefinition(
                name="Electronics_Display",
                coordinates=[(300, 0), (600, 0), (600, 300), (300, 300)],
                alert_on_loitering=True,
                max_loiter_seconds=TimeThresholds.HIGH_VALUE_LOITER_SECONDS
            ),
            ZoneDefinition(
                name="Exit_Zone",
                coordinates=[(700, 0), (1000, 0), (1000, 200), (700, 200)],
                alert_on_loitering=False
            ),
            ZoneDefinition(
                name="Employee_Storage",
                coordinates=[(0, 400), (200, 400), (200, 600), (0, 600)],
                is_restricted=True
            )
        ]


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

class LoggingConfig:
    """Configuration for logging and instrumentation."""
    
    # Maximum number of metrics to keep in memory
    MAX_METRICS_IN_MEMORY = 1000
    
    # Number of days to retain log files
    LOG_RETENTION_DAYS = 30
    
    # Default log directory
    DEFAULT_LOG_DIR = "./logs"


# =============================================================================
# FILE PATHS AND OUTPUT
# =============================================================================

class FilePaths:
    """Default file paths for output and reports."""
    
    DEFAULT_ALERT_DIR = "./alerts"
    DEFAULT_REPORT_FILE = "theft_report.json"
    DEMO_IMAGE_FILE = "demo_store.jpg"
    TEMP_FRAME_FILE = "temp_frame.jpg"


# =============================================================================
# API CONFIGURATION
# =============================================================================

class AzureVisionConfig:
    """Configuration for Azure AI Vision API."""
    
    # Visual features to request from Azure AI Vision
    # Note: Each feature has an associated cost
    VISUAL_FEATURES_REQUESTED = [
        'PEOPLE',   # Detect people and locations
        'OBJECTS',  # Detect objects (bags, items, etc.)
        'TAGS',     # Get scene understanding tags
        'CAPTION'   # Get natural language description
    ]


# =============================================================================
# VALIDATION RULES
# =============================================================================

class ValidationRules:
    """Rules for input validation."""
    
    # Minimum number of vertices for a valid polygon zone
    MIN_POLYGON_VERTICES = 3
    
    # Valid severity levels for alerts
    VALID_SEVERITY_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    # Valid alert types
    VALID_ALERT_TYPES = [
        "RESTRICTED_AREA_VIOLATION",
        "LOITERING",
        "UNPAID_ITEM_AT_EXIT",
        "CONCEALMENT_PATTERN"
    ]
