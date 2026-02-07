"""
Logging and Instrumentation Module for Retail Theft Detection
==============================================================

This module provides comprehensive logging, monitoring, and instrumentation
capabilities for the retail theft detection system.

Features:
- Structured logging with rotation
- Performance metrics tracking
- Azure Application Insights integration
- Custom metrics and telemetry
- Error tracking and reporting

Author: AI-102 Study Implementation
"""

import logging
import time
import json
import sys
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps
from pathlib import Path

# For Azure Application Insights (optional)
try:
    from opencensus.ext.azure import metrics_exporter
    from opencensus.ext.azure.log_exporter import AzureLogHandler
    from opencensus.stats import aggregation as aggregation_module
    from opencensus.stats import measure as measure_module
    from opencensus.stats import stats as stats_module
    from opencensus.stats import view as view_module
    from opencensus.tags import tag_map as tag_map_module
    AZURE_INSIGHTS_AVAILABLE = True
except ImportError:
    AZURE_INSIGHTS_AVAILABLE = False


class TheftDetectionLogger:
    """
    Comprehensive logging system for theft detection.
    
    Provides:
    - Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - File rotation (daily rotation, max 30 days retention)
    - Console output for development
    - Structured JSON logging for production
    - Azure Application Insights integration
    """
    
    def __init__(self, 
                 name: str = "TheftDetection",
                 log_dir: str = "./logs",
                 log_level: int = logging.INFO,
                 enable_console: bool = True,
                 enable_file: bool = True,
                 enable_azure: bool = False,
                 azure_connection_string: Optional[str] = None):
        """
        Initialize the logging system.
        
        Args:
            name: Logger name (used as prefix in logs)
            log_dir: Directory to store log files
            log_level: Minimum log level (DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50)
            enable_console: Enable console output
            enable_file: Enable file logging
            enable_azure: Enable Azure Application Insights
            azure_connection_string: Azure Application Insights connection string
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create log directory if it doesn't exist
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Define log format
        # Format: [timestamp] [level] [module] - message
        self.log_format = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)8s] [%(name)s.%(funcName)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # JSON format for structured logging
        self.json_format = logging.Formatter(
            fmt='{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "function": "%(funcName)s", '
                '"line": %(lineno)d, "message": "%(message)s"}'
        )
        
        # Add console handler if enabled
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            console_handler.setFormatter(self.log_format)
            self.logger.addHandler(console_handler)
        
        # Add file handler if enabled
        if enable_file:
            # Main log file (all levels)
            file_handler = logging.handlers.TimedRotatingFileHandler(
                filename=self.log_dir / 'theft_detection.log',
                when='midnight',  # Rotate at midnight
                interval=1,       # Every 1 day
                backupCount=30,   # Keep 30 days of logs
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(self.log_format)
            self.logger.addHandler(file_handler)
            
            # Error log file (ERROR and CRITICAL only)
            error_handler = logging.handlers.TimedRotatingFileHandler(
                filename=self.log_dir / 'theft_detection_errors.log',
                when='midnight',
                interval=1,
                backupCount=30,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(self.log_format)
            self.logger.addHandler(error_handler)
            
            # JSON structured log file
            json_handler = logging.handlers.TimedRotatingFileHandler(
                filename=self.log_dir / 'theft_detection_json.log',
                when='midnight',
                interval=1,
                backupCount=30,
                encoding='utf-8'
            )
            json_handler.setLevel(log_level)
            json_handler.setFormatter(self.json_format)
            self.logger.addHandler(json_handler)
        
        # Add Azure Application Insights handler if enabled
        if enable_azure and AZURE_INSIGHTS_AVAILABLE and azure_connection_string:
            try:
                azure_handler = AzureLogHandler(
                    connection_string=azure_connection_string
                )
                azure_handler.setLevel(log_level)
                self.logger.addHandler(azure_handler)
                self.logger.info("Azure Application Insights logging enabled")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Azure logging: {e}")
        
        self.logger.info(f"Logger initialized: {name}")
        self.logger.info(f"Log directory: {log_dir}")
        self.logger.info(f"Log level: {logging.getLevelName(log_level)}")
    
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context."""
        self._log_with_context(logging.DEBUG, message, kwargs)
    
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context."""
        self._log_with_context(logging.INFO, message, kwargs)
    
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context."""
        self._log_with_context(logging.WARNING, message, kwargs)
    
    
    def error(self, message: str, **kwargs):
        """Log error message with optional context."""
        self._log_with_context(logging.ERROR, message, kwargs)
    
    
    def critical(self, message: str, **kwargs):
        """Log critical message with optional context."""
        self._log_with_context(logging.CRITICAL, message, kwargs)
    
    
    def exception(self, message: str, exc_info=True, **kwargs):
        """
        Log exception with full traceback.
        
        Args:
            message: Error message
            exc_info: Include exception info (default: True)
            **kwargs: Additional context
        """
        if kwargs:
            message = f"{message} | Context: {json.dumps(kwargs)}"
        self.logger.exception(message, exc_info=exc_info)
    
    
    def _log_with_context(self, level: int, message: str, context: Dict[str, Any]):
        """
        Internal method to log with additional context.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            context: Dictionary of additional context data
        """
        if context:
            # Add context as JSON string to message
            message = f"{message} | Context: {json.dumps(context, default=str)}"
        
        self.logger.log(level, message)
    
    
    def log_api_call(self, 
                     endpoint: str, 
                     duration_ms: float, 
                     status_code: Optional[int] = None,
                     error: Optional[str] = None):
        """
        Log Azure API call metrics.
        
        Args:
            endpoint: API endpoint called
            duration_ms: Call duration in milliseconds
            status_code: HTTP status code (if applicable)
            error: Error message if call failed
        """
        context = {
            'endpoint': endpoint,
            'duration_ms': duration_ms,
            'status_code': status_code
        }
        
        if error:
            self.error(f"API call failed: {endpoint}", error=error, **context)
        else:
            self.info(f"API call successful: {endpoint}", **context)
    
    
    def log_detection_event(self, 
                           event_type: str, 
                           confidence: float,
                           location: str,
                           severity: str):
        """
        Log theft detection event.
        
        Args:
            event_type: Type of detection event
            confidence: Confidence score
            location: Location where detected
            severity: Alert severity
        """
        self.warning(
            f"Detection event: {event_type}",
            event_type=event_type,
            confidence=confidence,
            location=location,
            severity=severity
        )
    
    
    def log_performance_metric(self, 
                               metric_name: str, 
                               value: float, 
                               unit: str = "ms"):
        """
        Log performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
        """
        self.debug(
            f"Performance metric: {metric_name}",
            metric=metric_name,
            value=value,
            unit=unit
        )


class PerformanceMonitor:
    """
    Performance monitoring and metrics collection.
    
    Tracks:
    - API call latency
    - Frame processing time
    - Detection accuracy
    - System resource usage
    - Alert generation rate
    """
    
    def __init__(self, logger: TheftDetectionLogger):
        """
        Initialize performance monitor.
        
        Args:
            logger: TheftDetectionLogger instance
        """
        self.logger = logger
        
        # Metrics storage
        self.metrics = {
            'api_calls': [],           # API call durations
            'frame_processing': [],    # Frame processing times
            'detections': [],          # Detection events
            'alerts': [],              # Alert events
            'errors': []               # Error events
        }
        
        # Counters
        self.counters = {
            'total_frames': 0,
            'total_api_calls': 0,
            'total_detections': 0,
            'total_alerts': 0,
            'total_errors': 0
        }
    
    
    def record_api_call(self, endpoint: str, duration_ms: float, success: bool = True):
        """
        Record API call metrics.
        
        Args:
            endpoint: API endpoint
            duration_ms: Call duration in milliseconds
            success: Whether call succeeded
        """
        self.metrics['api_calls'].append({
            'timestamp': datetime.now().isoformat(),
            'endpoint': endpoint,
            'duration_ms': duration_ms,
            'success': success
        })
        
        self.counters['total_api_calls'] += 1
        
        # Keep only last 1000 metrics to prevent memory issues
        if len(self.metrics['api_calls']) > 1000:
            self.metrics['api_calls'] = self.metrics['api_calls'][-1000:]
        
        self.logger.log_performance_metric('api_call_duration', duration_ms, 'ms')
    
    
    def record_frame_processing(self, frame_number: int, duration_ms: float):
        """
        Record frame processing time.
        
        Args:
            frame_number: Frame number
            duration_ms: Processing duration in milliseconds
        """
        self.metrics['frame_processing'].append({
            'timestamp': datetime.now().isoformat(),
            'frame_number': frame_number,
            'duration_ms': duration_ms
        })
        
        self.counters['total_frames'] += 1
        
        if len(self.metrics['frame_processing']) > 1000:
            self.metrics['frame_processing'] = self.metrics['frame_processing'][-1000:]
        
        self.logger.log_performance_metric('frame_processing_duration', duration_ms, 'ms')
    
    
    def record_detection(self, event_type: str, confidence: float, severity: str):
        """
        Record detection event.
        
        Args:
            event_type: Type of detection
            confidence: Confidence score
            severity: Alert severity
        """
        self.metrics['detections'].append({
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'confidence': confidence,
            'severity': severity
        })
        
        self.counters['total_detections'] += 1
        
        if len(self.metrics['detections']) > 1000:
            self.metrics['detections'] = self.metrics['detections'][-1000:]
    
    
    def record_alert(self, alert_type: str, severity: str):
        """
        Record alert generation.
        
        Args:
            alert_type: Type of alert
            severity: Alert severity
        """
        self.metrics['alerts'].append({
            'timestamp': datetime.now().isoformat(),
            'alert_type': alert_type,
            'severity': severity
        })
        
        self.counters['total_alerts'] += 1
        
        if len(self.metrics['alerts']) > 1000:
            self.metrics['alerts'] = self.metrics['alerts'][-1000:]
    
    
    def record_error(self, error_type: str, message: str):
        """
        Record error event.
        
        Args:
            error_type: Type of error
            message: Error message
        """
        self.metrics['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'message': message
        })
        
        self.counters['total_errors'] += 1
        
        if len(self.metrics['errors']) > 1000:
            self.metrics['errors'] = self.metrics['errors'][-1000:]
    
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Returns:
            Dictionary containing performance statistics
        """
        stats = {
            'counters': self.counters.copy(),
            'averages': {}
        }
        
        # Calculate average API call duration
        if self.metrics['api_calls']:
            api_durations = [m['duration_ms'] for m in self.metrics['api_calls']]
            stats['averages']['api_call_ms'] = sum(api_durations) / len(api_durations)
            stats['averages']['api_call_min_ms'] = min(api_durations)
            stats['averages']['api_call_max_ms'] = max(api_durations)
        
        # Calculate average frame processing duration
        if self.metrics['frame_processing']:
            frame_durations = [m['duration_ms'] for m in self.metrics['frame_processing']]
            stats['averages']['frame_processing_ms'] = sum(frame_durations) / len(frame_durations)
            stats['averages']['frame_processing_min_ms'] = min(frame_durations)
            stats['averages']['frame_processing_max_ms'] = max(frame_durations)
        
        # Calculate alert rate (alerts per frame)
        if self.counters['total_frames'] > 0:
            stats['rates'] = {
                'alerts_per_frame': self.counters['total_alerts'] / self.counters['total_frames'],
                'detections_per_frame': self.counters['total_detections'] / self.counters['total_frames'],
                'errors_per_frame': self.counters['total_errors'] / self.counters['total_frames']
            }
        
        return stats
    
    
    def print_statistics(self):
        """Print performance statistics to console."""
        stats = self.get_statistics()
        
        print("\n" + "="*70)
        print("PERFORMANCE STATISTICS")
        print("="*70)
        
        print("\nCounters:")
        for key, value in stats['counters'].items():
            print(f"  {key}: {value}")
        
        if 'averages' in stats and stats['averages']:
            print("\nAverages:")
            for key, value in stats['averages'].items():
                print(f"  {key}: {value:.2f}")
        
        if 'rates' in stats:
            print("\nRates:")
            for key, value in stats['rates'].items():
                print(f"  {key}: {value:.4f}")
        
        print("="*70 + "\n")
    
    
    def export_metrics(self, output_file: str):
        """
        Export metrics to JSON file.
        
        Args:
            output_file: Path to output file
        """
        data = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'metrics': self.metrics
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Metrics exported to {output_file}")


# Decorators for automatic instrumentation

def log_execution_time(logger: TheftDetectionLogger):
    """
    Decorator to log function execution time.
    
    Usage:
        @log_execution_time(logger)
        def my_function():
            pass
    
    Args:
        logger: TheftDetectionLogger instance
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                logger.debug(
                    f"Function executed: {func.__name__}",
                    duration_ms=duration_ms,
                    success=True
                )
                
                return result
            
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                logger.error(
                    f"Function failed: {func.__name__}",
                    duration_ms=duration_ms,
                    error=str(e),
                    error_type=type(e).__name__
                )
                
                raise
        
        return wrapper
    return decorator


def retry_on_error(logger: TheftDetectionLogger, max_retries: int = 3, delay_seconds: float = 1.0):
    """
    Decorator to retry function on error with exponential backoff.
    
    Usage:
        @retry_on_error(logger, max_retries=3, delay_seconds=1.0)
        def my_api_call():
            pass
    
    Args:
        logger: TheftDetectionLogger instance
        max_retries: Maximum number of retry attempts
        delay_seconds: Initial delay between retries (doubles each time)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        # Exponential backoff
                        wait_time = delay_seconds * (2 ** (attempt - 1))
                        logger.warning(
                            f"Retrying {func.__name__} (attempt {attempt + 1}/{max_retries + 1})",
                            wait_time=wait_time
                        )
                        time.sleep(wait_time)
                    
                    result = func(*args, **kwargs)
                    
                    if attempt > 0:
                        logger.info(f"Retry successful for {func.__name__} after {attempt} attempt(s)")
                    
                    return result
                
                except Exception as e:
                    last_exception = e
                    logger.error(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}",
                        attempt=attempt + 1,
                        max_retries=max_retries + 1,
                        error_type=type(e).__name__
                    )
            
            # All retries exhausted
            logger.critical(
                f"All retries exhausted for {func.__name__}",
                max_retries=max_retries,
                error=str(last_exception)
            )
            
            raise last_exception
        
        return wrapper
    return decorator


def log_errors(logger: TheftDetectionLogger):
    """
    Decorator to automatically log and re-raise errors.
    
    Usage:
        @log_errors(logger)
        def my_function():
            pass
    
    Args:
        logger: TheftDetectionLogger instance
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(
                    f"Error in {func.__name__}: {str(e)}",
                    function=func.__name__,
                    error_type=type(e).__name__,
                    traceback=traceback.format_exc()
                )
                raise
        
        return wrapper
    return decorator


# Example usage and testing
if __name__ == "__main__":
    """
    Test the logging and instrumentation module.
    """
    
    print("Testing Logging and Instrumentation Module\n")
    
    # Initialize logger
    logger = TheftDetectionLogger(
        name="TestLogger",
        log_dir="./test_logs",
        log_level=logging.DEBUG,
        enable_console=True,
        enable_file=True
    )
    
    # Test different log levels
    logger.debug("This is a debug message", test_param="debug_value")
    logger.info("This is an info message", test_param="info_value")
    logger.warning("This is a warning message", test_param="warning_value")
    logger.error("This is an error message", test_param="error_value")
    logger.critical("This is a critical message", test_param="critical_value")
    
    # Test API call logging
    logger.log_api_call(
        endpoint="https://api.example.com/analyze",
        duration_ms=145.2,
        status_code=200
    )
    
    # Test detection event logging
    logger.log_detection_event(
        event_type="LOITERING",
        confidence=0.85,
        location="Checkout_Counter",
        severity="MEDIUM"
    )
    
    # Initialize performance monitor
    monitor = PerformanceMonitor(logger)
    
    # Record some test metrics
    monitor.record_api_call("analyze_image", 150.5, success=True)
    monitor.record_api_call("analyze_image", 175.2, success=True)
    monitor.record_frame_processing(1, 200.3)
    monitor.record_frame_processing(2, 185.7)
    monitor.record_detection("LOITERING", 0.85, "MEDIUM")
    monitor.record_alert("RESTRICTED_AREA_VIOLATION", "CRITICAL")
    
    # Print statistics
    monitor.print_statistics()
    
    # Test decorators
    @log_execution_time(logger)
    def test_function():
        """Test function for timing decorator."""
        time.sleep(0.1)
        return "Success"
    
    @log_errors(logger)
    def test_error_function():
        """Test function for error logging decorator."""
        raise ValueError("This is a test error")
    
    @retry_on_error(logger, max_retries=2, delay_seconds=0.5)
    def test_retry_function(attempt_count=[0]):
        """Test function for retry decorator."""
        attempt_count[0] += 1
        if attempt_count[0] < 2:
            raise ConnectionError("Simulated connection error")
        return "Success after retry"
    
    # Test timing decorator
    print("\nTesting execution time decorator:")
    result = test_function()
    print(f"Result: {result}")
    
    # Test error decorator
    print("\nTesting error logging decorator:")
    try:
        test_error_function()
    except ValueError:
        print("Error was logged and re-raised as expected")
    
    # Test retry decorator
    print("\nTesting retry decorator:")
    result = test_retry_function()
    print(f"Result: {result}")
    
    # Export metrics
    monitor.export_metrics("./test_logs/test_metrics.json")
    
    print("\n✓ Logging and instrumentation module test complete!")
    print(f"✓ Check ./test_logs/ directory for log files")
