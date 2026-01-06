"""\nFrame Ingestion Orchestration and Dependency Wiring\n\nThis module provides the composition root for frame ingestion use cases. It wires\ndependencies together based on Context configuration and provides entry points for\nexternal orchestration systems.\n\nKey Responsibilities:\n--------------------\n1. **Import Dependencies**: Dynamically import classes specified in Context\n2. **Instantiate Components**: Create instances of API clients, parsers, storage\n3. **Wire Use Cases**: Inject dependencies into use case instances\n4. **Provide Entry Points**: Expose orchestration-friendly functions\n\nClean Architecture Context:\n---------------------------\nThis is the Composition Root - the single place where all dependency decisions are\nmade. It sits at the outermost layer and is the only layer that knows about concrete\nimplementations. All other layers depend on abstractions.\n\nDependency Flow:\n----------------\n    Context (configuration)\n         ↓\n    import_frame_service_classes() (import based on config)\n         ↓\n    ingest_frames_from_api_into_landing_layer() (wire and execute)\n         ↓\n    DownloadAndStore use case (business logic)\n\nOrchestration Pattern:\n----------------------\nThe ingest_frames_from_api_into_landing_layer() function serves as an entry point for\nexternal orchestration systems (Airflow, Databricks, etc.). It:\n- Accepts Context for configuration\n- Handles all dependency wiring\n- Executes the use case\n- Returns control to orchestrator\n\"\""\n\nfrom typing import TypeGuard
from pathlib import Path
from example_project.composition.context import Context
from example_project.adapter.protocols import ApiClass, Parser, Storage, UnityCatalogStorage
from example_project.application.use_case import DownloadAndStore


def is_unity_catalog_storage(\n    storage_class: type[Storage] | type[UnityCatalogStorage],\n) -> TypeGuard[type[UnityCatalogStorage]]:\n    \"\"\"\n    Type guard for narrowing storage class to Unity Catalog storage.\n    \n    Type guards enable type-safe handling of different storage implementations. Python's\n    type system can't automatically distinguish between protocol implementations, so we\n    use runtime checks with TypeGuard to narrow types.\n    \n    Benefits:\n    ---------\n    1. **Type Safety**: Type checker knows storage_class is UnityCatalogStorage after check\n    2. **Correct Initialisation**: Ensures correct parameters for each storage type\n    3. **IDE Support**: Better autocomplete and error detection\n    4. **Runtime Safety**: Prevents incorrect parameter usage\n    \n    How TypeGuard Works:\n    --------------------\n    After this function returns True, the type checker narrows storage_class from:\n        type[Storage] | type[UnityCatalogStorage]\n    to:\n        type[UnityCatalogStorage]\n    \n    This enables type-safe access to Unity Catalog-specific initialisation parameters.\n    \n    Parameters:\n        storage_class: Storage class to check\n    \n    Returns:\n        bool: True if storage_class is Unity Catalog storage, False otherwise\n    \n    Example Usage:\n    --------------\n    >>> if is_unity_catalog_storage(storage_class):\n    ...     # Type checker knows storage_class is type[UnityCatalogStorage]\n    ...     storage = storage_class(catalog_name=..., schema_name=..., ...)\n    ... else:\n    ...     # Type checker knows storage_class is type[Storage]\n    ...     storage = storage_class(file_path=...)\n    \"\"\"
    return storage_class.storage_type == "unity-catalog-volume"
\ndef import_frame_service_classes(\n    context: Context,\n) -> tuple[type[ApiClass], type[Parser], type[Storage] | type[UnityCatalogStorage]]:\n    \"\"\"\n    Import frame service dependencies based on Context configuration.\n    \n    This function demonstrates dynamic dependency loading - one of the key techniques\n    enabling Clean Architecture's flexibility. Instead of hard-coded imports at the\n    top of the file, we import classes based on configuration.\n    \n    Dynamic Loading Benefits:\n    -------------------------\n    1. **Configuration-Driven**: Change implementations without code changes\n    2. **Lazy Loading**: Import classes only when needed\n    3. **Environment-Specific**: Load different classes for dev/test/prod\n    4. **Plugin Architecture**: Support runtime-discovered implementations\n    \n    Loading Methods:\n    ----------------\n    This function demonstrates three equivalent ways to load classes:\n    \n    1. Explicit method call:\n        frame_service_class = context.frames_class.import_class()\n    \n    2. Call syntax (via __call__):\n        frame_service_parser_class = context.frames_parser_class()\n    \n    3. Same as method 2:\n        frame_service_storage_class = context.storage_class()\n    \n    All three approaches use ClassImportPath to dynamically import based on strings\n    specified in Context.\n    \n    Parameters:\n        context: Application context with dependency specifications\n    \n    Returns:\n        tuple: (ApiClass type, Parser type, Storage/UnityCatalogStorage type)\n    \n    Example:\n    --------\n    >>> context = Context.default()\n    >>> api_class, parser_class, storage_class = import_frame_service_classes(context)\n    >>> api_instance = api_class()  # Create instance of GraphQLService\n    \"\"\"
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
\n\n# Entrypoint that an orchestration software need to call\ndef ingest_frames_from_api_into_landing_layer(context: Context):\n    \"\"\"\n    Entry point for frame ingestion orchestration.\n    \n    This function serves as the Composition Root for the frame ingestion use case.\n    It orchestrates the complete dependency injection and execution flow:\n    \n    Execution Flow:\n    ---------------\n    1. Import classes based on Context configuration\n    2. Instantiate API client, parser, and storage\n    3. Handle storage-specific initialisation (Unity Catalog vs. filesystem)\n    4. Create DownloadAndStore use case with dependencies\n    5. Execute the use case\n    \n    Clean Architecture in Action:\n    -----------------------------\n    This function demonstrates Clean Architecture's key benefits:\n    \n    **Dependency Inversion**: Use case depends on protocols, this function provides\n    concrete implementations\n    \n    **Open/Closed**: Add new storage/API/parser by updating Context, not this code\n    (though storage initialisation requires conditional logic)\n    \n    **Separation of Concerns**: Use case contains business logic, this function\n    contains wiring logic\n    \n    **Testability**: Can create test context with mock implementations\n    \n    Storage-Specific Initialisation:\n    --------------------------------\n    Different storage types require different initialisation parameters:\n    \n    - **Unity Catalog**: Requires catalog_name, schema_name, volume_name, file_path\n        Uses relative paths within volume\n    \n    - **Filesystem**: Requires file_path only\n        Uses absolute paths\n    \n    Type guards enable type-safe handling of these differences whilst maintaining\n    protocol-based abstraction.\n    \n    Orchestration Integration:\n    -------------------------\n    This function is designed to be called by orchestration systems:\n    \n    - **Airflow**: Call from PythonOperator\n    - **Databricks**: Call from notebook or job\n    - **CI/CD**: Call from deployment script\n    - **Cron**: Call from scheduled job\n    \n    The function is self-contained (except for Context) and returns after completion,\n    making it ideal for orchestration.\n    \n    Parameters:\n        context: Application context specifying environment and dependencies\n    \n    Side Effects:\n        - Downloads data from API specified in context\n        - Writes file to storage location specified in context\n        - Prints status messages to stdout\n    \n    Example Usage:\n    --------------\n    >>> # Local development\n    >>> context = Context.default()\n    >>> ingest_frames_from_api_into_landing_layer(context)\n    \n    >>> # Databricks notebook\n    >>> context = Context.notebook_default()\n    >>> ingest_frames_from_api_into_landing_layer(context)\n    \n    Extending This Function:\n    ------------------------\n    To add new storage types:\n    1. Define new protocol (e.g., S3Storage)\n    2. Add type guard (e.g., is_s3_storage)\n    3. Add conditional block for initialisation\n    4. Add ClassImportPath to Context\n    \n    To add new API or parser:\n    1. Implement protocol in adapter layer\n    2. Add ClassImportPath to Context\n    3. No changes needed here (protocols handle it)\n    \"\"\"
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
            file_path=Path("/Volumes/dev_catalog_base/default/sales-reporting-gen2-temp/landing_layer_test/2025_file.json")
        )

    download_and_store = DownloadAndStore(
        context=context,
        download_client=frame_service_client,
        parser=frame_service_parser,
        storage=frame_service_storage,
    )

    download_and_store.execute()
