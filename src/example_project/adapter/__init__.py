"""
Adapter Layer - External Interface Protocols and Implementations

This layer acts as the boundary between the application's core logic and external systems.
It contains protocols (interfaces) that define contracts and concrete implementations that
adapt external systems to work with the application.

Key Principles:
--------------
- **Dependency Inversion**: Inner layers define protocols; outer layers provide implementations
- **Protocol-Based Design**: All external interactions go through well-defined protocols
- **Isolation**: Shields core business logic from external system changes
- **Substitutability**: Multiple implementations of the same protocol are interchangeable

Layer Structure:
----------------
- protocols.py: Defines contracts (ApiClass, Parser, Storage, etc.)
- interface/: API client implementations (FrameService, GraphQLService)
- parser/: Data transformation implementations (AsIsParser)
- storage/: Persistence implementations (StorageService, UnityCatalogVolumeStorageService)

Benefits:
---------
- **Testability**: Mock implementations for testing without external dependencies
- **Flexibility**: Swap implementations without changing business logic
- **Maintainability**: External system changes contained within adapters
- **Technology Independence**: Core logic doesn't know about REST, GraphQL, or storage details

Clean Architecture Context:
---------------------------
The Adapter layer is the outermost application layer (before infrastructure). It depends
on the Application and Domain layers but is independent of specific frameworks or external
systems. The Infrastructure/Composition layer wires adapters to actual implementations.
"""