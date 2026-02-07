"""
Unit Tests for Retail Theft Detection System
=============================================

Comprehensive test suite covering:
- Azure AI Vision integration
- Detection logic
- Zone monitoring
- Alert generation
- Performance tracking
- Error handling

Run tests with:
    python -m pytest test_theft_detection.py -v
    
Or with coverage:
    python -m pytest test_theft_detection.py -v --cov=retail_theft_detection --cov-report=html

Author: AI-102 Study Implementation
"""

import unittest
import os
import json
import logging
import tempfile
import shutil
import time
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime
from typing import List, Dict

import numpy as np
import cv2

# Import the modules to test
# Note: Adjust import paths based on your project structure
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from retail_theft_detection import (
    RetailTheftDetector,
    DetectionZone,
    TheftAlert,
    ThreatLevel
)

from logging_instrumentation import (
    TheftDetectionLogger,
    PerformanceMonitor
)


class TestDetectionZone(unittest.TestCase):
    """Test cases for DetectionZone data class."""
    
    def test_zone_creation(self):
        """Test creating a detection zone."""
        zone = DetectionZone(
            name="Test_Zone",
            coordinates=[(0, 0), (100, 0), (100, 100), (0, 100)],
            is_restricted=True,
            alert_on_loitering=True,
            max_loiter_seconds=120
        )
        
        self.assertEqual(zone.name, "Test_Zone")
        self.assertEqual(len(zone.coordinates), 4)
        self.assertTrue(zone.is_restricted)
        self.assertTrue(zone.alert_on_loitering)
        self.assertEqual(zone.max_loiter_seconds, 120)
    
    
    def test_zone_defaults(self):
        """Test zone default values."""
        zone = DetectionZone(
            name="Simple_Zone",
            coordinates=[(0, 0), (50, 50)]
        )
        
        self.assertFalse(zone.is_restricted)
        self.assertFalse(zone.alert_on_loitering)
        self.assertEqual(zone.max_loiter_seconds, 120)


class TestTheftAlert(unittest.TestCase):
    """Test cases for TheftAlert data class."""
    
    def test_alert_creation(self):
        """Test creating a theft alert."""
        alert = TheftAlert(
            timestamp=datetime.now(),
            alert_type="TEST_ALERT",
            confidence=0.85,
            location="Test_Zone",
            description="Test alert description",
            image_path="/path/to/image.jpg",
            bounding_boxes=[{'x': 10, 'y': 20, 'width': 100, 'height': 200}],
            severity="MEDIUM"
        )
        
        self.assertEqual(alert.alert_type, "TEST_ALERT")
        self.assertEqual(alert.confidence, 0.85)
        self.assertEqual(alert.location, "Test_Zone")
        self.assertEqual(alert.severity, "MEDIUM")
        self.assertEqual(len(alert.bounding_boxes), 1)


class TestRetailTheftDetector(unittest.TestCase):
    """Test cases for the main RetailTheftDetector class."""
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Create a temporary directory for test outputs
        self.test_dir = tempfile.mkdtemp()
        
        # Mock Azure credentials
        self.mock_endpoint = "https://test.cognitiveservices.azure.com/"
        self.mock_key = "0123456789abcdef0123456789abcdef"
        
        # Create mock Vision client
        self.mock_vision_client = MagicMock()
        
        # Patch the ImageAnalysisClient to return our mock
        self.patcher = patch('retail_theft_detection.ImageAnalysisClient')
        self.mock_client_class = self.patcher.start()
        self.mock_client_class.return_value = self.mock_vision_client
    
    
    def tearDown(self):
        """Clean up after each test."""
        # Stop the patcher
        self.patcher.stop()
        
        # Remove temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    
    def test_detector_initialization(self):
        """Test detector initialization."""
        detector = RetailTheftDetector(
            endpoint=self.mock_endpoint,
            key=self.mock_key
        )
        
        # Verify client was created
        self.mock_client_class.assert_called_once()
        
        # Verify zones were initialized
        self.assertGreater(len(detector.zones), 0)
        
        # Verify tracking structures were initialized
        self.assertIsInstance(detector.tracked_people, dict)
        self.assertIsInstance(detector.recent_alerts, list)
    
    
    def test_point_in_polygon(self):
        """Test point-in-polygon detection."""
        detector = RetailTheftDetector(
            endpoint=self.mock_endpoint,
            key=self.mock_key
        )
        
        # Define a square polygon
        polygon = [(0, 0), (100, 0), (100, 100), (0, 100)]
        
        # Test points inside
        self.assertTrue(detector._point_in_polygon((50, 50), polygon))
        self.assertTrue(detector._point_in_polygon((10, 10), polygon))
        self.assertTrue(detector._point_in_polygon((90, 90), polygon))
        
        # Test points outside
        self.assertFalse(detector._point_in_polygon((150, 50), polygon))
        self.assertFalse(detector._point_in_polygon((50, 150), polygon))
        self.assertFalse(detector._point_in_polygon((-10, 50), polygon))
    
    
    def test_get_zone_for_location(self):
        """Test finding zone for a given location."""
        detector = RetailTheftDetector(
            endpoint=self.mock_endpoint,
            key=self.mock_key
        )
        
        # Add a test zone
        test_zone = DetectionZone(
            name="Test_Zone",
            coordinates=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        detector.zones = [test_zone]
        
        # Test location inside zone
        zone = detector._get_zone_for_location(50, 50)
        self.assertIsNotNone(zone)
        self.assertEqual(zone.name, "Test_Zone")
        
        # Test location outside zone
        zone = detector._get_zone_for_location(150, 150)
        self.assertIsNone(zone)
    
    
    def test_calculate_distance(self):
        """Test bounding box distance calculation."""
        detector = RetailTheftDetector(
            endpoint=self.mock_endpoint,
            key=self.mock_key
        )
        
        loc1 = {'x': 0, 'y': 0, 'width': 10, 'height': 10}
        loc2 = {'x': 30, 'y': 40, 'width': 10, 'height': 10}
        
        # Distance between centers should be 50 (3-4-5 triangle)
        distance = detector._calc_distance(loc1, loc2)
        self.assertAlmostEqual(distance, 50.0, places=1)
    
    
    def test_track_person(self):
        """Test person tracking across frames."""
        detector = RetailTheftDetector(
            endpoint=self.mock_endpoint,
            key=self.mock_key
        )
        
        # First detection
        location1 = {'x': 100, 'y': 100, 'width': 50, 'height': 100}
        person_id1 = detector._track_person(location1, frame_number=1)
        
        self.assertIn(person_id1, detector.tracked_people)
        self.assertEqual(detector.tracked_people[person_id1]['first_frame'], 1)
        self.assertEqual(len(detector.tracked_people[person_id1]['history']), 1)
        
        # Second detection (close to first - should be same person)
        location2 = {'x': 105, 'y': 105, 'width': 50, 'height': 100}
        person_id2 = detector._track_person(location2, frame_number=2)
        
        self.assertEqual(person_id1, person_id2)  # Same person ID
        self.assertEqual(len(detector.tracked_people[person_id1]['history']), 2)
        
        # Third detection (far from first - should be new person)
        location3 = {'x': 500, 'y': 500, 'width': 50, 'height': 100}
        person_id3 = detector._track_person(location3, frame_number=2)
        
        self.assertNotEqual(person_id1, person_id3)  # Different person ID
    
    
    def test_calculate_dwell_time(self):
        """Test dwell time calculation."""
        detector = RetailTheftDetector(
            endpoint=self.mock_endpoint,
            key=self.mock_key
        )
        
        # Track a person for multiple frames
        person_id = "person_0"
        detector.tracked_people[person_id] = {
            'first_frame': 0,
            'last_frame': 90,
            'history': []
        }
        
        # Calculate dwell time (90 frames at 30 fps = 3 seconds)
        dwell_time = detector._calculate_dwell_time(person_id, current_frame=90)
        self.assertAlmostEqual(dwell_time, 3.0, places=1)
    
    
    @patch('retail_theft_detection.open', create=True)
    def test_analyze_frame_with_mocked_api(self, mock_open):
        """Test frame analysis with mocked Azure API response."""
        detector = RetailTheftDetector(
            endpoint=self.mock_endpoint,
            key=self.mock_key
        )
        
        # Create mock image data
        mock_file = MagicMock()
        mock_file.read.return_value = b'fake_image_data'
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Create mock Azure API response
        mock_person = MagicMock()
        mock_person.bounding_box = MagicMock(x=100, y=100, width=50, height=100)
        mock_person.confidence = 0.95
        
        mock_result = MagicMock()
        mock_result.people = MagicMock(list=[mock_person])
        mock_result.objects = MagicMock(list=[])
        mock_result.tags = MagicMock(list=[])
        mock_result.caption = MagicMock(text="A person in a store")
        
        self.mock_vision_client.analyze.return_value = mock_result
        
        # Analyze frame
        alerts = detector.analyze_frame("test_image.jpg", frame_number=1)
        
        # Verify API was called
        self.mock_vision_client.analyze.assert_called_once()
        
        # Verify alerts is a list
        self.assertIsInstance(alerts, list)
    
    
    def test_detect_suspicious_objects(self):
        """Test suspicious object detection logic."""
        detector = RetailTheftDetector(
            endpoint=self.mock_endpoint,
            key=self.mock_key
        )
        
        # Create mock object detection results
        mock_tag = MagicMock()
        mock_tag.name = "laptop"
        mock_tag.confidence = 0.9
        
        mock_object = MagicMock()
        mock_object.tags = [mock_tag]
        mock_object.bounding_box = MagicMock(x=700, y=100, width=100, height=50)
        
        mock_result = MagicMock()
        mock_result.objects = MagicMock(list=[mock_object])
        mock_result.people = None
        mock_result.tags = None
        
        # Test with exit zone
        detector.zones = [
            DetectionZone(
                name="Exit_Zone",
                coordinates=[(700, 0), (800, 0), (800, 200), (700, 200)]
            )
        ]
        
        alerts = detector._detect_suspicious_objects(mock_result, "test.jpg")
        
        # Should detect laptop near exit
        self.assertGreater(len(alerts), 0)
        self.assertEqual(alerts[0].alert_type, "UNPAID_ITEM_AT_EXIT")
        self.assertIn("laptop", alerts[0].description.lower())


class TestLoggingInstrumentation(unittest.TestCase):
    """Test cases for logging and instrumentation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_log_dir = tempfile.mkdtemp()
    
    
    def tearDown(self):
        """Clean up after tests."""
        # Close all logging handlers to release file locks
        logging.shutdown()
        
        # Small delay to ensure file handles are released on Windows
        time.sleep(0.1)
        
        if os.path.exists(self.test_log_dir):
            try:
                shutil.rmtree(self.test_log_dir)
            except PermissionError:
                # On Windows, files might still be locked, try again after a short wait
                time.sleep(0.5)
                shutil.rmtree(self.test_log_dir)
    
    
    def test_logger_initialization(self):
        """Test logger initialization."""
        logger = TheftDetectionLogger(
            name="TestLogger",
            log_dir=self.test_log_dir,
            enable_console=False,
            enable_file=True
        )
        
        # Verify log directory was created
        self.assertTrue(os.path.exists(self.test_log_dir))
        
        # Verify logger was created
        self.assertIsNotNone(logger.logger)
    
    
    def test_logging_levels(self):
        """Test different logging levels."""
        logger = TheftDetectionLogger(
            name="TestLogger",
            log_dir=self.test_log_dir,
            enable_console=False,
            enable_file=True
        )
        
        # Test all logging levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Verify log file was created
        log_files = os.listdir(self.test_log_dir)
        self.assertGreater(len(log_files), 0)
    
    
    def test_performance_monitor(self):
        """Test performance monitoring."""
        logger = TheftDetectionLogger(
            name="TestLogger",
            log_dir=self.test_log_dir,
            enable_console=False,
            enable_file=True
        )
        
        monitor = PerformanceMonitor(logger)
        
        # Record some metrics
        monitor.record_api_call("test_endpoint", 150.5, success=True)
        monitor.record_frame_processing(1, 200.3)
        monitor.record_detection("TEST_EVENT", 0.85, "MEDIUM")
        monitor.record_alert("TEST_ALERT", "HIGH")
        
        # Get statistics
        stats = monitor.get_statistics()
        
        # Verify counters
        self.assertEqual(stats['counters']['total_api_calls'], 1)
        self.assertEqual(stats['counters']['total_frames'], 1)
        self.assertEqual(stats['counters']['total_detections'], 1)
        self.assertEqual(stats['counters']['total_alerts'], 1)
        
        # Verify averages
        self.assertIn('api_call_ms', stats['averages'])
        self.assertEqual(stats['averages']['api_call_ms'], 150.5)
    
    
    def test_metrics_export(self):
        """Test metrics export to JSON."""
        logger = TheftDetectionLogger(
            name="TestLogger",
            log_dir=self.test_log_dir,
            enable_console=False,
            enable_file=True
        )
        
        monitor = PerformanceMonitor(logger)
        monitor.record_api_call("test", 100.0, success=True)
        
        # Export metrics
        output_file = os.path.join(self.test_log_dir, "metrics.json")
        monitor.export_metrics(output_file)
        
        # Verify file was created
        self.assertTrue(os.path.exists(output_file))
        
        # Verify JSON content
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn('timestamp', data)
        self.assertIn('statistics', data)
        self.assertIn('metrics', data)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.mock_endpoint = "https://test.cognitiveservices.azure.com/"
        self.mock_key = "0123456789abcdef0123456789abcdef"
        
        # Create a test image
        self.test_image_path = os.path.join(self.test_dir, "test_frame.jpg")
        self._create_test_image(self.test_image_path)
        
        # Patch Azure client
        self.patcher = patch('retail_theft_detection.ImageAnalysisClient')
        self.mock_client_class = self.patcher.start()
        self.mock_vision_client = MagicMock()
        self.mock_client_class.return_value = self.mock_vision_client
    
    
    def tearDown(self):
        """Clean up after integration tests."""
        self.patcher.stop()
        
        # Close all logging handlers to release file locks
        logging.shutdown()
        
        # Small delay to ensure file handles are released on Windows
        time.sleep(0.1)
        
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except PermissionError:
                # On Windows, files might still be locked, try again after a short wait
                time.sleep(0.5)
                shutil.rmtree(self.test_dir)
    
    
    def _create_test_image(self, path: str):
        """Create a test image file."""
        # Create a simple 640x480 black image
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.imwrite(path, img)
    
    
    def test_end_to_end_detection(self):
        """Test complete detection workflow."""
        # Initialize detector with logging
        logger = TheftDetectionLogger(
            name="IntegrationTest",
            log_dir=self.test_dir,
            enable_console=False,
            enable_file=True
        )
        
        detector = RetailTheftDetector(
            endpoint=self.mock_endpoint,
            key=self.mock_key
        )
        
        # Mock Azure API response with person in restricted area
        mock_person = MagicMock()
        mock_person.bounding_box = MagicMock(x=50, y=450, width=50, height=100)
        mock_person.confidence = 0.95
        
        mock_result = MagicMock()
        mock_result.people = MagicMock(list=[mock_person])
        mock_result.objects = MagicMock(list=[])
        mock_result.tags = MagicMock(list=[])
        mock_result.caption = MagicMock(text="Person in store")
        
        self.mock_vision_client.analyze.return_value = mock_result
        
        # Set up zone that matches the person location
        detector.zones = [
            DetectionZone(
                name="Restricted_Zone",
                coordinates=[(0, 400), (200, 400), (200, 600), (0, 600)],
                is_restricted=True
            )
        ]
        
        # Analyze frame
        alerts = detector.analyze_frame(self.test_image_path, frame_number=1)
        
        # Verify results
        self.assertGreater(len(alerts), 0)
        
        # Should have restricted area violation
        restricted_alerts = [a for a in alerts if a.alert_type == "RESTRICTED_AREA_VIOLATION"]
        self.assertGreater(len(restricted_alerts), 0)
        
        # Generate report
        report_path = os.path.join(self.test_dir, "test_report.json")
        detector.generate_report(report_path)
        
        # Verify report was created
        self.assertTrue(os.path.exists(report_path))


# Test runner
if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
