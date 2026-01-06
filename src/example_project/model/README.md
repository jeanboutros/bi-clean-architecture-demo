# Domain Layer (Model)

## Overview

The Domain layer represents the **innermost circle** of Clean Architecture. It contains the core business entities and enterprise business rules that define what the system is fundamentally about.

## Key Principles

### Pure Business Logic
- Contains only domain entities and business rules
- No external dependencies (except Python standard library)
- Framework and technology independent

### Stability
- This layer should change **rarely**
- Changes are driven **only** by business requirement changes
- Not affected by UI, database, or API changes

### Immutability
- Domain entities are immutable (`frozen=True` in dataclasses)
- Ensures data integrity and predictability
- Supports functional programming patterns

## Why This Layer Exists

### Problem: Tight Coupling
Without domain entities, raw data structures from external systems (APIs, databases) flow directly through the application:

```python
# BAD: Tight coupling to API response structure
def process_data(api_response: dict):
    frame_id = api_response["id"]  # What if API changes "id" to "identifier"?
    frame_name = api_response["name"]
    # Business logic tightly coupled to API structure
```

### Solution: Domain Entities
Domain entities decouple internal representation from external data sources:

```python
# GOOD: Business logic depends on stable domain model
@dataclass(frozen=True, slots=True)
class Frame:
    id: str
    name: str
    location: str | None

def process_frame(frame: Frame):
    # Business logic uses domain model
    # API changes only affect the adapter layer
```

## Benefits

### 1. Testability
Pure Python objects with no external dependencies are trivial to test:

```python
def test_frame_creation():
    frame = Frame(id="1", name="Test", location="London")
    assert frame.id == "1"
    assert frame.name == "Test"
```

### 2. Maintainability
Business logic is isolated and easy to understand:
- No imports of external libraries
- No dependencies on frameworks
- Clear, simple Python classes

### 3. Flexibility
Domain entities can be reused across:
- Different applications
- Different contexts
- Different frameworks

### 4. Protection from External Changes
External system changes (API format, database schema) cannot affect domain logic:

```
API changes field name: "id" → "identifier"
├─ Adapter layer: Update mapping
├─ Domain layer: NO CHANGES
└─ Application layer: NO CHANGES
```

## Structure

```
model/
├── __init__.py          # Domain entities (Frame, etc.)
└── README.md           # This file
```

## Current Entities

### Frame
Represents a frame in the business domain.

**Attributes:**
- `id`: Unique identifier
- `name`: Human-readable name
- `location`: Optional geographical location

**Design Choices:**
- `frozen=True`: Immutable for data integrity
- `slots=True`: Memory efficiency
- `location: str | None`: Optional field using Python 3.10+ union syntax

## Usage Example

```python
from example_project.model import Frame

# Create domain entity
frame = Frame(
    id="frame_123",
    name="Main Frame",
    location="London, UK"
)

# Entities are immutable
# frame.id = "new_id"  # ❌ Raises FrozenInstanceError

# Use in business logic
def calculate_frame_metrics(frame: Frame) -> dict:
    return {
        "frame_id": frame.id,
        "has_location": frame.location is not None
    }
```

## Adding New Entities

When adding new domain entities:

1. **Define in `__init__.py`**:
   ```python
   @dataclass(frozen=True, slots=True)
   class NewEntity:
       field1: str
       field2: int
   ```

2. **Use Immutability**: Always use `frozen=True` unless you have a specific reason not to

3. **Type Hints**: Use proper type hints for all fields

4. **Documentation**: Add docstring explaining business concept

5. **Keep Pure**: No imports from outer layers (application, adapter, composition)

## Dependencies

**Depends on:** Nothing (innermost layer)

**Depended upon by:**
- Application layer (use_case.py)
- Adapter layer (parsers, storage)

## Clean Architecture Context

```
┌─────────────────────────────────────┐
│   Composition (Infrastructure)      │  ← Outermost: Wiring & Config
│   ┌─────────────────────────────┐   │
│   │      Adapter Layer          │   │  ← Protocols & Implementations
│   │   ┌─────────────────────┐   │   │
│   │   │  Application Layer  │   │   │  ← Use Cases
│   │   │  ┌──────────────┐   │   │   │
│   │   │  │ DOMAIN LAYER │   │   │   │  ← YOU ARE HERE
│   │   │  │   (Model)    │   │   │   │
│   │   │  └──────────────┘   │   │   │
│   │   └─────────────────────┘   │   │
│   └─────────────────────────────┘   │
└─────────────────────────────────────┘

Dependencies flow INWARD only
```

## Best Practices

### ✅ DO
- Keep entities simple and focused
- Use immutable data structures
- Represent core business concepts
- Use type hints
- Document business meaning

### ❌ DON'T
- Import from outer layers
- Add framework dependencies
- Include infrastructure concerns
- Make entities mutable without good reason
- Add technical implementation details

## Related Documentation

- [Application Layer README](../application/README.md) - How use cases orchestrate domain entities
- [Adapter Layer README](../adapter/README.md) - How adapters transform external data to domain entities
- [Composition Layer README](../composition/README.md) - How dependencies are wired together

## Further Reading

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design by Eric Evans](https://www.domainlanguage.com/ddd/)
- [Python dataclasses documentation](https://docs.python.org/3/library/dataclasses.html)
