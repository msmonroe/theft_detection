"""
Retail Theft Detection System - Refactored Source Code
=======================================================

This package contains the refactored theft detection system following
Clean Code principles and SOLID design patterns.

Main Components:
    - retail_theft_detection: Main entry point and facade
    - detection_orchestrator: Coordinates detection pipeline
    - vision_analyzer: Azure AI Vision integration
    - person_tracker: Person tracking across frames
    - zone_monitor: Zone monitoring and violations
    - alert_manager: Alert creation and management
    - behavior_analyzer: Behavior pattern analysis
    - geometry_utils: Geometric calculations
    - validators: Input validation
    - config: System configuration
    - demo_mock: Mock client for testing

Author: AI-102 Study Implementation
"""

from .retail_theft_detection import RetailTheftDetector, VideoProcessor
from .alert_manager import TheftAlert, ThreatLevel, AlertManager
from .zone_monitor import DetectionZone, ZoneMonitor
from .detection_orchestrator import DetectionOrchestrator

__version__ = "2.0.0"
__all__ = [
    'RetailTheftDetector',
    'VideoProcessor',
    'TheftAlert',
    'ThreatLevel',
    'AlertManager',
    'DetectionZone',
    'ZoneMonitor',
    'DetectionOrchestrator',
]
