"""
Adapter Protocols - Contracts for External System Integration

This module defines the protocols (interfaces) that all adapters must implement. Protocols
establish contracts between the application core and external systems, enabling dependency
inversion and loose coupling.

Protocol-Based Design Benefits:
--------------------------------
1. **Dependency Inversion**: Application depends on abstractions, not implementations
2. **Open/Closed Principle**: Add new implementations without modifying existing code
3. **Liskov Substitution**: All implementations are interchangeable
4. **Interface Segregation**: Small, focused protocols with single responsibilities
5. **Testing**: Easy to create test doubles (mocks, stubs, fakes)

Why Protocols Instead of Abstract Base Classes:
-----------------------------------------------
Python protocols use structural subtyping (duck typing) rather than nominal subtyping.
This means a class implements a protocol by having the required methods/attributes,
without explicitly inheriting from it. This provides:
- Less coupling (no inheritance required)
- Better compatibility with third-party code
- More Pythonic and flexible design

Protocol Usage Pattern:
-----------------------
1. Define protocol in this module (e.g., ApiClass)
2. Create implementation in appropriate subdirectory (e.g., interface/graphql_service.py)
3. Use type hints with protocol in application layer
4. Wire concrete implementation in composition layer
"""

from typing import Protocol, Any, runtime_checkable
from pathlib import Path


class ApiClass(Protocol):
    """
    Protocol for external API clients that download data.
    
    This protocol abstracts the concept of "downloading data from somewhere". The actual
    source could be:
    - REST API (FrameService)
    - GraphQL API (GraphQLService)
    - File system
    - Message queue
    - Database
    
    Benefits:
    ---------
    - Application layer doesn't know or care about API implementation details
    - Easy to add new API sources without changing business logic
    - Can mock for testing without network calls
    - Supports multiple API versions simultaneously
    
    Example Implementations:
    ------------------------
    - FrameService: REST-style API client
    - GraphQLService: GraphQL-style API client
    
    Returns:
        Any: Raw data structure from the API (typically dict or list)
    """
    def download(self) -> Any: ...


class Parser(Protocol):
    """
    Protocol for transforming downloaded data into application-specific format.
    
    Parsers sit between the API and storage, transforming raw API responses into
    the format required by the application or storage layer. This separation allows:
    
    Benefits:
    ---------
    - API response format changes don't affect storage layer
    - Can transform data differently for different destinations
    - Add validation, enrichment, or filtering logic
    - Convert between formats (JSON → DataFrame, JSON → Domain Entities)
    
    Example Implementations:
    ------------------------
    - AsIsParser: Pass-through with no transformation
    - JsonToDataFrameParser: Convert JSON to pandas DataFrame
    - JsonToDomainEntityParser: Map JSON to domain model instances
    
    Parameters:
        p: Raw data from API (Any type to support various formats)
    
    Returns:
        Any: Parsed/transformed data ready for storage
    """
    def parse(self, p: Any) -> Any: ...


@runtime_checkable
class Storage(Protocol):
    """
    Protocol for persisting data to storage systems.
    
    The Storage protocol abstracts data persistence, allowing the application to
    save data without knowing the underlying storage mechanism. This enables:
    
    Benefits:
    ---------
    - Switch between storage backends without changing business logic
    - Support multiple storage destinations simultaneously
    - Test with in-memory storage instead of real databases
    - Add new storage types (cloud, database) easily
    
    Runtime Checkable:
    ------------------
    The @runtime_checkable decorator allows isinstance() checks at runtime.
    This enables type guards for distinguishing between storage implementations.
    
    Example Implementations:
    ------------------------
    - StorageService: Local/network filesystem storage
    - UnityCatalogVolumeStorageService: Databricks Unity Catalog volumes
    - S3StorageService: AWS S3 buckets (future)
    - DatabaseStorageService: Relational database (future)
    
    Attributes:
        storage_type: Identifier for the storage backend type
    
    Parameters:
        d: Data to persist (format depends on parser output)
    """
    storage_type: str

    def save(self, d: Any) -> None: ...


@runtime_checkable
class UnityCatalogStorage(Protocol):
    """
    Specialised protocol for Databricks Unity Catalog volume storage.
    
    This protocol extends the Storage concept with Unity Catalog-specific configuration.
    Unity Catalog uses a three-level namespace (catalog.schema.volume) for organising
    data in Databricks environments.
    
    Why a Separate Protocol:
    ------------------------
    Unity Catalog requires specific initialisation parameters (catalog_name, schema_name,
    volume_name) that don't apply to other storage types. Having a separate protocol:
    - Makes these requirements explicit
    - Enables type guards for Unity Catalog-specific logic
    - Maintains flexibility for other storage types
    
    Type Guards:
    ------------
    Use with type guards (see composition/frames.py) to handle Unity Catalog-specific
    initialisation whilst maintaining protocol-based abstraction:
    
        if is_unity_catalog_storage(storage_class):
            storage = storage_class(catalog_name=..., schema_name=..., ...)
        else:
            storage = storage_class(file_path=...)
    
    Parameters:
        catalog_name: Unity Catalog catalog identifier
        schema_name: Schema within the catalog
        volume_name: Volume within the schema
        file_path: Relative path within the volume
    """
    storage_type: str

    def __init__(
        self, catalog_name: str, schema_name: str, volume_name: str, file_path: Path
    ): ...

    def save(self, d: Any) -> None: ...
