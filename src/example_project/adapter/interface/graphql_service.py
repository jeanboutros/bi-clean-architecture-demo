"""
GraphQL API Client Implementation

This module provides a GraphQL API client that implements the ApiClass protocol,
demonstrating how different API technologies can be unified behind a common interface.
"""

from typing import Any
from example_project.adapter.protocols import ApiClass


class GraphQLService(ApiClass):
    """
    GraphQL API client for downloading frame data.
    
    This implementation demonstrates the power of the Adapter pattern and Clean Architecture.
    Despite GraphQL and REST having different paradigms (queries vs. endpoints), both
    implement the same ApiClass protocol. This allows:
    
    Benefits:
    ---------
    1. **Interchangeability**: Swap between FrameService and GraphQLService via configuration
    2. **Technology Freedom**: Choose best API technology without affecting business logic
    3. **Gradual Migration**: Migrate from REST to GraphQL incrementally
    4. **Polyglot APIs**: Support multiple API types in same application
    
    Clean Architecture Benefit:
    --------------------------
    The application layer (DownloadAndStore use case) doesn't know whether it's using
    REST or GraphQL. It only knows the ApiClass protocol. This means:
    - Business logic is stable regardless of API changes
    - Can switch API implementations without touching use cases
    - Each API implementation can evolve independently
    
    Current Implementation:
    -----------------------
    This is a stub returning mock data. Production implementation would:
    - Execute GraphQL queries
    - Handle authentication (JWT, API keys)
    - Manage query complexity and batching
    - Handle GraphQL-specific errors
    
    Example Usage:
    --------------
    >>> client = GraphQLService()
    >>> data = client.download()  # Returns mock GraphQL response
    """
    
    def __init__(self):
        super().__init__()
        
    def download(self) -> Any:
        """
        Execute GraphQL query and return frame data.
        
        In production, this would execute actual GraphQL queries. Currently returns
        mock data for demonstration purposes.
        
        Returns:
            dict: GraphQL response with payload containing frame data
        """
        print("GraphQLService.get() has been called")
        return {
            "payload": [
                {
                    "id": 10,
                    "name": "frame1",
                    "location": "London, UK"
                },
                {
                    "id": 12,
                    "name": "frame2",
                    "location": "London, UK"
                },
                {
                    "id": 13,
                    "name": "frame3",
                    "location": "London, UK"
                },
                {
                    "id": 14,
                    "name": "frame4",
                    "location": "London, UK"
                }
            ]
        }