# Application Layer

## Overview

The Application layer contains **application-specific business rules** and orchestrates the flow of data between the domain layer and outer layers. It implements use cases that define how the system should behave for specific user interactions or system events.

## Key Principles

### Use Case Driven
Each class represents a specific business operation or workflow:
- `DownloadAndStore`: Orchestrates downloading, parsing, and storing data
- Future examples: `ValidateAndTransform`, `SyncAndNotify`, etc.

### Technology Agnostic
- No knowledge of UI frameworks
- No knowledge of databases or storage systems
- No knowledge of external APIs or protocols
- Only depends on **abstractions** (protocols), never concrete implementations

### Orchestration
Coordinates domain entities and adapter implementations to fulfill use cases:
```python
# Use case orchestrates the flow
data = download_client.download()      # Adapter
parsed_data = parser.parse(data)       # Adapter
storage.save(parsed_data)              # Adapter
```

### Single Direction Flow
Data flows from outer layers inward to domain:
```
External API → Adapter → Application → Domain
```

## Benefits

### 1. Clear Business Intent
Each use case explicitly defines what the application does:

```python
class DownloadAndStore(UseCase):
    """Download data, parse it, and save to storage."""
    def execute(self):
        # The code reads like the business requirement
        data = self.download_client.download()
        parsed_data = self.parser.parse(data)
        self.storage.save(parsed_data)
```

### 2. Testability
Use cases can be tested with mock adapters:

```python
def test_download_and_store():
    mock_client = MockApiClient(returns={"data": "test"})
    mock_parser = MockParser(returns={"parsed": "test"})
    mock_storage = MockStorage()
    
    use_case = DownloadAndStore(
        context=test_context,
        download_client=mock_client,
        parser=mock_parser,
        storage=mock_storage
    )
    
    use_case.execute()
    
    assert mock_storage.saved_data == {"parsed": "test"}
```

### 3. Separation of Concerns
Business workflow is separate from technical implementation:
- Use case: "Download, parse, and store"
- Adapters: How to download, how to parse, how to store

### 4. Flexibility
Can support multiple interfaces with same use cases:
- Web UI calls `DownloadAndStore`
- CLI calls `DownloadAndStore`
- API calls `DownloadAndStore`
- Scheduled job calls `DownloadAndStore`

## Structure

```
application/
├── __init__.py          # Layer documentation
├── use_case.py         # Use case implementations
└── README.md           # This file
```

## Use Cases

### UseCase Protocol

All use cases implement the `UseCase` protocol:

```python
class UseCase(Protocol):
    def execute(self) -> None: ...
    
    def __call__(self) -> None:
        self.execute()
```

**Benefits:**
- Consistent interface for all use cases
- Can be composed and chained
- Easy to wrap with cross-cutting concerns (logging, monitoring, transactions)

### DownloadAndStore

**Purpose:** Orchestrates downloading data from an API, parsing it, and storing the result.

**Dependencies:**
- `ApiClass` protocol: Downloads data
- `Parser` protocol: Transforms data
- `Storage` protocol: Persists data

**Clean Architecture Benefits:**

1. **Dependency Inversion**: Depends on protocols, not implementations
   ```python
   # ✅ Depends on abstraction
   def __init__(self, download_client: ApiClass, ...):
   
   # ❌ Would be tight coupling
   # def __init__(self, download_client: GraphQLService, ...):
   ```

2. **Open/Closed**: Add new implementations without modifying use case
   - Swap `FrameService` ↔ `GraphQLService`: No code changes
   - Change storage: No code changes
   - Add new parser: No code changes

3. **Single Responsibility**: Does one thing - orchestrates the flow
   - Doesn't know **how** to download
   - Doesn't know **how** to parse
   - Doesn't know **how** to store
   - Only knows **what** needs to happen

**Example Usage:**

```python
# Composition layer wires dependencies
use_case = DownloadAndStore(
    context=context,
    download_client=GraphQLService(),
    parser=AsIsParser(),
    storage=StorageService(file_path=Path("/tmp/output.json"))
)

# Execute the use case
use_case.execute()
# or
use_case()  # Via __call__
```

## Dependency Inversion Principle

### The Problem Without Dependency Inversion

```python
# ❌ BAD: Direct dependencies on implementations
from example_project.interface.graphql_service import GraphQLService
from example_project.storage import StorageService

class DownloadAndStore:
    def __init__(self):
        # Tightly coupled to specific implementations
        self.client = GraphQLService()
        self.storage = StorageService(Path("/tmp/out.json"))
    
    def execute(self):
        data = self.client.download()
        self.storage.save(data)
```

**Problems:**
- Can't swap implementations without code changes
- Hard to test (requires real API and filesystem)
- Business logic coupled to technical choices
- Changes to GraphQLService affect use case

### The Solution With Dependency Inversion

```python
# ✅ GOOD: Dependencies on protocols
from example_project.adapter.protocols import ApiClass, Storage

class DownloadAndStore:
    def __init__(self, download_client: ApiClass, storage: Storage):
        # Depends on abstractions
        self.download_client = download_client
        self.storage = storage
    
    def execute(self):
        data = self.download_client.download()
        self.storage.save(data)
```

**Benefits:**
- Swap implementations via dependency injection
- Easy to test with mocks
- Business logic independent of technical choices
- Use case stable regardless of implementation changes

## Adding New Use Cases

To add a new use case:

1. **Define the use case class**:
   ```python
   class ValidateAndTransform(UseCase):
       """Validates input data and transforms to target format."""
       
       def __init__(
           self,
           context: Context,
           validator: Validator,
           transformer: Transformer,
       ):
           self.context = context
           self.validator = validator
           self.transformer = transformer
       
       def execute(self):
           if self.validator.is_valid():
               return self.transformer.transform()
           raise ValidationError("Invalid data")
   ```

2. **Define required protocols** (in adapter layer):
   ```python
   class Validator(Protocol):
       def is_valid(self) -> bool: ...
   
   class Transformer(Protocol):
       def transform(self) -> Any: ...
   ```

3. **Create entry point** (in composition layer):
   ```python
   def validate_and_transform_workflow(context: Context):
       validator = context.validator_class()
       transformer = context.transformer_class()
       
       use_case = ValidateAndTransform(
           context=context,
           validator=validator,
           transformer=transformer
       )
       
       use_case.execute()
   ```

## Testing Use Cases

### Unit Testing with Mocks

```python
import pytest
from unittest.mock import Mock

def test_download_and_store_success():
    # Arrange
    mock_context = Mock()
    mock_client = Mock(spec=ApiClass)
    mock_client.download.return_value = {"data": "test"}
    
    mock_parser = Mock(spec=Parser)
    mock_parser.parse.return_value = {"parsed": "test"}
    
    mock_storage = Mock(spec=Storage)
    
    use_case = DownloadAndStore(
        context=mock_context,
        download_client=mock_client,
        parser=mock_parser,
        storage=mock_storage
    )
    
    # Act
    use_case.execute()
    
    # Assert
    mock_client.download.assert_called_once()
    mock_parser.parse.assert_called_once_with({"data": "test"})
    mock_storage.save.assert_called_once_with({"parsed": "test"})
```

### Integration Testing

```python
def test_download_and_store_integration():
    # Use real implementations for integration testing
    context = Context.default()
    
    use_case = DownloadAndStore(
        context=context,
        download_client=GraphQLService(),
        parser=AsIsParser(),
        storage=StorageService(file_path=Path("/tmp/test_output.json"))
    )
    
    use_case.execute()
    
    # Verify file was created
    assert Path("/tmp/test_output.json").exists()
```

## Dependencies

**Depends on:**
- Domain layer (model/) - for domain entities (if used)
- Adapter protocols (adapter/protocols.py) - NOT implementations

**Depended upon by:**
- Composition layer (composition/) - wires use cases with concrete implementations

**Does NOT depend on:**
- Adapter implementations (interface/, parser/, storage/)
- Infrastructure (composition/)
- External libraries or frameworks

## Clean Architecture Context

```
┌─────────────────────────────────────┐
│   Composition (Infrastructure)      │  ← Wires dependencies
│   ┌─────────────────────────────┐   │
│   │      Adapter Layer          │   │  ← Implementations
│   │   ┌─────────────────────┐   │   │
│   │   │ APPLICATION LAYER   │   │   │  ← YOU ARE HERE
│   │   │  (Use Cases)        │   │   │  ← Orchestrates flow
│   │   │  ┌──────────────┐   │   │   │
│   │   │  │ Domain Layer │   │   │   │  ← Business entities
│   │   │  └──────────────┘   │   │   │
│   │   └─────────────────────┘   │   │
│   └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

## Best Practices

### ✅ DO
- Keep use cases focused on single workflows
- Depend on protocols, never implementations
- Make dependencies explicit (constructor injection)
- Document business intent in docstrings
- Test with mocks for unit tests
- Return results or raise exceptions (don't print)

### ❌ DON'T
- Import concrete implementations from adapter layer
- Add infrastructure concerns (logging, monitoring)
- Directly instantiate dependencies (use injection)
- Mix multiple workflows in one use case
- Depend on external frameworks or libraries

## Common Patterns

### Composition Over Inheritance

```python
# ✅ GOOD: Compose use cases from injected dependencies
class DownloadAndStore(UseCase):
    def __init__(self, download_client: ApiClass, parser: Parser, storage: Storage):
        self.download_client = download_client
        self.parser = parser
        self.storage = storage

# ❌ BAD: Inherit from concrete classes
class DownloadAndStore(GraphQLService, StorageService):
    pass
```

### Command Pattern

Use cases are commands - they encapsulate operations:

```python
# Use cases can be queued, logged, or replayed
commands = [
    DownloadAndStore(...),
    ValidateAndTransform(...),
    SyncAndNotify(...)
]

for command in commands:
    command.execute()
```

### Strategy Pattern

Different strategies via different implementations:

```python
# Same use case, different parsing strategy
use_case_raw = DownloadAndStore(..., parser=AsIsParser(), ...)
use_case_transformed = DownloadAndStore(..., parser=JsonToEntityParser(), ...)
```

## Related Documentation

- [Domain Layer README](../model/README.md) - Core business entities
- [Adapter Layer README](../adapter/README.md) - Protocol definitions and implementations
- [Composition Layer README](../composition/README.md) - How use cases are wired

## Further Reading

- [Use Case Driven Object Modelling](https://www.ivarjacobson.com/publications/books/object-oriented-software-engineering-1992)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
