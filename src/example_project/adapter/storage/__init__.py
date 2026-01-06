"""
Storage Implementations and Commands

This module provides storage implementations that persist data to various backends.
It demonstrates both the Adapter pattern (for storage) and the Command pattern
(for reusable operations like type conversion and file writing).

Design Patterns:
----------------
1. **Adapter Pattern**: Storage classes adapt different backends to Storage protocol
2. **Command Pattern**: ConvertToBytes and SaveToFile encapsulate operations as objects
3. **DRY Principle**: Shared logic (conversion, writing) extracted to commands

Benefits of Command Pattern:
-----------------------------
- **Reusability**: Same commands used by all storage implementations
- **Testability**: Test conversion logic independently of storage
- **Flexibility**: Easy to add new conversion types or storage operations
- **Single Responsibility**: Each command does one thing well
"""

from typing import Any, Protocol
from pathlib import Path
import json
from datetime import datetime, date, timedelta
from example_project.adapter.protocols import Storage, UnityCatalogStorage


class Command(Protocol):
    """
    Command pattern protocol for encapsulating operations as objects.

    The Command pattern turns operations into first-class objects that can be:
    - Passed as parameters
    - Stored in data structures
    - Composed and chained
    - Tested independently

    Benefits:
    ---------
    1. **Reusability**: Same command used by multiple clients
    2. **Composability**: Commands can invoke other commands
    3. **Testability**: Isolated testing of individual operations
    4. **Separation of Concerns**: Operation logic separate from callers

    Usage Pattern:
    --------------
    Commands implement execute() for the actual operation and __call__() for
    convenient invocation: command(args) instead of command.execute(args)
    """

    def execute(self, *args: Any, **kwds: Any) -> Any: ...

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """Convenience method to invoke command via () syntax."""
        return self.execute(*args, **kwds)


class ConvertToBytes(Command):
    """
    Command for converting various data types to bytes for file serialisation.

    This command handles type conversion for data persistence, supporting multiple
    Python types and providing consistent serialisation across the application.

    Supported Types:
    ----------------
    - str: UTF-8 encoding
    - bytes/bytearray: Direct or converted to bytes
    - dict/list: JSON serialisation
    - Numeric types (int/float/bool): String representation
    - Date/time types: ISO format strings

    Clean Architecture Benefit:
    --------------------------
    By centralising conversion logic in a command, we achieve:
    - **Consistency**: All storage implementations use same conversion rules
    - **DRY**: No duplication of conversion logic across storage backends
    - **Maintainability**: Single place to update conversion rules
    - **Extensibility**: Easy to add new type support

    Example Usage:
    --------------
    >>> converter = ConvertToBytes()
    >>> converter({"key": "value"})  # Returns b'{"key": "value"}'
    >>> converter("text")  # Returns b'text'
    >>> converter(123)  # Returns b'123'

    Error Handling:
    ---------------
    Raises Exception for unsupported types with clear error message.
    """

    def execute(self, d: Any) -> bytes:
        """
        Convert data to bytes representation.

        Parameters:
            d: Data of any supported type to convert

        Returns:
            bytes: UTF-8 encoded byte representation of data

        Raises:
            Exception: If data type is not supported
        """
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
            d = str(d.total_seconds()).encode("utf-8")
        else:
            raise Exception(f"Unsupported type: {type(d)}")
        return d


class SaveToFile(Command):
    """
    Command for saving data to filesystem with automatic type conversion.

    This command orchestrates the complete file-saving operation:
    1. Convert data to bytes using ConvertToBytes command
    2. Ensure parent directory exists (create if needed)
    3. Write bytes to file

    Command Composition:
    --------------------
    SaveToFile demonstrates command composition by using ConvertToBytes internally.
    This shows how commands can be built from other commands, creating higher-level
    operations from primitive ones.

    Benefits:
    ---------
    - **Automatic Directory Creation**: Parent directories created if missing
    - **Type Flexibility**: Accepts any type supported by ConvertToBytes
    - **Error Prevention**: Prevents common filesystem errors
    - **Reusability**: Used by all storage implementations

    Example Usage:
    --------------
    >>> saver = SaveToFile()
    >>> saver({"data": "value"}, Path("/tmp/output.json"))
    >>> saver("text content", Path("/tmp/file.txt"))

    File System Safety:
    -------------------
    - Creates parent directories with parents=True
    - Uses exist_ok=True to avoid errors if directory exists
    - Opens file in binary write mode ('wb') for cross-platform compatibility
    """

    def execute(self, d: Any, file_path: Path):
        """
        Save data to file with automatic type conversion and directory creation.

        Parameters:
            d: Data to save (any type supported by ConvertToBytes)
            file_path: Destination path for the file

        Side Effects:
            - Creates parent directories if they don't exist
            - Writes or overwrites file at file_path
        """

        # Convert the data to bytes for serialization
        converter = ConvertToBytes()
        d = converter(d)

        # Check if the parent directory exists and create it if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the data to the file
        with file_path.open("wb") as f:
            f.write(d)

        print("Data written into file: ", file_path)


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

    def __init__(
        self, catalog_name: str, schema_name: str, volume_name: str, file_path: Path
    ):
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
        return Path(
            "/Volumes",
            self.catalog_name,
            self.schema_name,
            self.volume_name,
            self.file_path,
        )

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
