"""
Use Case Implementations

This module defines the use cases for the application. Use cases represent specific
business operations and orchestrate the flow between domain entities and adapters.

Clean Architecture Benefits Demonstrated:
-----------------------------------------
1. **Dependency Inversion**: Use cases depend on protocols (abstractions), not concrete
   implementations. This allows swapping storage backends, API clients, or parsers
   without changing the use case logic.

2. **Single Responsibility**: Each use case does one thing. DownloadAndStore handles
   the complete flow of downloading, parsing, and storing data.

3. **Testability**: Use cases can be tested with mock implementations of protocols,
   enabling fast, isolated unit tests.

Use Case Pattern:
-----------------
All use cases implement the UseCase protocol with an execute() method. This provides
a consistent interface for executing business operations throughout the application.
"""

from example_project.adapter.protocols import ApiClass, Parser, Storage
from example_project.composition.context import Context
from typing import Protocol


class UseCase(Protocol):
    """
    Base protocol for all use cases in the application.

    The UseCase protocol establishes a consistent interface for executing business
    operations. This allows use cases to be:
    - Called uniformly via execute()
    - Composed and chained together
    - Wrapped with cross-cutting concerns (logging, monitoring, transactions)

    The __call__ method provides syntactic sugar, allowing use cases to be invoked
    like functions: use_case() instead of use_case.execute()
    """

    def execute(self) -> None: ...

    def __call__(self) -> None:
        self.execute()


class DownloadAndStore(UseCase):
    """
    Use case for downloading data from an API, parsing it, and storing the result.

    This use case demonstrates Clean Architecture's Dependency Inversion Principle:
    it depends on abstractions (ApiClass, Parser, Storage protocols) rather than
    concrete implementations. This provides several key benefits:

    Benefits:
    ---------
    1. **Swappable Components**: Change from FrameService to GraphQLService without
       modifying this class
    2. **Multiple Storage Options**: Switch between filesystem and Unity Catalog
       storage by changing the injected dependency
    3. **Parser Flexibility**: Add JSON→DataFrame or JSON→Domain Entity parsers
       without touching this use case
    4. **Testability**: Mock each dependency independently for isolated testing
    5. **Stability**: This use case should never change due to external system changes

    Why This Matters:
    ----------------
    If we tightly coupled this class to specific implementations (e.g., directly
    importing GraphQLService), every change to the API or storage system would
    require modifying this business logic. With dependency injection via protocols,
    the business logic remains stable and protected from external changes.

    Parameters:
    -----------
    context : Context
        Application context containing configuration and environment information
    download_client : ApiClass
        Protocol implementation for downloading data from external source
    parser : Parser
        Protocol implementation for transforming downloaded data
    storage : Storage
        Protocol implementation for persisting parsed data

    Example:
    --------
    >>> download_and_store = DownloadAndStore(
    ...     context=my_context,
    ...     download_client=GraphQLService(),
    ...     parser=AsIsParser(),
    ...     storage=UnityCatalogVolumeStorageService(...)
    ... )
    >>> download_and_store.execute()  # Orchestrates the complete flow
    """

    def __init__(
        self,
        context: Context,
        download_client: ApiClass,
        parser: Parser,
        storage: Storage,
    ):
        self.context = context
        self.download_client = download_client
        self.parser = parser
        self.storage = storage

    def execute(self):
        data = self.download_client.download()
        parsed_data = self.parser.parse(data)
        self.storage.save(parsed_data)
