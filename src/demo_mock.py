"""
Mock Azure Vision Client for Demo Mode
=======================================

Provides mock Azure AI Vision responses for demonstration purposes.

Author: AI-102 Study Implementation
"""

from unittest.mock import MagicMock

try:
    from .retail_theft_detection import RetailTheftDetector
    from .vision_analyzer import VisionAnalyzer
    from .zone_monitor import ZoneMonitor
    from .alert_manager import AlertManager
    from .detection_orchestrator import DetectionOrchestrator
except ImportError:
    from retail_theft_detection import RetailTheftDetector
    from vision_analyzer import VisionAnalyzer
    from zone_monitor import ZoneMonitor
    from alert_manager import AlertManager
    from detection_orchestrator import DetectionOrchestrator


class MockVisionClient:
    """Mock Azure Vision client for demo mode."""
    
    def analyze(self, image_data, visual_features):
        """
        Return mock analysis results.
        
        Args:
            image_data: Binary image data (unused in mock)
            visual_features: Requested features (unused in mock)
            
        Returns:
            Mock analysis result object
        """
        # Create mock person detection
        mock_person = MagicMock()
        mock_person.bounding_box = MagicMock(x=50, y=100, width=150, height=300)
        mock_person.confidence = 0.92
        
        # Create mock object (bag)
        mock_tag = MagicMock()
        mock_tag.name = "bag"
        mock_tag.confidence = 0.85
        
        mock_object = MagicMock()
        mock_object.tags = [mock_tag]
        mock_object.bounding_box = MagicMock(x=80, y=250, width=50, height=40)
        
        # Create mock tags
        mock_tag1 = MagicMock()
        mock_tag1.name = "person"
        mock_tag1.confidence = 0.95
        
        mock_tag2 = MagicMock()
        mock_tag2.name = "indoor"
        mock_tag2.confidence = 0.88
        
        mock_tag3 = MagicMock()
        mock_tag3.name = "retail"
        mock_tag3.confidence = 0.82
        
        # Create result object
        mock_result = MagicMock()
        mock_result.people = MagicMock(list=[mock_person])
        mock_result.objects = MagicMock(list=[mock_object])
        mock_result.tags = MagicMock(list=[mock_tag1, mock_tag2, mock_tag3])
        mock_result.caption = MagicMock(text="A person with a bag in a retail store")
        
        return mock_result


def create_mock_detector() -> RetailTheftDetector:
    """
    Create a detector with mocked Azure Vision client for demo.
    
    Returns:
        RetailTheftDetector with mock vision client
    """
    # Create detector with dummy credentials
    print("Initializing demo detector...")
    
    # Create components
    vision_analyzer = VisionAnalyzer(
        endpoint="https://demo.cognitiveservices.azure.com/",
        key="demo-key-32-characters-long-xxxx"
    )
    
    # Replace with mock client
    vision_analyzer._client = MockVisionClient()
    
    zone_monitor = ZoneMonitor()
    alert_manager = AlertManager()
    
    # Create orchestrator
    orchestrator = DetectionOrchestrator(
        vision_analyzer=vision_analyzer,
        zone_monitor=zone_monitor,
        alert_manager=alert_manager
    )
    
    # Create detector with mocked components
    detector = RetailTheftDetector.__new__(RetailTheftDetector)
    detector._vision_analyzer = vision_analyzer
    detector._zone_monitor = zone_monitor
    detector._alert_manager = alert_manager
    detector._orchestrator = orchestrator
    
    return detector
