"""
Domain Layer - Core Business Entities

This layer represents the innermost circle of Clean Architecture and contains the enterprise
business rules and domain models. It has NO dependencies on any other layer.

Key Principles:
--------------
- **Pure Business Logic**: Contains only domain entities and business rules
- **Framework Independent**: No external library dependencies (except dataclasses from stdlib)
- **Stable Foundation**: Changes here should be rare and driven only by business requirement changes
- **Immutability**: Domain entities are immutable to ensure data integrity and predictability

Benefits:
---------
- **Testability**: Pure Python objects with no external dependencies are trivial to test
- **Maintainability**: Business logic is isolated and easy to understand
- **Flexibility**: Can be reused across different applications and contexts
- **Protection from External Changes**: API or database changes cannot affect domain logic

Why Entities Exist:
------------------
APIs return raw dictionaries or raw data structures. Passing those data structures directly 
through the system creates tight coupling between the API response format and core logic. 
Domain entities decouple the internal representation from external data sources, allowing 
the system to evolve independently.

Example:
--------
If the API changes field names from 'id' to 'identifier', only the adapter layer needs to 
change. The domain model remains stable, protecting all business logic from this change.

"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Frame:
    """
    Domain entity representing a Frame in our business model.
    
    This entity is immutable (frozen=True) to ensure data integrity and uses slots=True
    for memory efficiency. It represents the core concept independent of how frames are
    stored, retrieved, or transmitted.
    
    Attributes:
        id: Unique identifier for the frame
        name: Human-readable name of the frame
        location: Optional geographical location information
    """
    id: str
    name: str
    location: str | None
