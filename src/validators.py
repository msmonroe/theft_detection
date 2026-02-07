"""
Validation Utilities for Retail Theft Detection System
=======================================================

Contains validation functions and utilities following Clean Code principles.

Author: AI-102 Study Implementation
"""

import os
from typing import List, Tuple, Optional
from pathlib import Path

try:
    from .config import ValidationRules
except ImportError:
    from config import ValidationRules


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_file_exists(file_path: str) -> None:
    """
    Validate that a file exists.
    
    Args:
        file_path: Path to the file
        
    Raises:
        ValidationError: If file does not exist
    """
    if not os.path.exists(file_path):
        raise ValidationError(f"File not found: {file_path}")


def validate_directory_exists(directory_path: str) -> None:
    """
    Validate that a directory exists, create if it doesn't.
    
    Args:
        directory_path: Path to the directory
    """
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def validate_confidence_score(confidence: float) -> None:
    """
    Validate that a confidence score is within valid range.
    
    Args:
        confidence: Confidence score to validate
        
    Raises:
        ValidationError: If confidence is not between 0.0 and 1.0
    """
    if not 0.0 <= confidence <= 1.0:
        raise ValidationError(
            f"Confidence score must be between 0.0 and 1.0, got {confidence}"
        )


def validate_polygon(coordinates: List[Tuple[int, int]]) -> bool:
    """
    Validate that polygon coordinates form a valid polygon.
    
    Args:
        coordinates: List of (x, y) coordinate tuples
        
    Returns:
        True if valid polygon, False otherwise
    """
    if not coordinates:
        return False
    
    if len(coordinates) < ValidationRules.MIN_POLYGON_VERTICES:
        return False
    
    try:
        for x, y in coordinates:
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                return False
    except (TypeError, ValueError):
        return False
    
    return True


def validate_severity_level(severity: str) -> None:
    """
    Validate that severity level is valid.
    
    Args:
        severity: Severity level string
        
    Raises:
        ValidationError: If severity is not a valid level
    """
    if severity not in ValidationRules.VALID_SEVERITY_LEVELS:
        raise ValidationError(
            f"Invalid severity level: {severity}. "
            f"Must be one of {ValidationRules.VALID_SEVERITY_LEVELS}"
        )


def validate_alert_type(alert_type: str) -> None:
    """
    Validate that alert type is valid.
    
    Args:
        alert_type: Alert type string
        
    Raises:
        ValidationError: If alert type is not valid
    """
    if alert_type not in ValidationRules.VALID_ALERT_TYPES:
        raise ValidationError(
            f"Invalid alert type: {alert_type}. "
            f"Must be one of {ValidationRules.VALID_ALERT_TYPES}"
        )


def validate_azure_endpoint(endpoint: str) -> None:
    """
    Validate Azure endpoint format.
    
    Args:
        endpoint: Azure endpoint URL
        
    Raises:
        ValidationError: If endpoint format is invalid
    """
    if not endpoint:
        raise ValidationError("Azure endpoint cannot be empty")
    
    if not endpoint.startswith(("http://", "https://")):
        raise ValidationError(
            f"Azure endpoint must start with http:// or https://, got: {endpoint}"
        )


def validate_azure_key(key: str) -> None:
    """
    Validate Azure subscription key format.
    
    Args:
        key: Azure subscription key
        
    Raises:
        ValidationError: If key format is invalid
    """
    if not key:
        raise ValidationError("Azure key cannot be empty")
    
    if len(key) != 32:
        raise ValidationError(
            f"Azure key should be 32 characters, got {len(key)} characters"
        )
