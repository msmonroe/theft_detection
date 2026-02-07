"""
Alert Manager Module
====================

Handles creation, storage, and management of theft alerts following SRP.

Author: AI-102 Study Implementation
"""

import json
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from .config import AlertConfig
    from .validators import validate_severity_level, validate_confidence_score
except ImportError:
    from config import AlertConfig
    from validators import validate_severity_level, validate_confidence_score


class ThreatLevel(Enum):
    """Enumeration of threat severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class TheftAlert:
    """Represents a detected suspicious activity."""
    
    timestamp: datetime
    alert_type: str
    confidence: float
    location: str
    description: str
    image_path: str
    bounding_boxes: List[Dict]
    severity: str = "MEDIUM"
    
    def __post_init__(self):
        """Validate alert data after initialization."""
        validate_severity_level(self.severity)
        validate_confidence_score(self.confidence)
    
    def to_dict(self) -> Dict:
        """
        Convert alert to dictionary format.
        
        Returns:
            Dictionary representation of the alert
        """
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class AlertManager:
    """
    Manages theft alerts including creation, storage, and reporting.
    
    Responsibilities:
    - Create properly formatted alerts
    - Store recent alerts in memory
    - Generate alert reports
    - Prevent duplicate alerts
    """
    
    def __init__(self):
        """Initialize the alert manager."""
        self._recent_alerts: List[TheftAlert] = []
        print("✓ Alert Manager initialized")
    
    def create_alert(self,
                    alert_type: str,
                    confidence: float,
                    location: str,
                    description: str,
                    image_path: str,
                    bounding_boxes: List[Dict],
                    severity: str = "MEDIUM") -> TheftAlert:
        """
        Create a new theft alert.
        
        Args:
            alert_type: Type of suspicious activity
            confidence: Confidence score (0.0 - 1.0)
            location: Zone or area name
            description: Human-readable description
            image_path: Path to evidence image
            bounding_boxes: List of detected object/person locations
            severity: Alert severity level
            
        Returns:
            TheftAlert object
        """
        alert = TheftAlert(
            timestamp=datetime.now(),
            alert_type=alert_type,
            confidence=confidence,
            location=location,
            description=description,
            image_path=image_path,
            bounding_boxes=bounding_boxes,
            severity=severity
        )
        
        self._add_alert(alert)
        self._log_alert_to_console(alert)
        
        return alert
    
    def get_recent_alerts(self, count: int = None) -> List[TheftAlert]:
        """
        Get recent alerts.
        
        Args:
            count: Number of recent alerts to return (None for all)
            
        Returns:
            List of TheftAlert objects
        """
        if count is None:
            return self._recent_alerts.copy()
        return self._recent_alerts[-count:]
    
    def get_alert_count(self) -> int:
        """
        Get total number of stored alerts.
        
        Returns:
            Number of alerts
        """
        return len(self._recent_alerts)
    
    def clear_alerts(self) -> None:
        """Clear all stored alerts."""
        self._recent_alerts.clear()
    
    def generate_report(self, output_file: str = "theft_report.json") -> Dict:
        """
        Generate a comprehensive JSON report of all alerts.
        
        Args:
            output_file: Path to output JSON file
            
        Returns:
            Report dictionary
        """
        report = self._build_report()
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✓ Report saved: {output_file}")
        
        return report
    
    def _add_alert(self, alert: TheftAlert) -> None:
        """
        Add alert to storage.
        
        Args:
            alert: TheftAlert to store
        """
        self._recent_alerts.append(alert)
        
        # Keep only recent alerts to limit memory usage
        if len(self._recent_alerts) > AlertConfig.MAX_RECENT_ALERTS:
            self._recent_alerts = self._recent_alerts[-AlertConfig.MAX_RECENT_ALERTS:]
    
    def _log_alert_to_console(self, alert: TheftAlert) -> None:
        """
        Log alert details to console.
        
        Args:
            alert: TheftAlert to log
        """
        print(f"\n{'='*70}")
        print(f"🚨 {alert.severity} ALERT")
        print(f"{'='*70}")
        print(f"Type: {alert.alert_type}")
        print(f"Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Location: {alert.location}")
        print(f"Confidence: {alert.confidence:.1%}")
        print(f"Description: {alert.description}")
        print(f"{'='*70}\n")
    
    def _build_report(self) -> Dict:
        """
        Build comprehensive alert report.
        
        Returns:
            Report dictionary
        """
        report = {
            'generated': datetime.now().isoformat(),
            'total_alerts': len(self._recent_alerts),
            'by_type': self._count_alerts_by_type(),
            'by_severity': self._count_alerts_by_severity(),
            'alerts': [alert.to_dict() for alert in self._recent_alerts]
        }
        
        return report
    
    def _count_alerts_by_type(self) -> Dict[str, int]:
        """
        Count alerts grouped by type.
        
        Returns:
            Dictionary of alert_type -> count
        """
        counts = {}
        for alert in self._recent_alerts:
            counts[alert.alert_type] = counts.get(alert.alert_type, 0) + 1
        return counts
    
    def _count_alerts_by_severity(self) -> Dict[str, int]:
        """
        Count alerts grouped by severity.
        
        Returns:
            Dictionary of severity -> count
        """
        counts = {}
        for alert in self._recent_alerts:
            counts[alert.severity] = counts.get(alert.severity, 0) + 1
        return counts
