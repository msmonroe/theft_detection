#!/usr/bin/env python3
"""
Retail Theft Detection System - Main Entry Point
=================================================

This is the main entry point for running the theft detection system.

Usage:
    python main.py                    # Run in demo mode
    python main.py --production       # Run with Azure credentials
    python main.py --image path.jpg   # Analyze single image
    python main.py --video path.mp4   # Process video

Author: AI-102 Study Implementation
"""

import sys
import os

# Add src directory to Python path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import and run the main function
if __name__ == "__main__":
    # Import after path is set up
    import retail_theft_detection
    retail_theft_detection.main()
