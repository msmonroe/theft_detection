"""
Azure AI Vision Analyzer
=========================

Handles all interactions with Azure AI Vision API following Single Responsibility Principle.

Author: AI-102 Study Implementation
"""

from typing import List
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

try:
    from .validators import validate_azure_endpoint, validate_azure_key, validate_file_exists
    from .config import AzureVisionConfig
except ImportError:
    from validators import validate_azure_endpoint, validate_azure_key, validate_file_exists
    from config import AzureVisionConfig


class VisionAnalyzer:
    """
    Handles Azure AI Vision API calls for image analysis.
    
    This class is responsible only for communicating with Azure AI Vision
    and returning analysis results.
    """
    
    def __init__(self, endpoint: str, key: str):
        """
        Initialize the Azure AI Vision analyzer.
        
        Args:
            endpoint: Azure AI Vision endpoint URL
            key: Azure AI Vision subscription key
            
        Raises:
            ValidationError: If endpoint or key format is invalid
        """
        validate_azure_endpoint(endpoint)
        validate_azure_key(key)
        
        self._client = ImageAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
        self._endpoint = endpoint
        
        print(f"✓ Vision Analyzer initialized")
        print(f"  Endpoint: {endpoint}")
    
    def analyze_image(self, image_path: str):
        """
        Analyze an image using Azure AI Vision.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            ImageAnalysisResult from Azure AI Vision
            
        Raises:
            ValidationError: If image file doesn't exist
            Exception: If Azure API call fails
        """
        validate_file_exists(image_path)
        
        print(f"→ Analyzing image with Azure AI Vision...")
        
        image_data = self._read_image_file(image_path)
        visual_features = self._get_visual_features()
        
        result = self._client.analyze(
            image_data=image_data,
            visual_features=visual_features
        )
        
        self._log_analysis_result(result)
        
        return result
    
    def _read_image_file(self, image_path: str) -> bytes:
        """
        Read image file as binary data.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Binary image data
        """
        with open(image_path, 'rb') as f:
            return f.read()
    
    def _get_visual_features(self) -> List[VisualFeatures]:
        """
        Get the list of visual features to request from Azure.
        
        Returns:
            List of VisualFeatures enums
        """
        feature_map = {
            'PEOPLE': VisualFeatures.PEOPLE,
            'OBJECTS': VisualFeatures.OBJECTS,
            'TAGS': VisualFeatures.TAGS,
            'CAPTION': VisualFeatures.CAPTION
        }
        
        return [
            feature_map[feature_name]
            for feature_name in AzureVisionConfig.VISUAL_FEATURES_REQUESTED
            if feature_name in feature_map
        ]
    
    def _log_analysis_result(self, result) -> None:
        """
        Log the summary of analysis results.
        
        Args:
            result: Azure AI Vision analysis result
        """
        people_count = len(result.people.list) if result.people else 0
        object_count = len(result.objects.list) if result.objects else 0
        
        print(f"  ✓ People detected: {people_count}")
        print(f"  ✓ Objects detected: {object_count}")
        
        if result.caption:
            print(f"  ✓ Scene: {result.caption.text}")
    
    @property
    def endpoint(self) -> str:
        """Get the Azure endpoint URL."""
        return self._endpoint
