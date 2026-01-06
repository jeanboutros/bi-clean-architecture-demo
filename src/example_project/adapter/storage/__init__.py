"""\nStorage Implementations and Commands\n\nThis module provides storage implementations that persist data to various backends.\nIt demonstrates both the Adapter pattern (for storage) and the Command pattern\n(for reusable operations like type conversion and file writing).\n\nDesign Patterns:\n----------------\n1. **Adapter Pattern**: Storage classes adapt different backends to Storage protocol\n2. **Command Pattern**: ConvertToBytes and SaveToFile encapsulate operations as objects\n3. **DRY Principle**: Shared logic (conversion, writing) extracted to commands\n\nBenefits of Command Pattern:\n-----------------------------\n- **Reusability**: Same commands used by all storage implementations\n- **Testability**: Test conversion logic independently of storage\n- **Flexibility**: Easy to add new conversion types or storage operations\n- **Single Responsibility**: Each command does one thing well\n\"\""\n\nfrom typing import Any, Protocol\nfrom pathlib import Path\nimport json\nfrom datetime import datetime, date, timedelta\nfrom example_project.adapter.protocols import Storage, UnityCatalogStorage\n\n\nclass Command(Protocol):\n    \"\"\"\n    Command pattern protocol for encapsulating operations as objects.\n    \n    The Command pattern turns operations into first-class objects that can be:\n    - Passed as parameters\n    - Stored in data structures\n    - Composed and chained\n    - Tested independently\n    \n    Benefits:\n    ---------\n    1. **Reusability**: Same command used by multiple clients\n    2. **Composability**: Commands can invoke other commands\n    3. **Testability**: Isolated testing of individual operations\n    4. **Separation of Concerns**: Operation logic separate from callers\n    \n    Usage Pattern:\n    --------------\n    Commands implement execute() for the actual operation and __call__() for\n    convenient invocation: command(args) instead of command.execute(args)\n    \"\"\"\n    def execute(self, *args: Any, **kwds: Any) -> Any:\n        ...
    def __call__(self, *args: Any, **kwds: Any) ->Any:\n        """Convenience method to invoke command via () syntax."""
        return self.execute(*args, **kwds)
\nclass ConvertToBytes(Command):\n    \"\"\"\n    Command for converting various data types to bytes for file serialisation.\n    \n    This command handles type conversion for data persistence, supporting multiple\n    Python types and providing consistent serialisation across the application.\n    \n    Supported Types:\n    ----------------\n    - str: UTF-8 encoding\n    - bytes/bytearray: Direct or converted to bytes\n    - dict/list: JSON serialisation\n    - Numeric types (int/float/bool): String representation\n    - Date/time types: ISO format strings\n    \n    Clean Architecture Benefit:\n    --------------------------\n    By centralising conversion logic in a command, we achieve:\n    - **Consistency**: All storage implementations use same conversion rules\n    - **DRY**: No duplication of conversion logic across storage backends\n    - **Maintainability**: Single place to update conversion rules\n    - **Extensibility**: Easy to add new type support\n    \n    Example Usage:\n    --------------\n    >>> converter = ConvertToBytes()\n    >>> converter({\"key\": \"value\"})  # Returns b'{\"key\": \"value\"}'\n    >>> converter(\"text\")  # Returns b'text'\n    >>> converter(123)  # Returns b'123'\n    \n    Error Handling:\n    ---------------\n    Raises Exception for unsupported types with clear error message.\n    \"\"\"\n    def execute(self, d: Any) -> bytes:\n        \"\"\"\n        Convert data to bytes representation.\n        \n        Parameters:\n            d: Data of any supported type to convert\n        \n        Returns:\n            bytes: UTF-8 encoded byte representation of data\n        \n        Raises:\n            Exception: If data type is not supported\n        \"\"\"
        if isinstance(d, str):
            d = d.encode("utf-8")
        elif isinstance(d, bytes):
            pass
        elif isinstance(d, bytearray):
            d = bytes(d)
        elif isinstance(d, dict):
            d = json.dumps(d).encode("utf-8")
        elif isinstance(d, list):
            d = json.dumps(d).encode("utf-8")
        elif isinstance(d, float):
            d = str(d).encode("utf-8")
        elif isinstance(d, int):
            d = str(d).encode("utf-8")
        elif isinstance(d, bool):
            d = str(d).encode("utf-8")
        elif isinstance(d, datetime):
            d = d.isoformat().encode("utf-8")
        elif isinstance(d, date):
            d = d.isoformat().encode("utf-8")
        elif isinstance(d, timedelta):
            d = d.total_seconds().encode("utf-8")
        else:
            raise Exception(f"Unsupported type: {type(d)}")
        return d
\nclass SaveToFile(Command):\n    \"\"\"\n    Command for saving data to filesystem with automatic type conversion.\n    \n    This command orchestrates the complete file-saving operation:\n    1. Convert data to bytes using ConvertToBytes command\n    2. Ensure parent directory exists (create if needed)\n    3. Write bytes to file\n    \n    Command Composition:\n    --------------------\n    SaveToFile demonstrates command composition by using ConvertToBytes internally.\n    This shows how commands can be built from other commands, creating higher-level\n    operations from primitive ones.\n    \n    Benefits:\n    ---------\n    - **Automatic Directory Creation**: Parent directories created if missing\n    - **Type Flexibility**: Accepts any type supported by ConvertToBytes\n    - **Error Prevention**: Prevents common filesystem errors\n    - **Reusability**: Used by all storage implementations\n    \n    Example Usage:\n    --------------\n    >>> saver = SaveToFile()\n    >>> saver({\"data\": \"value\"}, Path(\"/tmp/output.json\"))\n    >>> saver(\"text content\", Path(\"/tmp/file.txt\"))\n    \n    File System Safety:\n    -------------------\n    - Creates parent directories with parents=True\n    - Uses exist_ok=True to avoid errors if directory exists\n    - Opens file in binary write mode ('wb') for cross-platform compatibility\n    \"\"\"\n    def execute(self, d: Any, file_path: Path):\n        \"\"\"\n        Save data to file with automatic type conversion and directory creation.\n        \n        Parameters:\n            d: Data to save (any type supported by ConvertToBytes)\n            file_path: Destination path for the file\n        \n        Side Effects:\n            - Creates parent directories if they don't exist\n            - Writes or overwrites file at file_path\n        \"\"\"

        # Convert the data to bytes for serialization
        converter = ConvertToBytes()
        d = converter(d)

        # Check if the parent directory exists and create it if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the data to the file
        with file_path.open("wb") as f:
            f.write(d)
\nclass UnityCatalogVolumeStorageService(UnityCatalogStorage):\n    \"\"\"\n    Storage adapter for Databricks Unity Catalog volumes.\n    \n    This implementation adapts Databricks Unity Catalog volumes to the Storage protocol,\n    enabling the application to persist data to Unity Catalog without the business\n    logic knowing about Databricks-specific details.\n    \n    Unity Catalog Overview:\n    -----------------------\n    Unity Catalog uses a three-level namespace for data organisation:\n    - Catalog: Top-level container (e.g., 'dev_catalog_base')\n    - Schema: Logical grouping within catalog (e.g., 'default')\n    - Volume: Storage location within schema (e.g., 'sales-reporting-gen2-temp')\n    \n    Path Construction:\n    ------------------\n    Unity Catalog volumes are mounted at /Volumes/{catalog}/{schema}/{volume}/\n    This class constructs absolute paths by combining the mount point with the\n    relative file_path provided during initialisation.\n    \n    Clean Architecture Benefits:\n    ---------------------------\n    1. **Technology Independence**: Business logic doesn't know about Unity Catalog\n    2. **Substitutability**: Can swap with StorageService via configuration\n    3. **Testability**: Can test with mock storage in non-Databricks environments\n    4. **Flexibility**: Easy to migrate between storage systems\n    \n    Parameters:\n    -----------\n    catalog_name : str\n        Unity Catalog catalog identifier\n    schema_name : str\n        Schema within the catalog\n    volume_name : str\n        Volume within the schema\n    file_path : Path\n        Relative path within the volume (must be a file, not directory)\n    \n    Raises:\n        Exception: If file_path ends with '/' (indicates directory)\n    \n    Example Usage:\n    --------------\n    >>> storage = UnityCatalogVolumeStorageService(\n    ...     catalog_name=\"dev_catalog_base\",\n    ...     schema_name=\"default\",\n    ...     volume_name=\"sales-reporting-gen2-temp\",\n    ...     file_path=Path(\"landing_layer/data.json\")\n    ... )\n    >>> storage.save({\"key\": \"value\"})  # Saves to Unity Catalog volume\n    \"\"\"\n    def __init__(self, catalog_name: str, schema_name: str, volume_name: str, file_path: Path):
        self.catalog_name = catalog_name
        self.schema_name = schema_name
        self.volume_name = volume_name
        self.file_path = Path(file_path)

        if self.file_path.as_posix().endswith("/"):
            raise Exception(f"file_path should be a file, not a directory")

    storage_type: str = "unity-catalog-volume"

    def _absolute_path(self) -> Path:
        return Path("/Volumes", self.catalog_name, self.schema_name, self.volume_name, self.file_path)
    

class UnityCatalogVolumeStorageService(UnityCatalogStorage):
    """
    Storage adapter for Databricks Unity Catalog volumes.
    
    This implementation adapts Databricks Unity Catalog volumes to the Storage protocol,
    enabling the application to persist data to Unity Catalog without the business
    logic knowing about Databricks-specific details.
    
    Unity Catalog Overview:
    -----------------------
    Unity Catalog uses a three-level namespace for data organisation:
    - Catalog: Top-level container (e.g., 'dev_catalog_base')
    - Schema: Logical grouping within catalog (e.g., 'default')
    - Volume: Storage location within schema (e.g., 'sales-reporting-gen2-temp')
    
    Path Construction:
    ------------------
    Unity Catalog volumes are mounted at /Volumes/{catalog}/{schema}/{volume}/
    This class constructs absolute paths by combining the mount point with the
    relative file_path provided during initialisation.
    
    Clean Architecture Benefits:
    ---------------------------
    1. **Technology Independence**: Business logic doesn't know about Unity Catalog
    2. **Substitutability**: Can swap with StorageService via configuration
    3. **Testability**: Can test with mock storage in non-Databricks environments
    4. **Flexibility**: Easy to migrate between storage systems
    
    Parameters:
    -----------
    catalog_name : str
        Unity Catalog catalog identifier
    schema_name : str
        Schema within the catalog
    volume_name : str
        Volume within the schema
    file_path : Path
        Relative path within the volume (must be a file, not directory)
    
    Raises:
        Exception: If file_path ends with '/' (indicates directory)
    
    Example Usage:
    --------------
    >>> storage = UnityCatalogVolumeStorageService(
    ...     catalog_name="dev_catalog_base",
    ...     schema_name="default",
    ...     volume_name="sales-reporting-gen2-temp",
    ...     file_path=Path("landing_layer/data.json")
    ... )
    >>> storage.save({"key": "value"})  # Saves to Unity Catalog volume
    """
    def __init__(self, catalog_name: str, schema_name: str, volume_name: str, file_path: Path):
        self.catalog_name = catalog_name
        self.schema_name = schema_name
        self.volume_name = volume_name
        self.file_path = Path(file_path)

        if self.file_path.as_posix().endswith("/"):
            raise Exception(f"file_path should be a file, not a directory")

    storage_type: str = "unity-catalog-volume"

    def _absolute_path(self) -> Path:
        """
        Construct absolute path for Unity Catalog volume.
        
        Combines the Unity Catalog mount point (/Volumes/) with catalog, schema,
        volume, and file path to create the full absolute path.
        
        Returns:
            Path: Absolute path in Unity Catalog volume filesystem
        """
        return Path("/Volumes", self.catalog_name, self.schema_name, self.volume_name, self.file_path)
    
    def save(self, d: Any):
        """
        Save data to Unity Catalog volume.
        
        Uses SaveToFile command with Unity Catalog-specific absolute path.
        
        Parameters:
            d: Data to save (any type supported by ConvertToBytes)
        """
        save_to_file = SaveToFile()
        save_to_file(d, self._absolute_path())


class StorageService(Storage):
    """
    Storage adapter for local and network filesystems.
    
    This implementation provides filesystem-based storage that works with local disks,
    network mounts, or any path-accessible storage. It implements the Storage protocol,
    making it interchangeable with other storage backends like Unity Catalog.
    
    Path Handling:
    --------------
    Unlike UnityCatalogVolumeStorageService which uses relative paths, StorageService
    expects absolute paths or resolves relative paths to absolute paths. This provides
    flexibility for development, testing, and non-Databricks deployments.
    
    Clean Architecture Benefits:
    ---------------------------
    1. **Development Flexibility**: Use local filesystem during development
    2. **Testing**: Easy to test without external dependencies
    3. **Portability**: Works on any system with filesystem access
    4. **Substitutability**: Drop-in replacement for Unity Catalog storage
    
    Use Cases:
    ----------
    - Local development and testing
    - CI/CD pipelines with local storage
    - Network-mounted storage (NFS, SMB)
    - Containerised environments with volume mounts
    
    Parameters:
    -----------
    file_path : Path
        Absolute path to the target file (or relative, will be resolved)
    
    Example Usage:
    --------------
    >>> storage = StorageService(file_path=Path("/tmp/output/data.json"))
    >>> storage.save({"key": "value"})  # Saves to /tmp/output/data.json
    
    Path Resolution:
    ----------------
    Uses Path.resolve() to convert relative paths to absolute paths, ensuring
    consistent behaviour regardless of current working directory.
    """
    def __init__(self, file_path: Path):
        self.file_path = Path(file_path)

    storage_type: str = "linux-path"

    def _absolute_path(self) -> Path:
        """
        Resolve file path to absolute path.
        
        Converts relative paths to absolute paths using Path.resolve(), which
        resolves symlinks and makes paths absolute based on current working directory.
        
        Returns:
            Path: Absolute filesystem path
        """
        return self.file_path.resolve()
    
    def save(self, d: Any):
        """
        Save data to filesystem.
        
        Uses SaveToFile command with resolved absolute path.
        
        Parameters:
            d: Data to save (any type supported by ConvertToBytes)
        """
        save_to_file = SaveToFile()
        save_to_file(d, self._absolute_path())
