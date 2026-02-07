# Clean Code Refactoring - Module Guide

## Quick Reference: Module Responsibilities

This guide helps you understand which module to use or modify for specific tasks.

---

## 📋 Configuration & Constants

### `config.py`
**When to use**: Changing thresholds, timeouts, or default values

**Examples**:
- Adjust minimum confidence threshold
- Change loitering time limits
- Modify tracking distance
- Update high-value item lists

**Common tasks**:
```python
from config import DetectionThresholds

# Change minimum confidence
DetectionThresholds.MIN_CONFIDENCE = 0.7

# Adjust loitering threshold
from config import TimeThresholds
TimeThresholds.DEFAULT_LOITER_SECONDS = 240
```

---

## 🔍 Detection & Analysis

### `vision_analyzer.py`
**When to use**: Azure AI Vision API integration

**Responsibilities**:
- Call Azure AI Vision API
- Parse API responses
- Handle API errors

**You would modify this to**:
- Change Azure API features requested
- Add retry logic for API calls
- Log API performance metrics

### `detection_orchestrator.py`
**When to use**: Coordinating detection pipeline

**Responsibilities**:
- Orchestrate analysis workflow
- Combine results from analyzers
- Coordinate component interactions

**You would modify this to**:
- Add new detection steps to pipeline
- Change order of detection operations
- Add new alert types

### `behavior_analyzer.py`
**When to use**: Adding or modifying behavior detection logic

**Responsibilities**:
- Detect suspicious patterns
- Analyze movement behaviors
- Evaluate item combinations

**You would modify this to**:
- Add new suspicious patterns
- Implement new behavior detection algorithms
- Change pattern matching logic

---

## 👥 Tracking & Monitoring

### `person_tracker.py`
**When to use**: Person tracking logic

**Responsibilities**:
- Track people across frames
- Match detections to existing tracks
- Calculate dwell times

**You would modify this to**:
- Implement better tracking algorithms (DeepSORT, etc.)
- Add appearance-based matching
- Improve track management

### `zone_monitor.py`
**When to use**: Zone-based detection

**Responsibilities**:
- Manage detection zones
- Check point-in-polygon
- Zone violation detection

**You would modify this to**:
- Add dynamic zone creation
- Implement zone hierarchies
- Add zone-based behaviors

---

## 🚨 Alerts & Reporting

### `alert_manager.py`
**When to use**: Alert creation and management

**Responsibilities**:
- Create alerts
- Store alert history
- Generate reports

**You would modify this to**:
- Add alert deduplication
- Implement alert aggregation
- Add alert routing/notifications
- Change report formats

---

## 🔧 Utilities

### `validators.py`
**When to use**: Input validation

**Responsibilities**:
- Validate inputs
- Check data formats
- Provide error messages

**You would modify this to**:
- Add new validation rules
- Implement custom validators
- Add more specific error messages

### `geometry_utils.py`
**When to use**: Geometric calculations

**Responsibilities**:
- Point-in-polygon tests
- Distance calculations
- Bounding box operations

**You would modify this to**:
- Add new geometric functions
- Optimize performance
- Add 3D calculations

---

## 🎯 Common Tasks

### Task: Add a New Alert Type

1. **Update** `config.py`:
   ```python
   # Add to ValidationRules.VALID_ALERT_TYPES
   VALID_ALERT_TYPES = [
       "RESTRICTED_AREA_VIOLATION",
       "LOITERING",
       "UNPAID_ITEM_AT_EXIT",
       "CONCEALMENT_PATTERN",
       "YOUR_NEW_TYPE"  # Add here
   ]
   ```

2. **Implement detection** in `detection_orchestrator.py`:
   ```python
   def _check_your_new_detection(self, ...):
       alert = self._alert_manager.create_alert(
           alert_type="YOUR_NEW_TYPE",
           ...
       )
       return alert
   ```

3. **Call in pipeline** `analyze_frame()`:
   ```python
   new_alerts = self._check_your_new_detection(...)
   all_alerts.extend(new_alerts)
   ```

### Task: Adjust Detection Sensitivity

1. **Update** `config.py`:
   ```python
   class DetectionThresholds:
       MIN_CONFIDENCE = 0.75  # Raise for fewer false positives
   ```

2. **No code changes needed** - configuration drives behavior!

### Task: Add Custom Zone

1. **Create zone** in your code:
   ```python
   from zone_monitor import DetectionZone
   
   custom_zone = DetectionZone(
       name="Premium_Section",
       coordinates=[(100, 100), (400, 100), (400, 300), (100, 300)],
       is_restricted=False,
       alert_on_loitering=True,
       max_loiter_seconds=90
   )
   ```

2. **Pass to detector**:
   ```python
   detector = RetailTheftDetector(
       endpoint=endpoint,
       key=key,
       zones=[custom_zone]  # Add your zones
   )
   ```

### Task: Implement Custom Tracking

1. **Extend** `person_tracker.py`:
   ```python
   class AdvancedPersonTracker(PersonTracker):
       def track_person(self, bounding_box, frame_number):
           # Your custom tracking logic
           pass
   ```

2. **Use in orchestrator**:
   ```python
   # In detection_orchestrator.py __init__
   self._person_tracker = AdvancedPersonTracker()
   ```

### Task: Add Logging

```python
# Already prepared for logging integration
from logging_instrumentation import TheftDetectionLogger

logger = TheftDetectionLogger()

# Use in any module:
logger.info("Detection started", frame=frame_number)
logger.error("Analysis failed", error=str(e))
```

---

## 📐 Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│         RetailTheftDetector (Facade)                    │
│  - Simple API for users                                 │
│  - Delegates to orchestrator                            │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│         DetectionOrchestrator                           │
│  - Coordinates detection pipeline                       │
│  - No business logic, only orchestration                │
└──┬────────┬─────────┬─────────────┬────────────────────┘
   │        │         │             │
   ▼        ▼         ▼             ▼
┌─────┐ ┌─────┐  ┌──────┐    ┌──────────┐
│Vision│ │Zone │  │Person│    │Behavior  │
│Analyzer Monitor  Tracker│    │Analyzer  │
└─────┘ └─────┘  └──────┘    └──────────┘
   │        │         │             │
   └────────┴─────────┴─────────────┘
                   │
                   ▼
            ┌──────────────┐
            │AlertManager  │
            └──────────────┘
```

---

## 🧪 Testing Strategy

### Unit Testing
Each module can be tested independently:

```python
# Test vision_analyzer.py
def test_vision_analyzer():
    analyzer = VisionAnalyzer(endpoint, key)
    result = analyzer.analyze_image("test.jpg")
    assert result is not None

# Test zone_monitor.py
def test_zone_contains_point():
    zone = DetectionZone(...)
    assert zone.contains_point(150, 150) == True

# Test behavior_analyzer.py
def test_concealment_detection():
    analyzer = BehaviorAnalyzer()
    tags = ["person", "bag", "clothing"]
    pattern = analyzer.detect_concealment_patterns(tags)
    assert pattern is not None
```

### Integration Testing
Test components working together:

```python
def test_detection_pipeline():
    orchestrator = create_test_orchestrator()
    alerts = orchestrator.analyze_frame("test.jpg")
    assert len(alerts) > 0
```

---

## 💡 Best Practices

### 1. Configuration Over Code
- ✅ Add new thresholds to `config.py`
- ❌ Don't hardcode values in business logic

### 2. Single Responsibility
- ✅ One module, one purpose
- ❌ Don't mix concerns (e.g., tracking + alerting)

### 3. Dependency Injection
- ✅ Pass dependencies to constructors
- ❌ Don't create dependencies inside classes

### 4. Fail Fast
- ✅ Validate in constructors (`__post_init__`)
- ❌ Don't defer validation

### 5. Descriptive Names
- ✅ `should_alert_for_loitering()`
- ❌ `check()` or `process()`

---

## 🔄 Migration Path

### Phase 1: Parallel Run
Run both old and new code side-by-side:
```python
# Import both versions
from retail_theft_detection import RetailTheftDetector as OldDetector
from retail_theft_detection_refactored import RetailTheftDetector as NewDetector

# Compare results
old_alerts = old_detector.analyze_frame(image)
new_alerts = new_detector.analyze_frame(image)
```

### Phase 2: Gradual Switchover
Switch one feature at a time:
```python
# Week 1: Use new detector for images
# Week 2: Use new detector for videos
# Week 3: Full migration
```

### Phase 3: Deprecate Old Code
Mark old code as deprecated:
```python
import warnings

class OldRetailTheftDetector:
    def __init__(self, ...):
        warnings.warn(
            "This class is deprecated. Use RetailTheftDetector from "
            "retail_theft_detection_refactored instead.",
            DeprecationWarning
        )
```

---

## 📞 Support

### Questions?
1. Check the docstrings in each module
2. Read `REFACTORING_SUMMARY.md` for architectural decisions
3. Review the original `retail_theft_detection.py` for comparison

### Want to Contribute?
1. Follow the established patterns
2. Add unit tests for new components
3. Update this guide with new modules
4. Keep modules focused and single-purpose
