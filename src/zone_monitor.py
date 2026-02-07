"""
Zone Monitor Module
===================

Handles monitoring of detection zones and zone violations following SRP.

Author: AI-102 Study Implementation
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass

try:
    from .geometry_utils import point_in_polygon, calculate_bounding_box_center
    from .config import DefaultZones, ZoneDefinition
    from .validators import validate_polygon
except ImportError:
    from geometry_utils import point_in_polygon, calculate_bounding_box_center
    from config import DefaultZones, ZoneDefinition
    from validators import validate_polygon


@dataclass
class DetectionZone:
    """
    Represents a monitoring zone in the retail store.
    
    Zones are used to:
    - Detect unauthorized access to restricted areas
    - Monitor high-value merchandise areas
    - Track customer flow
    - Detect unusual dwell times
    """
    
    name: str
    coordinates: List[Tuple[int, int]]
    is_restricted: bool = False
    alert_on_loitering: bool = False
    max_loiter_seconds: int = 120
    
    def __post_init__(self):
        """Validate zone data after initialization."""
        if not validate_polygon(self.coordinates):
            raise ValueError(f"Invalid polygon coordinates for zone '{self.name}'")
    
    def contains_point(self, x: int, y: int) -> bool:
        """
        Check if a point is within this zone.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if point is inside zone
        """
        return point_in_polygon((x, y), self.coordinates)
    
    def contains_bounding_box(self, bounding_box: dict) -> bool:
        """
        Check if a bounding box center is within this zone.
        
        Args:
            bounding_box: Dictionary with x, y, width, height
            
        Returns:
            True if bounding box center is inside zone
        """
        center_x, center_y = calculate_bounding_box_center(bounding_box)
        return self.contains_point(int(center_x), int(center_y))


class ZoneMonitor:
    """
    Monitors detection zones and identifies zone-based violations.
    
    Responsibilities:
    - Maintain list of monitoring zones
    - Determine which zone a location belongs to
    - Check for zone violations
    """
    
    def __init__(self, zones: Optional[List[DetectionZone]] = None):
        """
        Initialize the zone monitor.
        
        Args:
            zones: List of DetectionZone objects (uses defaults if None)
        """
        if zones is None:
            self._zones = self._create_default_zones()
        else:
            self._zones = zones
        
        print(f"✓ Zone Monitor initialized with {len(self._zones)} zone(s)")
    
    def find_zone_for_point(self, x: int, y: int) -> Optional[DetectionZone]:
        """
        Find which zone contains a specific point.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            DetectionZone if point is in a zone, None otherwise
        """
        for zone in self._zones:
            if zone.contains_point(x, y):
                return zone
        return None
    
    def find_zone_for_bounding_box(self, bounding_box: dict) -> Optional[DetectionZone]:
        """
        Find which zone contains a bounding box center.
        
        Args:
            bounding_box: Dictionary with x, y, width, height
            
        Returns:
            DetectionZone if bounding box is in a zone, None otherwise
        """
        center_x, center_y = calculate_bounding_box_center(bounding_box)
        return self.find_zone_for_point(int(center_x), int(center_y))
    
    def is_in_restricted_zone(self, x: int, y: int) -> bool:
        """
        Check if a point is in a restricted zone.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if point is in restricted zone
        """
        zone = self.find_zone_for_point(x, y)
        return zone is not None and zone.is_restricted
    
    def should_alert_on_loitering(self, x: int, y: int) -> bool:
        """
        Check if loitering alerts are enabled for this location.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if loitering alerts are enabled for this zone
        """
        zone = self.find_zone_for_point(x, y)
        return zone is not None and zone.alert_on_loitering
    
    def get_all_zones(self) -> List[DetectionZone]:
        """
        Get all monitoring zones.
        
        Returns:
            List of DetectionZone objects
        """
        return self._zones.copy()
    
    def add_zone(self, zone: DetectionZone) -> None:
        """
        Add a new monitoring zone.
        
        Args:
            zone: DetectionZone to add
        """
        self._zones.append(zone)
    
    def _create_default_zones(self) -> List[DetectionZone]:
        """
        Create default zones from configuration.
        
        Returns:
            List of DetectionZone objects
        """
        zone_definitions = DefaultZones.get_default_zones()
        
        return [
            DetectionZone(
                name=zd.name,
                coordinates=zd.coordinates,
                is_restricted=zd.is_restricted,
                alert_on_loitering=zd.alert_on_loitering,
                max_loiter_seconds=zd.max_loiter_seconds
            )
            for zd in zone_definitions
        ]
