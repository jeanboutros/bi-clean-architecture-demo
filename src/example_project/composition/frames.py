"""
Frame Ingestion Orchestration and Dependency Wiring

This module provides the composition root for frame ingestion use cases. It wires
dependencies together based on Context configuration and provides entry points for
external orchestration systems.

Key Responsibilities:
--------------------
1. **Import Dependencies**: Dynamically import classes specified in Context
2. **Instantiate Components**: Create instances of API clients, parsers, storage
3. **Wire Use Cases**: Inject dependencies into use case instances
4. **Provide Entry Points**: Expose orchestration-friendly functions

Clean Architecture Context:
---------------------------
This is the Composition Root - the single place where all dependency decisions are
made. It sits at the outermost layer and is the only layer that knows about concrete
implementations. All other layers depend on abstractions.

Dependency Flow:
----------------
    Context (configuration)
         ↓
    import_frame_service_classes() (import based on config)
         ↓
    ingest_frames_from_api_into_landing_layer() (wire and execute)
         ↓
    DownloadAndStore use case (business logic)

Orchestration Pattern:
----------------------
The ingest_frames_from_api_into_landing_layer() function serves as an entry point for
external orchestration systems (Airflow, Databricks, etc.). It:
- Accepts Context for configuration
- Handles all dependency wiring
- Executes the use case
- Returns control to orchestrator
"""

from typing import TypeGuard
from pathlib import Path
from example_project.composition.context import Context
from example_project.adapter.protocols import (
    ApiClass,
    Parser,
    Storage,
    UnityCatalogStorage,
)
from example_project.application.use_case import DownloadAndStore


def is_unity_catalog_storage(
    storage_class: type[Storage] | type[UnityCatalogStorage],
) -> TypeGuard[type[UnityCatalogStorage]]:
    """
    Type guard for narrowing storage class to Unity Catalog storage.

    Type guards enable type-safe handling of different storage implementations. Python's
    type system can't automatically distinguish between protocol implementations, so we
    use runtime checks with TypeGuard to narrow types.

    Benefits:
    ---------
    1. **Type Safety**: Type checker knows storage_class is UnityCatalogStorage after check
    2. **Correct Initialisation**: Ensures correct parameters for each storage type
    3. **IDE Support**: Better autocomplete and error detection
    4. **Runtime Safety**: Prevents incorrect parameter usage

    How TypeGuard Works:
    --------------------
    After this function returns True, the type checker narrows storage_class from:
        type[Storage] | type[UnityCatalogStorage]
    to:
        type[UnityCatalogStorage]

    This enables type-safe access to Unity Catalog-specific initialisation parameters.

    Parameters:
        storage_class: Storage class to check

    Returns:
        bool: True if storage_class is Unity Catalog storage, False otherwise

    Example Usage:
    --------------
    >>> if is_unity_catalog_storage(storage_class):
    ...     # Type checker knows storage_class is type[UnityCatalogStorage]
    ...     storage = storage_class(catalog_name=..., schema_name=..., ...)
    ... else:
    ...     # Type checker knows storage_class is type[Storage]
    ...     storage = storage_class(file_path=...)
    """
    return storage_class.storage_type == "unity-catalog-volume"


def import_frame_service_classes(
    context: Context,
) -> tuple[type[ApiClass], type[Parser], type[Storage] | type[UnityCatalogStorage]]:
    """
    Import frame service dependencies based on Context configuration.

    This function demonstrates dynamic dependency loading - one of the key techniques
    enabling Clean Architecture's flexibility. Instead of hard-coded imports at the
    top of the file, we import classes based on configuration.

    Dynamic Loading Benefits:
    -------------------------
    1. **Configuration-Driven**: Change implementations without code changes
    2. **Lazy Loading**: Import classes only when needed
    3. **Environment-Specific**: Load different classes for dev/test/prod
    4. **Plugin Architecture**: Support runtime-discovered implementations

    Loading Methods:
    ----------------
    This function demonstrates three equivalent ways to load classes:

    1. Explicit method call:
        frame_service_class = context.frames_class.import_class()

    2. Call syntax (via __call__):
        frame_service_parser_class = context.frames_parser_class()

    3. Same as method 2:
        frame_service_storage_class = context.storage_class()

    All three approaches use ClassImportPath to dynamically import based on strings
    specified in Context.

    Parameters:
        context: Application context with dependency specifications

    Returns:
        tuple: (ApiClass type, Parser type, Storage/UnityCatalogStorage type)

    Example:
    --------
    >>> context = Context.default()
    >>> api_class, parser_class, storage_class = import_frame_service_classes(context)
    >>> api_instance = api_class()  # Create instance of GraphQLService
    """
    # Here we are importing the class
    frame_service_class = context.frames_class.import_class()

    # Here we are importing the parser to parse the data returned by the api
    # This is an alternavie way of calling the class without having to use
    # the import_class() function directly
    frame_service_parser_class = context.frames_parser_class()

    # Here we are importing the storage to store the data parsed by the parser
    # into a storage location or a database
    frame_service_storage_class = context.storage_class()

    return frame_service_class, frame_service_parser_class, frame_service_storage_class


# Entrypoint that an orchestration software need to call
def ingest_frames_from_api_into_landing_layer(context: Context):
    """
    Entry point for frame ingestion orchestration.

    This function serves as the Composition Root for the frame ingestion use case.
    It orchestrates the complete dependency injection and execution flow:

    Execution Flow:
    ---------------
    1. Import classes based on Context configuration
    2. Instantiate API client, parser, and storage
    3. Handle storage-specific initialisation (Unity Catalog vs. filesystem)
    4. Create DownloadAndStore use case with dependencies
    5. Execute the use case

    Clean Architecture in Action:
    -----------------------------
    This function demonstrates Clean Architecture's key benefits:

    **Dependency Inversion**: Use case depends on protocols, this function provides
    concrete implementations

    **Open/Closed**: Add new storage/API/parser by updating Context, not this code
    (though storage initialisation requires conditional logic)

    **Separation of Concerns**: Use case contains business logic, this function
    contains wiring logic

    **Testability**: Can create test context with mock implementations

    Storage-Specific Initialisation:
    --------------------------------
    Different storage types require different initialisation parameters:

    - **Unity Catalog**: Requires catalog_name, schema_name, volume_name, file_path
        Uses relative paths within volume

    - **Filesystem**: Requires file_path only
        Uses absolute paths

    Type guards enable type-safe handling of these differences whilst maintaining
    protocol-based abstraction.

    Orchestration Integration:
    -------------------------
    This function is designed to be called by orchestration systems:

    - **Airflow**: Call from PythonOperator
    - **Databricks**: Call from notebook or job
    - **CI/CD**: Call from deployment script
    - **Cron**: Call from scheduled job

    The function is self-contained (except for Context) and returns after completion,
    making it ideal for orchestration.

    Parameters:
        context: Application context specifying environment and dependencies

    Side Effects:
        - Downloads data from API specified in context
        - Writes file to storage location specified in context
        - Prints status messages to stdout

    Example Usage:
    --------------
    >>> # Local development
    >>> context = Context.default()
    >>> ingest_frames_from_api_into_landing_layer(context)

    >>> # Databricks notebook
    >>> context = Context.notebook_default()
    >>> ingest_frames_from_api_into_landing_layer(context)

    Extending This Function:
    ------------------------
    To add new storage types:
    1. Define new protocol (e.g., S3Storage)
    2. Add type guard (e.g., is_s3_storage)
    3. Add conditional block for initialisation
    4. Add ClassImportPath to Context

    To add new API or parser:
    1. Implement protocol in adapter layer
    2. Add ClassImportPath to Context
    3. No changes needed here (protocols handle it)
    """
    frame_service_class, frame_service_parser_class, frame_service_storage_class = (
        import_frame_service_classes(context=context)
    )

    # The initialisation and the wiring should take place here
    frame_service_client = frame_service_class()
    frame_service_parser = frame_service_parser_class()

    if is_unity_catalog_storage(frame_service_storage_class):
        # Type checker now knows frame_service_storage_class is type[UnityCatalogStorage]
        print("Unity Catalog Volume")

        frame_service_storage = frame_service_storage_class(
            catalog_name=context.base_catalog_name,
            schema_name="default",
            volume_name="sales-reporting-gen2-temp",
            file_path=Path("landing_layer_test/2025_file.json"),
        )
    else:
        print("Filesystem")
        frame_service_storage = frame_service_storage_class(
            file_path=Path(
                "/Volumes/dev_catalog_base/default/sales-reporting-gen2-temp/landing_layer_test/2025_file.json"
            )
        )

    download_and_store = DownloadAndStore(
        context=context,
        download_client=frame_service_client,
        parser=frame_service_parser,
        storage=frame_service_storage,
    )

    download_and_store.execute()
