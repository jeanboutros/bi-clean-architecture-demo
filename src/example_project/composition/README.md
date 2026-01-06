# Composition Layer (Infrastructure)

## Overview

The Composition layer represents the **outermost circle** of Clean Architecture. This is the **Composition Root** - the single place where all dependency decisions are made and components are wired together.

## Key Principles

### Composition Root
- **Single Location**: All dependency wiring happens in one place
- **Knows Everything**: This layer imports and knows about all other layers
- **Known by Nothing**: No other layer imports or knows about this layer

### Dependency Injection
Creates concrete implementations and injects them into use cases:
```python
# This layer creates...
api_client = GraphQLService()
parser = AsIsParser()
storage = StorageService(...)

# ...and injects into use case
use_case = DownloadAndStore(
    download_client=api_client,
    parser=parser,
    storage=storage
)
```

### Configuration Management
Handles environment-specific settings and implementation choices:
```python
# Development configuration
context = Context.default()  # Uses filesystem storage

# Production configuration  
context = Context.production()  # Uses Unity Catalog storage
```

### Entry Points
Provides orchestration-friendly entry points:
```python
# Called by Airflow, Databricks, cron, etc.
ingest_frames_from_api_into_landing_layer(context)
```

## Structure

```
composition/
├── __init__.py          # Layer documentation
├── context.py          # Configuration and class loading
└── frames.py           # Wiring and entry points
```

## Key Concepts

### ClassImportPath

**Purpose:** String-based dynamic class loading for dependency injection.

**Why String-Based Loading?**

Without dynamic loading (tight coupling):
```python
# ❌ Hard-coded imports
from example_project.interface.graphql_service import GraphQLService
from example_project.storage import StorageService

def setup():
    return DownloadAndStore(
        download_client=GraphQLService(),  # Can't change without code change
        storage=StorageService(...)        # Can't change without code change
    )
```

With dynamic loading (loose coupling):
```python
# ✅ Configuration-driven imports
frames_class = ClassImportPath.from_string(
    "example_project.interface.graphql_service.GraphQLService"
)

# Change to different implementation by changing string:
# "example_project.interface.frame_service.FrameService"

api_class = frames_class.import_class()
api_instance = api_class()
```

**Benefits:**
1. **Configuration-Driven**: Change implementations via config files
2. **Lazy Loading**: Import only when needed
3. **Circular Import Prevention**: Break circular dependencies
4. **Plugin Architecture**: Load implementations discovered at runtime
5. **Environment-Specific**: Different implementations for dev/test/prod

**API:**
```python
# Parse from string
path = ClassImportPath.from_string("module.path.ClassName")

# Import the class
my_class = path.import_class()

# Or use shorthand
my_class = path()

# Get string representation
str(path)  # "module.path.ClassName"
```

### Context

**Purpose:** Configuration container specifying which implementations to use.

**Why Context?**

Without Context:
```python
# ❌ Wiring scattered throughout codebase
def workflow_a():
    use_case = DownloadAndStore(GraphQLService(), AsIsParser(), StorageService(...))

def workflow_b():
    use_case = DownloadAndStore(FrameService(), AsIsParser(), StorageService(...))

# Inconsistent, hard to manage, lots of duplication
```

With Context:
```python
# ✅ Centralised configuration
context = Context.default()

def workflow_a(context):
    # Wiring based on context
    use_case = create_use_case(context)

def workflow_b(context):
    # Same wiring logic, different context
    use_case = create_use_case(context)
```

**Benefits:**
1. **Centralised Decisions**: All dependency choices in one place
2. **Environment Management**: Different contexts for dev/staging/prod
3. **Testability**: Test contexts with mock implementations
4. **Documentation**: Context serves as documentation of dependencies
5. **Consistency**: Same configuration used across application

**Attributes:**
```python
class Context(NamedTuple):
    environment: str                    # "dev", "staging", "prod"
    project_package_name: str           # Base package name
    frames_class: ClassImportPath       # API client to use
    frames_parser_class: ClassImportPath  # Parser to use
    storage_class: ClassImportPath      # Storage backend to use
```

**Methods:**

#### Context.default()
Standard configuration for local development:
- GraphQLService for API
- AsIsParser for parsing
- StorageService for filesystem storage

```python
context = Context.default()
```

#### Context.notebook_default()
Configuration for Databricks notebooks:
- Same as default() currently
- Provides flexibility for notebook-specific implementations

```python
context = Context.notebook_default()
```

**Adding New Context Methods:**

```python
@classmethod
def test(cls):
    """Test context with mock implementations."""
    return cls(
        environment="test",
        project_package_name="example_project",
        frames_class=ClassImportPath.from_string(
            "tests.mocks.MockApiClient"
        ),
        frames_parser_class=ClassImportPath.from_string(
            "tests.mocks.MockParser"
        ),
        storage_class=ClassImportPath.from_string(
            "tests.mocks.MockStorage"
        ),
    )

@classmethod
def production(cls):
    """Production context with Unity Catalog."""
    return cls(
        environment="prod",
        project_package_name="example_project",
        frames_class=ClassImportPath.from_string(
            "example_project.interface.graphql_service.GraphQLService"
        ),
        frames_parser_class=ClassImportPath.from_string(
            "example_project.parser.AsIsParser"
        ),
        storage_class=ClassImportPath.from_string(
            "example_project.storage.UnityCatalogVolumeStorageService"
        ),
    )
```

## Dependency Wiring (frames.py)

### import_frame_service_classes()

**Purpose:** Import classes specified in Context.

**Process:**
```python
def import_frame_service_classes(context):
    # Import API client class
    frame_service_class = context.frames_class.import_class()
    
    # Import parser class (shorthand syntax)
    frame_service_parser_class = context.frames_parser_class()
    
    # Import storage class (shorthand syntax)
    frame_service_storage_class = context.storage_class()
    
    return frame_service_class, frame_service_parser_class, frame_service_storage_class
```

**Returns:** Tuple of (API class, Parser class, Storage class)

### ingest_frames_from_api_into_landing_layer()

**Purpose:** Entry point for frame ingestion orchestration.

**This is the Composition Root** - where all the pieces come together:

```python
def ingest_frames_from_api_into_landing_layer(context: Context):
    # 1. Import classes based on context
    api_class, parser_class, storage_class = import_frame_service_classes(context)
    
    # 2. Instantiate components
    api_client = api_class()
    parser = parser_class()
    
    # 3. Handle storage-specific initialisation
    if is_unity_catalog_storage(storage_class):
        storage = storage_class(
            catalog_name=context.base_catalog_name,
            schema_name="default",
            volume_name="sales-reporting-gen2-temp",
            file_path=Path("landing_layer_test/2025_file.json")
        )
    else:
        storage = storage_class(
            file_path=Path("/Volumes/.../landing_layer_test/2025_file.json")
        )
    
    # 4. Create use case with dependencies
    use_case = DownloadAndStore(
        context=context,
        download_client=api_client,
        parser=parser,
        storage=storage
    )
    
    # 5. Execute
    use_case.execute()
```

**Orchestration Integration:**

This function is designed for external orchestration systems:

#### Airflow
```python
from airflow.operators.python import PythonOperator

def run_ingestion():
    context = Context.default()
    ingest_frames_from_api_into_landing_layer(context)

task = PythonOperator(
    task_id="ingest_frames",
    python_callable=run_ingestion,
    dag=dag
)
```

#### Databricks
```python
# In Databricks notebook
from example_project.composition.context import Context
from example_project.composition.frames import ingest_frames_from_api_into_landing_layer

context = Context.notebook_default()
ingest_frames_from_api_into_landing_layer(context)
```

#### CLI/Cron
```python
# In main.py or CLI script
if __name__ == "__main__":
    context = Context.default()
    ingest_frames_from_api_into_landing_layer(context)
```

### Type Guards

Type guards enable type-safe storage initialisation:

```python
def is_unity_catalog_storage(
    storage_class: type[Storage] | type[UnityCatalogStorage],
) -> TypeGuard[type[UnityCatalogStorage]]:
    """Type guard to narrow storage class type."""
    return storage_class.storage_type == "unity-catalog-volume"
```

**Usage:**
```python
if is_unity_catalog_storage(storage_class):
    # Type checker knows: type[UnityCatalogStorage]
    storage = storage_class(
        catalog_name="...",
        schema_name="...",
        volume_name="...",
        file_path=Path("...")
    )
else:
    # Type checker knows: type[Storage]
    storage = storage_class(file_path=Path("..."))
```

**Why Needed?**

Different storage types have different constructors:
- `UnityCatalogStorage`: Requires catalog/schema/volume parameters
- `Storage`: Requires only file_path

Type guards enable handling these differences whilst maintaining abstraction.

## Clean Architecture Benefits

### Dependency Flow

```
Composition → Adapter Implementations → Adapter Protocols → Application → Domain
   (knows)         (knows)              (defines)         (uses)     (pure)
```

**Key Insight:** Dependencies flow **inward**. Outer layers depend on inner layers, never the reverse.

### The Power of Composition

**Before (Without Clean Architecture):**
```python
# Tightly coupled, hard to change
def ingest():
    client = GraphQLService()  # Hard-coded
    data = client.download()
    with open("/tmp/out.json", "w") as f:  # Hard-coded
        json.dump(data, f)

# To change API or storage:
# 1. Modify this function
# 2. Risk breaking other code
# 3. Can't test without real API/filesystem
```

**After (With Clean Architecture):**
```python
# Loosely coupled, easy to change
def ingest(context: Context):
    # Configuration-driven
    api_class = context.frames_class()
    storage_class = context.storage_class()
    
    # Wiring
    api_client = api_class()
    storage = storage_class(...)
    
    # Use case
    use_case = DownloadAndStore(
        download_client=api_client,
        storage=storage
    )
    use_case.execute()

# To change API or storage:
# 1. Update Context
# 2. No other code changes needed
# 3. Easy to test with mock context
```

### Swapping Implementations

Change implementations by changing Context:

```python
# Development: Fast mock API, local storage
dev_context = Context(
    frames_class=ClassImportPath.from_string("mocks.MockApiClient"),
    storage_class=ClassImportPath.from_string("mocks.InMemoryStorage"),
    ...
)

# Testing: Controlled test doubles
test_context = Context(
    frames_class=ClassImportPath.from_string("tests.TestApiClient"),
    storage_class=ClassImportPath.from_string("tests.TestStorage"),
    ...
)

# Production: Real API, Unity Catalog
prod_context = Context(
    frames_class=ClassImportPath.from_string("...GraphQLService"),
    storage_class=ClassImportPath.from_string("...UnityCatalogVolumeStorageService"),
    ...
)

# Same wiring logic for all!
ingest_frames_from_api_into_landing_layer(context)
```

### A/B Testing

Run different implementations simultaneously:

```python
# Strategy A: GraphQL + Unity Catalog
context_a = Context(
    frames_class=ClassImportPath.from_string("...GraphQLService"),
    storage_class=ClassImportPath.from_string("...UnityCatalogVolumeStorageService"),
    ...
)

# Strategy B: REST + S3
context_b = Context(
    frames_class=ClassImportPath.from_string("...RestService"),
    storage_class=ClassImportPath.from_string("...S3StorageService"),
    ...
)

# Compare
ingest_frames_from_api_into_landing_layer(context_a)
ingest_frames_from_api_into_landing_layer(context_b)
```

## Adding New Entry Points

To add a new orchestrated workflow:

1. **Define use case** (application layer):
   ```python
   class ValidateAndTransform(UseCase):
       def __init__(self, validator: Validator, transformer: Transformer):
           self.validator = validator
           self.transformer = transformer
       
       def execute(self):
           if self.validator.is_valid():
               return self.transformer.transform()
   ```

2. **Add to Context**:
   ```python
   class Context(NamedTuple):
       ...
       validator_class: ClassImportPath
       transformer_class: ClassImportPath
   ```

3. **Create entry point** (composition layer):
   ```python
   def validate_and_transform_workflow(context: Context):
       # Import
       validator_class = context.validator_class()
       transformer_class = context.transformer_class()
       
       # Instantiate
       validator = validator_class()
       transformer = transformer_class()
       
       # Wire
       use_case = ValidateAndTransform(
           validator=validator,
           transformer=transformer
       )
       
       # Execute
       use_case.execute()
   ```

4. **Call from orchestrator**:
   ```python
   context = Context.default()
   validate_and_transform_workflow(context)
   ```

## Testing Composition

### Unit Testing Wiring

```python
def test_import_frame_service_classes():
    context = Context.default()
    
    api_class, parser_class, storage_class = import_frame_service_classes(context)
    
    assert api_class.__name__ == "GraphQLService"
    assert parser_class.__name__ == "AsIsParser"
    assert storage_class.__name__ == "StorageService"

def test_is_unity_catalog_storage():
    unity_storage = UnityCatalogVolumeStorageService
    filesystem_storage = StorageService
    
    assert is_unity_catalog_storage(unity_storage) == True
    assert is_unity_catalog_storage(filesystem_storage) == False
```

### Integration Testing

```python
def test_ingest_frames_integration(tmp_path):
    # Create test context with real implementations
    context = Context(
        environment="test",
        project_package_name="example_project",
        frames_class=ClassImportPath.from_string(
            "example_project.interface.graphql_service.GraphQLService"
        ),
        frames_parser_class=ClassImportPath.from_string(
            "example_project.parser.AsIsParser"
        ),
        storage_class=ClassImportPath.from_string(
            "example_project.storage.StorageService"
        ),
    )
    
    # Override storage path for test
    # (Note: Would need to make path configurable or use test-specific context)
    
    # Execute full workflow
    ingest_frames_from_api_into_landing_layer(context)
    
    # Verify results
    # assert output_file.exists()
```

### Testing with Mocks

```python
def test_ingest_with_mocks():
    # Create context with mock implementations
    mock_context = Context(
        environment="test",
        project_package_name="example_project",
        frames_class=ClassImportPath.from_string("tests.mocks.MockApiClient"),
        frames_parser_class=ClassImportPath.from_string("tests.mocks.MockParser"),
        storage_class=ClassImportPath.from_string("tests.mocks.MockStorage"),
    )
    
    # Mock implementations can track calls, return controlled data
    ingest_frames_from_api_into_landing_layer(mock_context)
    
    # Verify mock interactions
    # assert MockStorage.save_called == True
```

## Dependencies

**Depends on:**
- Domain layer (model/)
- Application layer (application/)
- Adapter protocols (adapter/protocols.py)
- Adapter implementations (adapter/interface/, adapter/parser/, adapter/storage/)

**Depended upon by:**
- Nothing (outermost layer)
- Called by orchestration systems (Airflow, Databricks, cron, etc.)

## Clean Architecture Context

```
┌─────────────────────────────────────┐
│ COMPOSITION LAYER (Infrastructure)  │  ← YOU ARE HERE
│     Composition Root                │  ← All dependencies wired here
│ ┌─────────────────────────────────┐ │
│ │      Adapter Layer              │ │  ← Imports implementations
│ │   ┌─────────────────────────┐   │ │
│ │   │  Application Layer      │   │ │  ← Creates use cases
│ │   │  ┌──────────────┐       │   │ │
│ │   │  │ Domain Layer │       │   │ │  ← Uses domain entities
│ │   │  └──────────────┘       │   │ │
│ │   └─────────────────────────┘   │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘

This layer knows about EVERYTHING
Nothing knows about this layer
```

## Best Practices

### ✅ DO
- Keep all wiring in composition layer
- Use Context for configuration
- Provide orchestration-friendly entry points
- Use type guards for type-safe initialisation
- Document entry point contracts
- Make entry points self-contained

### ❌ DON'T
- Add business logic (belongs in use cases)
- Create dependencies in other layers
- Hard-code implementations (use Context)
- Let other layers import composition layer
- Create circular dependencies

## Configuration Management

### Environment Variables

```python
import os

@classmethod
def from_environment(cls):
    """Create context from environment variables."""
    environment = os.getenv("APP_ENV", "dev")
    
    if environment == "prod":
        return cls.production()
    elif environment == "test":
        return cls.test()
    else:
        return cls.default()
```

### Configuration Files

```python
import json

@classmethod
def from_config_file(cls, config_path: Path):
    """Create context from JSON config file."""
    with open(config_path) as f:
        config = json.load(f)
    
    return cls(
        environment=config["environment"],
        project_package_name=config["package"],
        frames_class=ClassImportPath.from_string(config["frames_class"]),
        frames_parser_class=ClassImportPath.from_string(config["parser_class"]),
        storage_class=ClassImportPath.from_string(config["storage_class"]),
    )
```

## Related Documentation

- [Domain Layer README](../model/README.md) - Core business entities
- [Application Layer README](../application/README.md) - Use cases
- [Adapter Layer README](../adapter/README.md) - Protocols and implementations

## Further Reading

- [Dependency Injection](https://en.wikipedia.org/wiki/Dependency_injection)
- [Composition Root](https://blog.ploeh.dk/2011/07/28/CompositionRoot/)
- [Inversion of Control](https://martinfowler.com/bliki/InversionOfControl.html)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
