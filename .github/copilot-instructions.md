# Copilot Instructions for Example Project

## Architecture Overview

This project implements a **Clean Architecture** data ingestion pipeline organized into four distinct layers:

```
Domain (model/) → Application (application/) → Adapters (adapter/) → Infrastructure (composition/)
```

**Key principle**: Dependencies flow inward. Outer layers depend on inner layers, never the reverse. This allows swapping implementations (APIs, storage, parsers) without changing business logic.

### Design Principles

This project strictly adheres to:

- **Clean Architecture**: Business logic is isolated from external concerns; dependencies point inward
- **SOLID Principles**:
  - **Single Responsibility**: Each class has one reason to change (e.g., `DownloadAndStore` orchestrates, `SaveToFile` writes)
  - **Open/Closed**: Extend behavior via new implementations, not modifications (add new Storage/Parser/ApiClass)
  - **Liskov Substitution**: All protocol implementations are interchangeable (swap `FrameService` ↔ `GraphQLService`)
  - **Interface Segregation**: Small, focused protocols (`ApiClass`, `Parser`, `Storage`)
  - **Dependency Inversion**: Depend on protocols, not concrete classes (see `DownloadAndStore` constructor)
- **DRY (Don't Repeat Yourself)**: Shared logic extracted to commands (`ConvertToBytes`, `SaveToFile`) and reused across storage implementations

### Layer Responsibilities

- **Domain** (`model/`): Core entities (currently minimal)
- **Application** (`application/use_case.py`): Business logic via `DownloadAndStore` use case
- **Adapters** (`adapter/`): Protocols and implementations for external interactions
  - `protocols.py`: Defines `ApiClass`, `Parser`, `Storage`, `UnityCatalogStorage` protocols
  - `interface/`: API clients (FrameService, GraphQLService)
  - `parser/`: Data transformation (AsIsParser)
  - `storage/`: Persistence (UnityCatalogVolumeStorageService, StorageService)
- **Infrastructure** (`composition/`): Dependency wiring and configuration

## Dependency Injection Pattern

**Critical**: This codebase uses string-based dynamic class loading via `ClassImportPath` in [composition/context.py](src/example_project/composition/context.py).

```python
# Context specifies dependencies as strings
frames_class = ClassImportPath.from_string("example_project.interface.graphql_service.GraphQLService")

# Composition layer imports and wires them
frame_service_class = context.frames_class.import_class()
frame_service_client = frame_service_class()
```

**When adding new implementations**:
1. Define implementation class conforming to protocol in `adapter/`
2. Update `Context.default()` or create new context method with the new class path
3. Wire dependencies in [composition/frames.py](src/example_project/composition/frames.py)'s `ingest_frames_from_api_into_landing_layer()`

## Protocol-Based Design

All adapters implement protocols from [adapter/protocols.py](src/example_project/adapter/protocols.py):

- **ApiClass**: Must have `download() -> Any` method
- **Parser**: Must have `parse(p: Any) -> Any` method
- **Storage**: Must have `storage_type: str` and `save(d: Any) -> None` method
- **UnityCatalogStorage**: Storage variant with Unity Catalog parameters

**Type guards** are used for storage specialization (see `is_unity_catalog_storage()` in [composition/frames.py](src/example_project/composition/frames.py)).

## Storage Implementations

Two storage backends exist with different initialization patterns:

```python
# Unity Catalog (Databricks volume storage)
UnityCatalogVolumeStorageService(
    catalog_name="dev_catalog_base",
    schema_name="default", 
    volume_name="sales-reporting-gen2-temp",
    file_path=Path("landing_layer_test/2025_file.json")  # Relative path
)

# Filesystem
StorageService(
    file_path=Path("/absolute/path/to/file.json")  # Absolute path
)
```

Both use `SaveToFile` command that handles type conversion via `ConvertToBytes` (supports dict, list, str, bytes, datetime, etc.).

## Development Workflows

### Build & Run

```bash
# Activate virtual environment (uv-managed)
source .venv/bin/activate

# Run the project
python -m example_project
# or
uv run example-project
```

### Code Quality

```bash
# Linting (project uses both)
flake8
ruff check

# Auto-fix with ruff
ruff check --fix
```

### Project Structure

- Entry point: [src/example_project/__main__.py](src/example_project/__main__.py) → [main.py](src/example_project/main.py)
- Orchestration entry: `ingest_frames_from_api_into_landing_layer()` in [composition/frames.py](src/example_project/composition/frames.py)

## Databricks Integration

[ExampleImplementation.py](src/example_project/ExampleImplementation.py) shows Databricks notebook usage:

```python
# Databricks-specific setup
sys.path.remove(current_path)  # Force package imports
sys.path.append(project_path)  # Add project root

# Use notebook-specific context
notebook_context = Context.notebook_default()
ingest_frames_from_api_into_landing_layer(context=notebook_context)
```

**Key difference**: Unity Catalog paths use `/Volumes/{catalog}/{schema}/{volume}` prefix.

## Conventions

- **Python 3.12+** required
- **Import paths**: Always use fully qualified module paths (e.g., `example_project.adapter.protocols`)
- **Protocol conformance**: Use `@runtime_checkable` when runtime type checking is needed
- **File paths**: Use `pathlib.Path`, convert with `.as_posix()` for cross-platform compatibility
- **Type hints**: Use Protocol for interfaces, TypeGuard for narrowing types
- **Naming**: `*Service` suffix for external interface implementations, `*Storage` for persistence
- **Language**: Use British English spelling (e.g., "colour", "organise", "behaviour")
- **Writing style**: Avoid filler words and adverbs in comments, docstrings, and variable names (write "validates data" not "actually validates data very carefully")

## Adding New Features

**To add a new API source**:
1. Create class in `adapter/interface/` implementing `ApiClass` protocol
2. Update `Context.default()` with new `ClassImportPath`

**To add a new storage backend**:
1. Create class in `adapter/storage/` implementing `Storage` or `UnityCatalogStorage`
2. Add type guard if needed (see `is_unity_catalog_storage`)
3. Update wiring logic in `ingest_frames_from_api_into_landing_layer()`

**To add a new parser**:
1. Create class in `adapter/parser/` implementing `Parser` protocol
2. Update `Context.default()` with new `ClassImportPath`
