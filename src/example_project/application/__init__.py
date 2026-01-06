"""Application Layer - Use Cases and Application Business Rules

This layer contains application-specific business rules and orchestrates the flow of data
between the domain layer and the outer layers. It implements use cases that define how
the system should behave for specific user interactions or system events.

Key Principles:
--------------
- **Use Case Driven**: Each class represents a specific business operation
- **Technology Agnostic**: No knowledge of UI, database, or external APIs
- **Orchestration**: Coordinates domain entities and adapters to fulfill use cases
- **Single Direction Flow**: Data flows from outer layers inward to domain

Benefits:
---------
- **Clear Business Intent**: Each use case explicitly defines what the application does
- **Testability**: Use cases can be tested with mock adapters
- **Separation of Concerns**: Business flow is separate from technical implementation
- **Flexibility**: Can support multiple UIs (web, CLI, API) with same use cases

Dependencies:
-------------
- Depends on: Domain layer (model/)
- Depended upon by: Infrastructure layer (composition/)
- Uses: Adapter protocols (not implementations)
"""
