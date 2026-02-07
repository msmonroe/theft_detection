# Clean Code Refactoring - Before & After Examples

This document shows specific examples of how the code was improved following Clean Code principles.

---

## Example 1: Eliminating Magic Numbers

### ❌ Before (Anti-Pattern)
```python
# retail_theft_detection.py (Original)
if confidence < 0.6:  # What does 0.6 mean?
    continue

if dwell_time > 180:  # Why 180?
    alert = create_alert()

if dist < 100:  # 100 what? Why 100?
    person_id = existing_id
```

### ✅ After (Clean Code)
```python
# config.py
class DetectionThresholds:
    MIN_CONFIDENCE = 0.6  # Minimum confidence for accepting detections

class TimeThresholds:
    DEFAULT_LOITER_SECONDS = 180  # 3 minutes triggers loitering

class TrackingConfig:
    MAX_TRACKING_DISTANCE_PIXELS = 100  # Maximum distance for matching

# detection_orchestrator.py
if confidence < DetectionThresholds.MIN_CONFIDENCE:
    continue

if dwell_time > TimeThresholds.DEFAULT_LOITER_SECONDS:
    alert = create_alert()

if distance < TrackingConfig.MAX_TRACKING_DISTANCE_PIXELS:
    person_id = existing_id
```

**Benefits**:
- ✅ Self-documenting code
- ✅ Easy to adjust thresholds
- ✅ Single source of truth
- ✅ No need to hunt through code to change values

---

## Example 2: Single Responsibility Principle

### ❌ Before (God Class)
```python
# One class doing everything!
class RetailTheftDetector:
    def __init__(self, endpoint, key):
        # Initialize Azure client
        # Initialize zones
        # Initialize tracking
        # Initialize alerts
        # ... 200 lines ...
    
    def analyze_frame(self):
        # Call Azure API
        # Track people
        # Check zones
        # Analyze behavior
        # Create alerts
        # ... 300 lines ...
    
    def _track_person(self):
        # Tracking logic
        # ... 100 lines ...
    
    def _detect_objects(self):
        # Object detection
        # ... 100 lines ...
    
    # ... 15 more methods, 1000+ lines total
```

### ✅ After (Focused Classes)
```python
# vision_analyzer.py (ONE responsibility)
class VisionAnalyzer:
    """ONLY handles Azure AI Vision API calls."""
    def __init__(self, endpoint, key):
        self._client = ImageAnalysisClient(...)
    
    def analyze_image(self, image_path):
        return self._client.analyze(...)

# person_tracker.py (ONE responsibility)
class PersonTracker:
    """ONLY handles person tracking."""
    def track_person(self, bounding_box, frame_number):
        return person_id

# zone_monitor.py (ONE responsibility)
class ZoneMonitor:
    """ONLY handles zone monitoring."""
    def find_zone_for_point(self, x, y):
        return zone

# alert_manager.py (ONE responsibility)
class AlertManager:
    """ONLY handles alert management."""
    def create_alert(self, alert_type, ...):
        return alert

# detection_orchestrator.py (ONLY orchestrates)
class DetectionOrchestrator:
    """ONLY coordinates components - no business logic!"""
    def __init__(self, vision_analyzer, zone_monitor, alert_manager):
        self._vision_analyzer = vision_analyzer
        self._zone_monitor = zone_monitor
        self._alert_manager = alert_manager
```

**Benefits**:
- ✅ Each class has one reason to change
- ✅ Easy to test in isolation
- ✅ Easy to understand
- ✅ Easy to replace/extend

---

## Example 3: Descriptive Function Names

### ❌ Before
```python
def _calc(self, loc1, loc2):  # Calc what?
    x1 = loc1['x'] + loc1['width'] / 2
    y1 = loc1['y'] + loc1['height'] / 2
    x2 = loc2['x'] + loc2['width'] / 2
    y2 = loc2['y'] + loc2['height'] / 2
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def _check(self, zone):  # Check what?
    if zone.is_restricted:
        return True
    return False

def _process(self, result, data, num):  # Process what? What are these params?
    # ... 50 lines of unclear logic
```

### ✅ After
```python
# geometry_utils.py
def calculate_distance_between_boxes(bbox1: Dict, bbox2: Dict) -> float:
    """
    Calculate Euclidean distance between centers of two bounding boxes.
    
    Args:
        bbox1: First bounding box with x, y, width, height
        bbox2: Second bounding box with x, y, width, height
        
    Returns:
        Euclidean distance in pixels
    """
    center1 = calculate_bounding_box_center(bbox1)
    center2 = calculate_bounding_box_center(bbox2)
    return calculate_euclidean_distance(center1, center2)

# zone_monitor.py
def is_in_restricted_zone(self, x: int, y: int) -> bool:
    """
    Check if a point is in a restricted zone.
    
    Args:
        x: X coordinate
        y: Y coordinate
        
    Returns:
        True if point is in any restricted zone
    """
    zone = self.find_zone_for_point(x, y)
    return zone is not None and zone.is_restricted

# detection_orchestrator.py
def _analyze_people(self, 
                   result: VisionAnalysisResult, 
                   image_path: str, 
                   frame_number: int) -> List[TheftAlert]:
    """
    Analyze detected people for suspicious activity.
    
    Args:
        result: Azure AI Vision analysis result
        image_path: Path to analyzed image
        frame_number: Current frame number for tracking
        
    Returns:
        List of alerts related to people detections
    """
    # Clear, focused logic
```

**Benefits**:
- ✅ Function name tells you exactly what it does
- ✅ Type hints make parameters clear
- ✅ Docstrings explain purpose and usage
- ✅ No need to read implementation to understand

---

## Example 4: Small, Focused Functions

### ❌ Before (Long Function)
```python
def analyze_frame(self, image_path, frame_number):
    """100+ lines doing everything!"""
    alerts = []
    
    # Validate file
    if not os.path.exists(image_path):
        raise FileNotFoundError(...)
    
    # Read image
    with open(image_path, 'rb') as f:
        image_data = f.read()
    
    # Call Azure
    result = self.vision_client.analyze(
        image_data=image_data,
        visual_features=[...]
    )
    
    # Log results
    people_count = len(result.people.list) if result.people else 0
    print(f"People: {people_count}")
    
    # Process people
    if result.people:
        for person in result.people.list:
            bbox = person.bounding_box
            # ... 20 lines of processing
            
            # Check zones
            for zone in self.zones:
                # ... 15 lines of zone checking
                
            # Track person
            for existing_id, data in self.tracked_people.items():
                # ... 20 lines of tracking
    
    # Process objects
    if result.objects:
        for obj in result.objects.list:
            # ... 30 lines of object processing
    
    # Check patterns
    if result.tags:
        # ... 20 lines of pattern checking
    
    return alerts  # After 100+ lines!
```

### ✅ After (Composed of Small Functions)
```python
# detection_orchestrator.py
def analyze_frame(self, image_path: str, frame_number: int) -> List[TheftAlert]:
    """
    Run complete analysis pipeline on a single frame.
    
    Clean, readable orchestration - no implementation details!
    """
    try:
        analysis_result = self._vision_analyzer.analyze_image(image_path)
        
        people_alerts = self._analyze_people(
            analysis_result, image_path, frame_number
        )
        
        object_alerts = self._analyze_objects(
            analysis_result, image_path
        )
        
        behavior_alerts = self._analyze_behavior_patterns(
            analysis_result, image_path, frame_number
        )
        
        return people_alerts + object_alerts + behavior_alerts
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return []

# Each helper function is small and focused (10-30 lines each)
def _analyze_people(self, result, image_path, frame_number):
    """Only analyzes people - nothing else! ~30 lines"""
    
def _analyze_objects(self, result, image_path):
    """Only analyzes objects - nothing else! ~25 lines"""
    
def _analyze_behavior_patterns(self, result, image_path, frame_number):
    """Only analyzes patterns - nothing else! ~20 lines"""
```

**Benefits**:
- ✅ Main function reads like a high-level description
- ✅ Each helper function fits on one screen
- ✅ Easy to understand flow
- ✅ Easy to test each step independently

---

## Example 5: DRY (Don't Repeat Yourself)

### ❌ Before (Repetition)
```python
# Repeated geometry calculations everywhere
def _detect_people(self, ...):
    x = bbox['x'] + bbox['width'] / 2
    y = bbox['y'] + bbox['height'] / 2
    # Use x, y...

def _detect_objects(self, ...):
    x = bbox['x'] + bbox['width'] / 2  # Same calculation!
    y = bbox['y'] + bbox['height'] / 2
    # Use x, y...

def _track_person(self, ...):
    x1 = loc1['x'] + loc1['width'] / 2  # Again!
    y1 = loc1['y'] + loc1['height'] / 2
    x2 = loc2['x'] + loc2['width'] / 2  # And again!
    y2 = loc2['y'] + loc2['height'] / 2
    dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
def _analyze_behaviors(self, ...):
    # Same distance calculation AGAIN
    x1 = positions[0]['x'] + positions[0]['width'] / 2
    # ... repeated
```

### ✅ After (DRY)
```python
# geometry_utils.py - ONE place for geometry calculations
def calculate_bounding_box_center(bbox: Dict) -> Tuple[float, float]:
    """Calculate center once, use everywhere."""
    center_x = bbox['x'] + bbox['width'] / 2
    center_y = bbox['y'] + bbox['height'] / 2
    return (center_x, center_y)

def calculate_distance_between_boxes(bbox1: Dict, bbox2: Dict) -> float:
    """Calculate distance once, use everywhere."""
    center1 = calculate_bounding_box_center(bbox1)
    center2 = calculate_bounding_box_center(bbox2)
    return calculate_euclidean_distance(center1, center2)

# Now used everywhere consistently:
# detection_orchestrator.py
center = calculate_bounding_box_center(bbox)

# person_tracker.py
distance = calculate_distance_between_boxes(bbox1, bbox2)

# behavior_analyzer.py
speed = calculate_movement_speed(positions, time_span)
```

**Benefits**:
- ✅ Fix bugs in one place, not many
- ✅ Consistent behavior everywhere
- ✅ Easy to optimize
- ✅ Easy to test

---

## Example 6: Dependency Injection for Testability

### ❌ Before (Hard to Test)
```python
class RetailTheftDetector:
    def __init__(self, endpoint, key):
        # Creates dependencies internally - can't be mocked!
        self.vision_client = ImageAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
    
    def analyze_frame(self, image_path):
        # Always calls real Azure API
        result = self.vision_client.analyze(...)
        # Hard to test without Azure credentials!
```

### ✅ After (Easy to Test)
```python
# detection_orchestrator.py
class DetectionOrchestrator:
    def __init__(self,
                 vision_analyzer: VisionAnalyzer,  # Injected!
                 zone_monitor: ZoneMonitor,        # Injected!
                 alert_manager: AlertManager):     # Injected!
        self._vision_analyzer = vision_analyzer
        self._zone_monitor = zone_monitor
        self._alert_manager = alert_manager

# Testing is now easy:
def test_detection_orchestrator():
    # Create mocks
    mock_vision = Mock(spec=VisionAnalyzer)
    mock_zones = Mock(spec=ZoneMonitor)
    mock_alerts = Mock(spec=AlertManager)
    
    # Inject mocks
    orchestrator = DetectionOrchestrator(
        vision_analyzer=mock_vision,
        zone_monitor=mock_zones,
        alert_manager=mock_alerts
    )
    
    # Test without real Azure!
    orchestrator.analyze_frame("test.jpg")
    
    # Verify interactions
    mock_vision.analyze_image.assert_called_once()
```

**Benefits**:
- ✅ Test without Azure credentials
- ✅ Test in isolation
- ✅ Fast tests (no network calls)
- ✅ Easy to mock behavior

---

## Example 7: Validation (Fail Fast)

### ❌ Before (Fail Late)
```python
class DetectionZone:
    def __init__(self, name, coordinates, ...):
        self.name = name
        self.coordinates = coordinates  # No validation!
        # ... used later...
    
    def contains_point(self, x, y):
        # Fails here with confusing error!
        if len(self.coordinates) < 3:
            return False  # Invalid polygon discovered too late
```

### ✅ After (Fail Fast)
```python
# zone_monitor.py
@dataclass
class DetectionZone:
    name: str
    coordinates: List[Tuple[int, int]]
    is_restricted: bool = False
    alert_on_loitering: bool = False
    max_loiter_seconds: int = 120
    
    def __post_init__(self):
        """Validate immediately on construction!"""
        if not validate_polygon(self.coordinates):
            raise ValueError(
                f"Invalid polygon coordinates for zone '{self.name}'. "
                f"Need at least 3 vertices, got {len(self.coordinates)}"
            )

# Now errors happen immediately:
zone = DetectionZone(
    name="BadZone",
    coordinates=[(0, 0), (10, 10)]  # Only 2 points!
)
# ValueError: Invalid polygon coordinates for zone 'BadZone'.
#             Need at least 3 vertices, got 2

# Good - fails immediately with clear message!
```

**Benefits**:
- ✅ Errors reported immediately
- ✅ Clear error messages
- ✅ Can't create invalid objects
- ✅ Easier debugging

---

## Summary: Clean Code Wins

| Aspect | Before | After |
|--------|--------|-------|
| **Lines per class** | 1000+ | 50-200 |
| **Magic numbers** | 20+ | 0 |
| **Testability** | Low (tightly coupled) | High (dependency injection) |
| **Readability** | Hard (all mixed together) | Easy (focused modules) |
| **Maintainability** | Hard (find code in 1000 lines) | Easy (know which module) |
| **Extensibility** | Hard (modify 1000 line class) | Easy (add new module) |
| **Reusability** | Low (embedded logic) | High (utility modules) |

---

## Key Takeaways

1. **No Magic Numbers**: Use named constants
2. **Single Responsibility**: One class, one job
3. **Descriptive Names**: Code should read like prose
4. **Small Functions**: One screen or less
5. **DRY**: Don't repeat yourself
6. **Dependency Injection**: Inject dependencies for testability
7. **Fail Fast**: Validate early

These aren't just academic principles - they make your code:
- ✅ Easier to understand
- ✅ Easier to modify
- ✅ Easier to test
- ✅ Easier to debug
- ✅ More professional
