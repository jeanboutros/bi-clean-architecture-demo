"""\nREST-style API Client Implementation\n\nThis module provides a REST-style API client that implements the ApiClass protocol.\nIt demonstrates how external API clients adapt to the application's protocol interface.\n\"\""\n\nfrom typing import Any\nfrom example_project.adapter.protocols import ApiClass\n\n\nclass FrameService(ApiClass):\n    \"\"\"\n    REST-style API client for downloading frame data.\n    \n    This implementation demonstrates the Adapter pattern by wrapping a REST API\n    and presenting it through the ApiClass protocol interface. This allows the\n    application to interact with the API through a consistent interface regardless\n    of the underlying protocol.\n    \n    Adapter Pattern Benefits:\n    -------------------------\n    1. **Isolation**: API changes only affect this class\n    2. **Consistency**: Presents same interface as other API implementations\n    3. **Substitutability**: Can swap with GraphQLService without code changes\n    4. **Testing**: Easy to replace with mock for testing\n    \n    Current Implementation:\n    -----------------------\n    This is a stub implementation returning mock data. In production, this would:\n    - Make HTTP requests to actual REST API\n    - Handle authentication and headers\n    - Process pagination\n    - Handle errors and retries\n    \n    Example Usage:\n    --------------\n    >>> client = FrameService()\n    >>> data = client.download()  # Returns mock frame data\n    \"\"\"\n    \n    def __init__(self):\n        super().__init__()
        
    def download(self) -> Any:
        """\n        Download frame data from REST API.\n        \n        In production, this would make actual HTTP requests. Currently returns\n        mock data for demonstration purposes.\n        \n        Returns:\n            dict: Frame data with pagination metadata and data array\n        \"\""
        print("FrameService.get() has been called")
        return {
            "start": 0,
            "offset": 0,
            "limit": 500,
            "data": [
                {
                    "id": 1,
                    "name": "frame1"
                },
                {
                    "id": 2,
                    "name": "frame2"
                },
                {
                    "id": 3,
                    "name": "frame3"
                }
            ]
        }