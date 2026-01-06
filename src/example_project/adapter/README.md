# Adapter Layer

## Overview

The Adapter layer acts as the **boundary between the application's core logic and external systems**. It contains protocols (interfaces) that define contracts and concrete implementations that adapt external systems to work with the application.

## Key Principles

### Dependency Inversion
- Inner layers define protocols
- Outer layers provide implementations
- Dependencies point inward (implementations depend on protocols, not vice versa)

### Protocol-Based Design
All external interactions go through well-defined protocols:
- `ApiClass`: Defines contract for API clients
- `Parser`: Defines contract for data transformation
- `Storage`: Defines contract for data persistence

### Isolation
Shields core business logic from external system changes:
- API changes? Only adapter implementations change
- New storage backend? Add new implementation
- Different data format? Add new parser

### Substitutability
Multiple implementations of the same protocol are **interchangeable**:
- Swap `FrameService` ↔ `GraphQLService` via configuration
- Switch `StorageService` ↔ `UnityCatalogVolumeStorageService` without code changes

## Structure

```
adapter/
├── __init__.py              # Layer documentation
├── protocols.py             # Protocol definitions
├── interface/              # API client implementations
│   ├── __init__.py
│   ├── frame_service.py    # REST-style API client
│   └── graphql_service.py  # GraphQL API client
├── parser/                 # Data transformation implementations
│   └── __init__.py         # AsIsParser
└── storage/                # Persistence implementations
    └── __init__.py         # StorageService, UnityCatalogVolumeStorageService
```

## Protocols

### Why Protocols Instead of Abstract Base Classes?

Python protocols use **structural subtyping** (duck typing) rather than **nominal subtyping**:

```python
# ❌ Abstract Base Class: Requires explicit inheritance
from abc import ABC, abstractmethod

class ApiClientABC(ABC):
    @abstractmethod
    def download(self): ...

class MyClient(ApiClientABC):  # Must inherit
    def download(self): ...

# ✅ Protocol: Structural typing
from typing import Protocol

class ApiClass(Protocol):
    def download(self): ...

class MyClient:  # No inheritance required
    def download(self): ...  # Implements protocol implicitly
```

**Benefits:**
- Less coupling (no inheritance required)
- Better compatibility with third-party code
- More Pythonic and flexible
- Easier to retrofit existing classes

### ApiClass Protocol

**Purpose:** Defines contract for downloading data from external sources.

**Contract:**
```python
class ApiClass(Protocol):
    def download(self) -> Any: ...
```

**Implementations:**
- `FrameService`: REST-style API client
- `GraphQLService`: GraphQL API client
- Future: `FileSystemClient`, `MessageQueueClient`, etc.

**Benefits:**
- Application doesn't know about HTTP, GraphQL, or other protocols
- Easy to add new API sources
- Can mock for testing without network calls
- Support multiple API versions simultaneously

### Parser Protocol

**Purpose:** Defines contract for transforming data.

**Contract:**
```python
class Parser(Protocol):
    def parse(self, p: Any) -> Any: ...
```

**Implementations:**
- `AsIsParser`: Pass-through (no transformation)
- Future: `JsonToDataFrameParser`, `JsonToDomainEntityParser`, etc.

**Benefits:**
- API response format changes don't affect storage
- Different transformations for different destinations
- Add validation, enrichment, or filtering
- Convert between formats

### Storage Protocol

**Purpose:** Defines contract for persisting data.

**Contract:**
```python
@runtime_checkable
class Storage(Protocol):
    storage_type: str
    def save(self, d: Any) -> None: ...
```

**Implementations:**
- `StorageService`: Local/network filesystem
- `UnityCatalogVolumeStorageService`: Databricks Unity Catalog

**Runtime Checkable:**
The `@runtime_checkable` decorator enables `isinstance()` checks:

```python
if isinstance(storage, Storage):
    storage.save(data)
```

### UnityCatalogStorage Protocol

**Purpose:** Specialised protocol for Unity Catalog storage.

**Contract:**
```python
@runtime_checkable
class UnityCatalogStorage(Protocol):
    storage_type: str
    def __init__(self, catalog_name: str, schema_name: str, 
                 volume_name: str, file_path: Path): ...
    def save(self, d: Any) -> None: ...
```

**Why Separate Protocol?**
Unity Catalog requires specific initialisation parameters that don't apply to other storage types:
- Makes requirements explicit
- Enables type guards for Unity Catalog-specific logic
- Maintains flexibility for other storage types

## Implementations

### API Clients (interface/)

#### FrameService
REST-style API client implementation.

**Current State:** Stub returning mock data

**Production Implementation Would:**
- Make HTTP requests to actual REST API
- Handle authentication and headers
- Process pagination
- Handle errors and retries

#### GraphQLService
GraphQL API client implementation.

**Current State:** Stub returning mock data

**Production Implementation Would:**
- Execute GraphQL queries
- Handle authentication (JWT, API keys)
- Manage query complexity and batching
- Handle GraphQL-specific errors

**Interchangeability Example:**
```python
# Change via configuration, not code
# Before:
context = Context(frames_class="...FrameService")

# After:
context = Context(frames_class="...GraphQLService")

# Use case code unchanged!
```

### Parsers (parser/)

#### AsIsParser
Pass-through parser with no transformation.

**Use Cases:**
- API data format matches storage requirements
- Want to store raw data for later processing
- Testing or debugging API responses
- Prototyping before implementing transformation

**Future Parsers:**
- `JsonToDomainEntityParser`: Map JSON to domain entities
- `JsonToDataFrameParser`: Convert to pandas DataFrame
- `DataCleaningParser`: Validate and clean data
- `EnrichmentParser`: Add computed fields or external data

### Storage (storage/)

#### Command Pattern
Storage implementations use the **Command pattern** for reusable operations:

```python
class Command(Protocol):
    def execute(self, *args, **kwargs) -> Any: ...
    def __call__(self, *args, **kwargs) -> Any:
        return self.execute(*args, **kwargs)
```

**Commands:**
- `ConvertToBytes`: Type conversion for serialisation
- `SaveToFile`: File writing with directory creation

**Benefits:**
- Reusability: Same commands used by all storage implementations
- Testability: Test conversion logic independently
- Single Responsibility: Each command does one thing
- DRY: No duplication across storage backends

#### ConvertToBytes
Converts various Python types to bytes for file serialisation.

**Supported Types:**
- `str`: UTF-8 encoding
- `bytes`/`bytearray`: Direct or converted
- `dict`/`list`: JSON serialisation
- Numeric types: String representation
- Date/time types: ISO format strings

**Example:**
```python
converter = ConvertToBytes()
converter({"key": "value"})  # Returns b'{"key": "value"}'
converter("text")            # Returns b'text'
converter(123)               # Returns b'123'
```

#### SaveToFile
Orchestrates file saving with automatic type conversion.

**Process:**
1. Convert data to bytes (using `ConvertToBytes`)
2. Ensure parent directory exists
3. Write bytes to file

**Example:**
```python
saver = SaveToFile()
saver({"data": "value"}, Path("/tmp/output.json"))
```

#### StorageService
Filesystem-based storage implementation.

**Features:**
- Works with local disks, network mounts
- Absolute path handling
- Cross-platform compatibility

**Use Cases:**
- Local development and testing
- CI/CD pipelines
- Network-mounted storage (NFS, SMB)
- Containerised environments

**Example:**
```python
storage = StorageService(file_path=Path("/tmp/output/data.json"))
storage.save({"key": "value"})
```

#### UnityCatalogVolumeStorageService
Databricks Unity Catalog volume storage implementation.

**Unity Catalog Overview:**
Three-level namespace:
- **Catalog**: Top-level container (e.g., `dev_catalog_base`)
- **Schema**: Logical grouping (e.g., `default`)
- **Volume**: Storage location (e.g., `sales-reporting-gen2-temp`)

**Path Construction:**
```
/Volumes/{catalog}/{schema}/{volume}/{file_path}
/Volumes/dev_catalog_base/default/sales-reporting-gen2-temp/landing_layer/data.json
```

**Example:**
```python
storage = UnityCatalogVolumeStorageService(
    catalog_name="dev_catalog_base",
    schema_name="default",
    volume_name="sales-reporting-gen2-temp",
    file_path=Path("landing_layer/data.json")  # Relative path
)
storage.save({"key": "value"})
```

## Design Patterns

### Adapter Pattern
Adapters wrap external systems and present them through protocol interfaces:

```
External System → Adapter → Protocol → Application
  (GraphQL)    (GraphQLSvc) (ApiClass)  (Use Case)
```

**Benefit:** Application interacts with consistent interface regardless of external system.

### Strategy Pattern
Different strategies provided via different implementations:

```python
# Different storage strategies
storage_filesystem = StorageService(...)
storage_unity = UnityCatalogVolumeStorageService(...)

# Same interface, different strategy
storage_filesystem.save(data)
storage_unity.save(data)
```

### Command Pattern
Operations encapsulated as objects:

```python
# Commands are reusable, testable, composable
converter = ConvertToBytes()
saver = SaveToFile()

# Used by multiple storage implementations
bytes_data = converter(data)
saver(bytes_data, path)
```

## Type Guards

Type guards enable type-safe handling of different implementations:

```python
def is_unity_catalog_storage(
    storage_class: type[Storage] | type[UnityCatalogStorage],
) -> TypeGuard[type[UnityCatalogStorage]]:
    return storage_class.storage_type == "unity-catalog-volume"

# Usage
if is_unity_catalog_storage(storage_class):
    # Type checker knows storage_class is type[UnityCatalogStorage]
    storage = storage_class(catalog_name=..., schema_name=..., ...)
else:
    # Type checker knows storage_class is type[Storage]
    storage = storage_class(file_path=...)
```

**Benefits:**
- Type safety at runtime
- Correct initialisation parameters
- Better IDE support (autocomplete, error detection)

## Adding New Implementations

### Adding New API Client

1. **Create implementation**:
   ```python
   # adapter/interface/rest_client.py
   from example_project.adapter.protocols import ApiClass
   
   class RestClient(ApiClass):
       def __init__(self, base_url: str, api_key: str):
           self.base_url = base_url
           self.api_key = api_key
       
       def download(self):
           # Make REST API call
           return requests.get(f"{self.base_url}/data").json()
   ```

2. **Update Context**:
   ```python
   frames_class = ClassImportPath.from_string(
       "example_project.interface.rest_client.RestClient"
   )
   ```

### Adding New Parser

1. **Create implementation**:
   ```python
   # adapter/parser/json_to_entity.py
   from example_project.adapter.protocols import Parser
   from example_project.model import Frame
   
   class JsonToEntityParser(Parser):
       def parse(self, data: dict) -> list[Frame]:
           return [
               Frame(
                   id=str(item["id"]),
                   name=item["name"],
                   location=item.get("location")
               )
               for item in data["payload"]
           ]
   ```

2. **Update Context**:
   ```python
   frames_parser_class = ClassImportPath.from_string(
       "example_project.parser.json_to_entity.JsonToEntityParser"
   )
   ```

### Adding New Storage Backend

1. **Define protocol** (if needed):
   ```python
   @runtime_checkable
   class S3Storage(Protocol):
       storage_type: str
       def __init__(self, bucket: str, key: str): ...
       def save(self, d: Any) -> None: ...
   ```

2. **Create implementation**:
   ```python
   class S3StorageService(S3Storage):
       storage_type = "s3"
       
       def __init__(self, bucket: str, key: str):
           self.bucket = bucket
           self.key = key
       
       def save(self, d: Any):
           converter = ConvertToBytes()
           data_bytes = converter(d)
           # Upload to S3
   ```

3. **Add type guard**:
   ```python
   def is_s3_storage(
       storage_class: type[Storage] | type[S3Storage],
   ) -> TypeGuard[type[S3Storage]]:
       return storage_class.storage_type == "s3"
   ```

4. **Update wiring logic** (composition/frames.py):
   ```python
   if is_s3_storage(storage_class):
       storage = storage_class(bucket="my-bucket", key="data.json")
   elif is_unity_catalog_storage(storage_class):
       storage = storage_class(catalog_name=..., ...)
   else:
       storage = storage_class(file_path=...)
   ```

## Testing Adapters

### Unit Testing

```python
def test_graphql_service_download():
    service = GraphQLService()
    data = service.download()
    
    assert isinstance(data, dict)
    assert "payload" in data
    assert isinstance(data["payload"], list)

def test_convert_to_bytes():
    converter = ConvertToBytes()
    
    assert converter({"key": "value"}) == b'{"key": "value"}'
    assert converter("text") == b'text'
    assert converter(123) == b'123'

def test_storage_service_save(tmp_path):
    storage = StorageService(file_path=tmp_path / "test.json")
    storage.save({"key": "value"})
    
    assert (tmp_path / "test.json").exists()
    content = (tmp_path / "test.json").read_text()
    assert content == '{"key": "value"}'
```

### Integration Testing

```python
def test_api_to_storage_integration(tmp_path):
    # Test full flow through adapters
    client = GraphQLService()
    parser = AsIsParser()
    storage = StorageService(file_path=tmp_path / "output.json")
    
    data = client.download()
    parsed = parser.parse(data)
    storage.save(parsed)
    
    assert (tmp_path / "output.json").exists()
```

## Dependencies

**Depends on:**
- Domain layer (model/) - for domain entities (optional)
- Python standard library
- Type hints (`typing` module)

**Depended upon by:**
- Application layer (application/) - uses protocols
- Composition layer (composition/) - uses implementations

**Does NOT depend on:**
- Application layer
- Composition layer

## Clean Architecture Context

```
┌─────────────────────────────────────┐
│   Composition (Infrastructure)      │  ← Wires adapters
│   ┌─────────────────────────────┐   │
│   │   ADAPTER LAYER             │   │  ← YOU ARE HERE
│   │   ├─ Protocols              │   │  ← Contracts
│   │   ├─ interface/             │   │  ← API clients
│   │   ├─ parser/                │   │  ← Transformers
│   │   └─ storage/               │   │  ← Persistence
│   │   ┌─────────────────────┐   │   │
│   │   │  Application Layer  │   │   │  ← Uses protocols
│   │   │  ┌──────────────┐   │   │   │
│   │   │  │ Domain Layer │   │   │   │
│   │   │  └──────────────┘   │   │   │
│   │   └─────────────────────┘   │   │
│   └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

## Best Practices

### ✅ DO
- Define protocols before implementations
- Keep protocols small and focused
- Use `@runtime_checkable` when runtime type checks needed
- Document protocol contracts in docstrings
- Make adapters stateless when possible
- Handle errors appropriately in implementations

### ❌ DON'T
- Import application or composition layers
- Add business logic to adapters (belongs in use cases)
- Create god protocols with many methods
- Use inheritance when composition suffices
- Leak external system details to inner layers

## Related Documentation

- [Domain Layer README](../model/README.md) - Core business entities
- [Application Layer README](../application/README.md) - Use cases that depend on protocols
- [Composition Layer README](../composition/README.md) - How adapters are wired

## Further Reading

- [Adapter Pattern](https://en.wikipedia.org/wiki/Adapter_pattern)
- [Strategy Pattern](https://en.wikipedia.org/wiki/Strategy_pattern)
- [Command Pattern](https://en.wikipedia.org/wiki/Command_pattern)
- [Python Protocols (PEP 544)](https://peps.python.org/pep-0544/)
- [Type Guards (PEP 647)](https://peps.python.org/pep-0647/)
