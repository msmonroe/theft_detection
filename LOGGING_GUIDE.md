# Integration Guide: Logging, Error Handling, and Unit Testing

This guide explains how to integrate comprehensive logging, error handling, and testing into the Retail Theft Detection System.

## Files Created

1. **`logging_instrumentation.py`** - Comprehensive logging and monitoring
2. **`test_theft_detection.py`** - Unit test suite
3. **Updated `retail_theft_detection.py`** - With integrated logging

## Features Added

### 1. Comprehensive Logging

**Multi-Level Logging:**
- DEBUG: Detailed diagnostic information
- INFO: General information messages
- WARNING: Warning messages (potential issues)
- ERROR: Error messages (failures)
- CRITICAL: Critical errors (system failures)

**Log Outputs:**
- Console output (for development)
- Rotating file logs (30-day retention)
- JSON structured logs (for log aggregation)
- Error-only logs (for quick error review)

**Azure Application Insights Integration:**
- Optional integration with Azure monitoring
- Real-time error tracking
- Performance metrics
- Custom telemetry

### 2. Performance Monitoring

**Metrics Tracked:**
- API call latency (min, max, average)
- Frame processing time
- Detection accuracy
- Alert generation rate
- Error frequency

**Metrics Export:**
- JSON format for analysis
- Statistics dashboard
- Historical trending

### 3. Error Handling

**Comprehensive Error Handling:**
- Try-catch blocks for all external calls
- Detailed error logging with context
- Graceful degradation on failures
- Retry logic with exponential backoff

**Error Categories:**
- Azure API errors (rate limits, auth failures)
- File I/O errors (missing files, permissions)
- Processing errors (invalid data, corrupted frames)
- Configuration errors (invalid zones, thresholds)

### 4. Instrumentation Decorators

**@log_execution_time:**
```python
@log_execution_time(logger)
def my_function():
    # Automatically logs execution time
    pass
```

**@retry_on_error:**
```python
@retry_on_error(logger, max_retries=3, delay_seconds=1.0)
def api_call():
    # Automatically retries on failure with exponential backoff
    pass
```

**@log_errors:**
```python
@log_errors(logger)
def risky_operation():
    # Automatically logs exceptions before re-raising
    pass
```

## Usage Examples

### Basic Usage with Logging

```python
from retail_theft_detection import RetailTheftDetector
from logging_instrumentation import TheftDetectionLogger, PerformanceMonitor

# Initialize logger
logger = TheftDetectionLogger(
    name="MyTheftDetector",
    log_dir="./logs",
    enable_console=True,
    enable_file=True,
    enable_azure=False  # Set True for Azure App Insights
)

# Initialize detector with logging
detector = RetailTheftDetector(
    endpoint="your-endpoint",
    key="your-key",
    enable_logging=True  # Enables integrated logging
)

# Analyze frame (automatically logged)
try:
    alerts = detector.analyze_frame("camera_frame.jpg")
    logger.info(f"Analysis complete: {len(alerts)} alerts")
except Exception as e:
    logger.exception("Frame analysis failed")
```

### Using Performance Monitor

```python
from logging_instrumentation import PerformanceMonitor

# Create monitor
monitor = PerformanceMonitor(logger)

# Record metrics manually
monitor.record_api_call("analyze_image", duration_ms=150.5, success=True)
monitor.record_frame_processing(frame_number=1, duration_ms=200.0)
monitor.record_detection("LOITERING", confidence=0.85, severity="MEDIUM")
monitor.record_alert("RESTRICTED_AREA_VIOLATION", severity="CRITICAL")

# Get statistics
stats = monitor.get_statistics()
print(f"Average API latency: {stats['averages']['api_call_ms']}ms")

# Export metrics
monitor.export_metrics("metrics_report.json")

# Print summary
monitor.print_statistics()
```

### Azure Application Insights Integration

```python
# Enable Azure monitoring
logger = TheftDetectionLogger(
    name="ProductionDetector",
    log_dir="./logs",
    enable_azure=True,
    azure_connection_string="InstrumentationKey=your-key;..."
)

# All logs automatically sent to Azure
logger.info("System started")
logger.error("Detection failure", alert_type="LOITERING", confidence=0.85)

# View logs in Azure Portal → Application Insights → Logs
```

## Running Unit Tests

### Prerequisites

```bash
pip install pytest pytest-cov
```

### Run All Tests

```bash
# Basic test run
python -m pytest test_theft_detection.py -v

# With coverage report
python -m pytest test_theft_detection.py -v --cov=retail_theft_detection --cov-report=html

# Run specific test class
python -m pytest test_theft_detection.py::TestRetailTheftDetector -v

# Run specific test method
python -m pytest test_theft_detection.py::TestRetailTheftDetector::test_point_in_polygon -v
```

### Test Coverage

The test suite covers:
- ✅ Detection zone creation and validation
- ✅ Alert generation logic
- ✅ Point-in-polygon algorithm
- ✅ Zone location detection
- ✅ Distance calculations
- ✅ Person tracking across frames
- ✅ Dwell time calculations
- ✅ Suspicious object detection
- ✅ Azure API integration (mocked)
- ✅ Logging functionality
- ✅ Performance monitoring
- ✅ End-to-end integration

### Understanding Test Output

```
test_theft_detection.py::TestDetectionZone::test_zone_creation PASSED    [ 10%]
test_theft_detection.py::TestDetectionZone::test_zone_defaults PASSED    [ 20%]
test_theft_detection.py::TestRetailTheftDetector::test_detector_initialization PASSED [ 30%]
...
================================ Coverage Report ================================
Name                         Stmts   Miss  Cover
-----------------------------------------------
retail_theft_detection.py      450     50    89%
logging_instrumentation.py     200     20    90%
-----------------------------------------------
TOTAL                          650     70    89%
```

## Log File Structure

```
logs/
├── theft_detection.log          # All logs (INFO and above)
├── theft_detection_errors.log   # ERROR and CRITICAL only
└── theft_detection_json.log     # JSON structured logs
```

### Sample Log Output

**Standard Log:**
```
[2026-02-06 14:30:15] [    INFO] [RetailTheftDetector.analyze_frame:245] - Analyzing: camera_1_frame_0001.jpg
[2026-02-06 14:30:15] [    INFO] [RetailTheftDetector._call_azure_vision:305] - Azure API call successful | Context: {"duration_ms": 145.2, "people_detected": 3, "objects_detected": 5}
[2026-02-06 14:30:15] [ WARNING] [RetailTheftDetector._detect_people:380] - Detection event: LOITERING | Context: {"event_type": "LOITERING", "confidence": 0.85, "location": "Electronics_Display", "severity": "MEDIUM"}
```

**JSON Log:**
```json
{"timestamp": "2026-02-06 14:30:15", "level": "INFO", "logger": "RetailTheftDetector", "function": "analyze_frame", "line": 245, "message": "Analyzing: camera_1_frame_0001.jpg"}
{"timestamp": "2026-02-06 14:30:15", "level": "WARNING", "logger": "RetailTheftDetector", "function": "_detect_people", "line": 380, "message": "Detection event: LOITERING | Context: {\"event_type\": \"LOITERING\", \"confidence\": 0.85, \"location\": \"Electronics_Display\", \"severity\": \"MEDIUM\"}"}
```

## Error Handling Examples

### Handling Azure API Errors

```python
from azure.core.exceptions import AzureError, HttpResponseError

try:
    alerts = detector.analyze_frame("frame.jpg")
except HttpResponseError as e:
    if e.status_code == 401:
        logger.critical("Authentication failed - check API key")
    elif e.status_code == 429:
        logger.warning("Rate limit exceeded - slowing down")
        time.sleep(60)  # Wait before retry
    else:
        logger.error(f"Azure API error: {e}")
except FileNotFoundError:
    logger.error("Image file not found")
except Exception as e:
    logger.exception("Unexpected error in frame analysis")
```

### Handling Video Processing Errors

```python
try:
    detector.process_video("store_footage.mp4", "./alerts")
except cv2.error as e:
    logger.error(f"OpenCV error: {e}")
except Exception as e:
    logger.exception("Video processing failed")
    # Could continue with next video or exit gracefully
```

## Best Practices

### 1. Log Levels

- **DEBUG**: `logger.debug("Checking zone: Test_Zone", coordinates=[...])`
- **INFO**: `logger.info("Frame analyzed successfully", frame_number=1)`
- **WARNING**: `logger.warning("High API latency detected", duration_ms=5000)`
- **ERROR**: `logger.error("Failed to process frame", error=str(e))`
- **CRITICAL**: `logger.critical("System shutdown - disk full")`

### 2. Contextual Logging

Always include relevant context:

```python
# Good
logger.info("Detection completed", 
    frame_number=123,
    alerts_count=5,
    processing_time_ms=250.5
)

# Bad
logger.info("Detection completed")
```

### 3. Exception Logging

```python
# Use logger.exception() for automatic traceback
try:
    result = detector.analyze_frame("frame.jpg")
except Exception as e:
    # This automatically includes full traceback
    logger.exception("Frame analysis failed")
    
    # Or manually with context
    logger.error(
        "Frame analysis failed",
        frame_path="frame.jpg",
        error_type=type(e).__name__,
        error_message=str(e)
    )
```

### 4. Performance Tracking

```python
import time

start_time = time.time()

# Your processing code
result = detector.analyze_frame("frame.jpg")

duration_ms = (time.time() - start_time) * 1000

# Log performance
logger.debug("Frame processed", duration_ms=duration_ms)

# Or use decorator
@log_execution_time(logger)
def process_frame(path):
    return detector.analyze_frame(path)
```

## Production Deployment

### Environment Variables

```bash
# Logging configuration
export LOG_LEVEL=INFO
export LOG_DIR=/var/log/theft-detection
export ENABLE_AZURE_INSIGHTS=true
export AZURE_INSIGHTS_KEY=your-instrumentation-key

# System configuration
export AZURE_VISION_ENDPOINT=your-endpoint
export AZURE_VISION_KEY=your-key
```

### Log Rotation

Built-in log rotation:
- Daily rotation at midnight
- 30 days retention
- Automatic compression (optional)

For custom rotation:

```python
logger = TheftDetectionLogger(
    name="Production",
    log_dir="/var/log/theft-detection",
    log_level=logging.INFO
)
```

### Monitoring Dashboard

Recommended monitoring:
1. **Azure Application Insights** - Real-time monitoring
2. **ELK Stack** - Log aggregation (Elasticsearch, Logstash, Kibana)
3. **Grafana** - Custom dashboards
4. **Prometheus** - Metrics collection

### Alerts

Set up alerts for:
- Error rate > 5% of total operations
- API latency > 1000ms
- Detection failures
- Disk space < 10%

## Troubleshooting

### Issue: No log files created

**Solution:**
- Check directory permissions
- Verify `enable_file=True`
- Check available disk space

### Issue: Logs not appearing in Azure

**Solution:**
- Verify Application Insights connection string
- Check `enable_azure=True`
- Verify network connectivity
- Check Azure quota limits

### Issue: Tests failing

**Solution:**
- Install test dependencies: `pip install pytest pytest-cov`
- Verify mock objects configured correctly
- Check test data files exist

### Issue: High memory usage

**Solution:**
- Metrics are limited to last 1000 entries
- Old logs are rotated automatically
- Adjust log level to WARNING or ERROR in production

## Additional Resources

- [Azure Application Insights Documentation](https://docs.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Python Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
