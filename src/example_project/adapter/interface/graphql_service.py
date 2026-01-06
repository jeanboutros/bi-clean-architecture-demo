"""\nGraphQL API Client Implementation\n\nThis module provides a GraphQL API client that implements the ApiClass protocol,\ndemonstrating how different API technologies can be unified behind a common interface.\n\"\""\n\nfrom typing import Any\nfrom example_project.adapter.protocols import ApiClass\n\n\nclass GraphQLService(ApiClass):\n    \"\"\"\n    GraphQL API client for downloading frame data.\n    \n    This implementation demonstrates the power of the Adapter pattern and Clean Architecture.\n    Despite GraphQL and REST having different paradigms (queries vs. endpoints), both\n    implement the same ApiClass protocol. This allows:\n    \n    Benefits:\n    ---------\n    1. **Interchangeability**: Swap between FrameService and GraphQLService via configuration\n    2. **Technology Freedom**: Choose best API technology without affecting business logic\n    3. **Gradual Migration**: Migrate from REST to GraphQL incrementally\n    4. **Polyglot APIs**: Support multiple API types in same application\n    \n    Clean Architecture Benefit:\n    --------------------------\n    The application layer (DownloadAndStore use case) doesn't know whether it's using\n    REST or GraphQL. It only knows the ApiClass protocol. This means:\n    - Business logic is stable regardless of API changes\n    - Can switch API implementations without touching use cases\n    - Each API implementation can evolve independently\n    \n    Current Implementation:\n    -----------------------\n    This is a stub returning mock data. Production implementation would:\n    - Execute GraphQL queries\n    - Handle authentication (JWT, API keys)\n    - Manage query complexity and batching\n    - Handle GraphQL-specific errors\n    \n    Example Usage:\n    --------------\n    >>> client = GraphQLService()\n    >>> data = client.download()  # Returns mock GraphQL response\n    \"\"\"\n    \n    def __init__(self):\n        super().__init__()
        
    def download(self) -> Any:
        """\n        Execute GraphQL query and return frame data.\n        \n        In production, this would execute actual GraphQL queries. Currently returns\n        mock data for demonstration purposes.\n        \n        Returns:\n            dict: GraphQL response with payload containing frame data\n        \"\""
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