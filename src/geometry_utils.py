"""
Geometry Utilities for Retail Theft Detection System
=====================================================

Contains geometric calculation functions following Clean Code principles.

Author: AI-102 Study Implementation
"""

import math
from typing import Dict, List, Tuple
import numpy as np


def point_in_polygon(point: Tuple[int, int], 
                     polygon: List[Tuple[int, int]]) -> bool:
    """
    Determine if a point is inside a polygon using ray casting algorithm.
    
    Args:
        point: (x, y) coordinates of the point to test
        polygon: List of (x, y) vertices defining the polygon
        
    Returns:
        True if point is inside polygon, False otherwise
    """
    if not polygon or len(polygon) < 3:
        return False
    
    x, y = point
    n = len(polygon)
    inside = False
    
    try:
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if _is_point_on_ray(x, y, p1x, p1y, p2x, p2y):
                inside = not inside
            p1x, p1y = p2x, p2y
    except (TypeError, ValueError, IndexError):
        return False
    
    return inside


def _is_point_on_ray(x: float, y: float, 
                     p1x: float, p1y: float, 
                     p2x: float, p2y: float) -> bool:
    """
    Helper function to determine if a horizontal ray from point crosses edge.
    
    Args:
        x, y: Point coordinates
        p1x, p1y: First edge vertex
        p2x, p2y: Second edge vertex
        
    Returns:
        True if ray crosses edge
    """
    if y > min(p1y, p2y):
        if y <= max(p1y, p2y):
            if x <= max(p1x, p2x):
                if p1y != p2y:
                    xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        return True
    return False


def calculate_bounding_box_center(bbox: Dict) -> Tuple[float, float]:
    """
    Calculate the center point of a bounding box.
    
    Args:
        bbox: Dictionary with keys 'x', 'y', 'width', 'height'
        
    Returns:
        Tuple of (center_x, center_y)
    """
    center_x = bbox['x'] + bbox['width'] / 2
    center_y = bbox['y'] + bbox['height'] / 2
    return (center_x, center_y)


def calculate_distance_between_boxes(bbox1: Dict, bbox2: Dict) -> float:
    """
    Calculate Euclidean distance between centers of two bounding boxes.
    
    Args:
        bbox1: First bounding box
        bbox2: Second bounding box
        
    Returns:
        Euclidean distance in pixels
    """
    center1 = calculate_bounding_box_center(bbox1)
    center2 = calculate_bounding_box_center(bbox2)
    
    return calculate_euclidean_distance(center1, center2)


def calculate_euclidean_distance(point1: Tuple[float, float], 
                                 point2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two points.
    
    Args:
        point1: (x, y) coordinates of first point
        point2: (x, y) coordinates of second point
        
    Returns:
        Euclidean distance
    """
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def calculate_path_distance(positions: List[Dict]) -> float:
    """
    Calculate total distance traveled along a path of positions.
    
    Args:
        positions: List of bounding box dictionaries representing path
        
    Returns:
        Total distance in pixels
    """
    if len(positions) < 2:
        return 0.0
    
    total_distance = 0.0
    for i in range(len(positions) - 1):
        total_distance += calculate_distance_between_boxes(
            positions[i], 
            positions[i + 1]
        )
    
    return total_distance


def calculate_movement_speed(positions: List[Dict], 
                            time_span_seconds: float) -> float:
    """
    Calculate movement speed from a sequence of positions.
    
    Args:
        positions: List of bounding box positions over time
        time_span_seconds: Time span covered by positions
        
    Returns:
        Speed in pixels per second
    """
    if time_span_seconds <= 0:
        return 0.0
    
    distance = calculate_path_distance(positions)
    return distance / time_span_seconds
