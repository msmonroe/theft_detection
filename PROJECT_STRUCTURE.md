# Project Structure Guide

## 📁 Organized Directory Layout

The project has been reorganized following industry best practices for better understandability and maintainability.

```
theft_detection/
│
├── 📂 src/                           ← All source code (refactored)
│   ├── __init__.py                   Package initialization
│   ├── config.py                     ✨ Configuration constants (no magic numbers!)
│   ├── validators.py                 ✨ Input validation utilities
│   ├── geometry_utils.py             ✨ Geometric calculations (DRY)
│   ├── vision_analyzer.py            ✨ Azure AI Vision integration (SRP)
│   ├── person_tracker.py             ✨ Person tracking logic (SRP)
│   ├── zone_monitor.py               ✨ Zone monitoring (SRP)
│   ├── alert_manager.py              ✨ Alert management (SRP)
│   ├── behavior_analyzer.py          ✨ Behavior analysis (SRP)
│   ├── detection_orchestrator.py     ✨ Detection coordination (Orchestrator)
│   ├── retail_theft_detection.py     ✨ Main system (Facade)
│   └── demo_mock.py                  ✨ Mock client for demo/testing
│
├── 📂 tests/                         ← Test files
│   ├── __init__.py                   Test package initialization
│   └── test_theft_detection.py       Comprehensive test suite
│
├── 📂 utils/                         ← Utility modules
│   ├── __init__.py                   Utils package initialization
│   └── logging_instrumentation.py    Logging and monitoring tools
│
├── 📂 legacy/                        ← Original code (archived)
│   └── retail_theft_detection_original.py  Original monolithic code
│
├── 📂 docs/                          ← Documentation files
│   ├── REFACTORING_COMPLETE.md       Quick start guide
│   ├── REFACTORING_SUMMARY.md        Detailed architectural overview
│   ├── MODULE_GUIDE.md               Module usage guide
│   ├── BEFORE_AFTER_EXAMPLES.md      Side-by-side code comparisons
│   ├── LOGGING_GUIDE.md              Logging documentation
│   └── ENHANCEMENTS.md               Enhancement ideas
│
├── 📂 logs/                          ← Log files (auto-generated)
│   └── (log files created at runtime)
│
├── 📂 __pycache__/                   ← Python cache (auto-generated)
│
├── 📄 main.py                        ⭐ Main entry point - START HERE!
├── 📄 README.md                      Project overview
├── 📄 QUICKSTART.md                  Quick start guide
├── 📄 requirements.txt               Python dependencies
└── 📄 demo_report.json               Sample demo output

```

## 🎯 Where to Find What

### Want to run the system?
👉 **`main.py`** - Main entry point

### Want to understand the code?
👉 **`src/retail_theft_detection.py`** - Start here (main facade)
👉 **`docs/REFACTORING_COMPLETE.md`** - Overview and quick start

### Want to modify detection logic?
👉 **`src/detection_orchestrator.py`** - Detection pipeline coordination
👉 **`src/behavior_analyzer.py`** - Behavior patterns
👉 **`src/config.py`** - Adjust thresholds

### Want to add new features?
👉 **`docs/MODULE_GUIDE.md`** - Which module to modify
👉 **`src/`** - Add new modules here

### Want to see what changed?
👉 **`docs/BEFORE_AFTER_EXAMPLES.md`** - Code comparisons
👉 **`docs/REFACTORING_SUMMARY.md`** - Why and how

### Want to write tests?
👉 **`tests/test_theft_detection.py`** - Test suite
👉 **`tests/`** - Add new tests here

### Want to see the original code?
👉 **`legacy/retail_theft_detection_original.py`** - Original monolithic version

## 🚀 How to Use the Organized Structure

### Import from the organized structure:

```python
# Import main components
from src import RetailTheftDetector

# Import specific modules
from src.config import DetectionThresholds
from src.zone_monitor import DetectionZone
from src.alert_manager import TheftAlert

# Use utilities
from utils import TheftDetectionLogger

# Initialize
detector = RetailTheftDetector(endpoint, key)
```

### Run the main entry point:

```bash
# From project root
python main.py

# Or with Python module syntax
python -m src.retail_theft_detection
```

### Run tests:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_theft_detection.py -v
```

## 📊 Benefits of This Organization

### ✅ Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| **Source files location** | Root (mixed with docs) | `src/` directory |
| **Import clarity** | Unclear | Package-based imports |
| **Test organization** | Mixed with source | `tests/` directory |
| **Documentation** | Mixed with code | `docs/` directory |
| **Utilities** | Mixed with main code | `utils/` directory |
| **Legacy code** | Confusing | `legacy/` (clearly marked) |

### ✅ Clear Separation

- **Source code** (`src/`) - Clean, focused modules
- **Tests** (`tests/`) - All tests in one place
- **Documentation** (`docs/`) - All guides together
- **Utilities** (`utils/`) - Reusable components
- **Legacy** (`legacy/`) - Old code for reference

### ✅ Professional Structure

This structure follows Python best practices:
- Standard package layout
- Clear module boundaries
- Logical grouping
- Easy to navigate
- IDE-friendly

## 🔄 Migration from Old Structure

If you had code using the old structure:

### Old imports:
```python
from retail_theft_detection_refactored import RetailTheftDetector
from config import DetectionThresholds
```

### New imports:
```python
from src.retail_theft_detection import RetailTheftDetector
from src.config import DetectionThresholds
```

### Or use the package:
```python
from src import RetailTheftDetector
```

## 📖 Next Steps

1. **Start here**: Run `python main.py` to see it working
2. **Read docs**: Check `docs/REFACTORING_COMPLETE.md`
3. **Explore code**: Browse `src/` directory
4. **Understand structure**: Review this file
5. **Make changes**: Follow `docs/MODULE_GUIDE.md`

---

**This organized structure makes the codebase:**
- ✅ Easy to navigate
- ✅ Professional and maintainable
- ✅ Clear and understandable
- ✅ Following industry standards
- ✅ Ready for team collaboration
