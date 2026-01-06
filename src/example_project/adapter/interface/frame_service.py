"""
REST-style API Client Implementation

This module provides a REST-style API client that implements the ApiClass protocol.
It demonstrates how external API clients adapt to the application's protocol interface.
"""

from typing import Any
from example_project.adapter.protocols import ApiClass


class FrameService(ApiClass):
    """
    REST-style API client for downloading frame data.

    This implementation demonstrates the Adapter pattern by wrapping a REST API
    and presenting it through the ApiClass protocol interface. This allows the
    application to interact with the API through a consistent interface regardless
    of the underlying protocol.

    Adapter Pattern Benefits:
    -------------------------
    1. **Isolation**: API changes only affect this class
    2. **Consistency**: Presents same interface as other API implementations
    3. **Substitutability**: Can swap with GraphQLService without code changes
    4. **Testing**: Easy to replace with mock for testing

    Current Implementation:
    -----------------------
    This is a stub implementation returning mock data. In production, this would:
    - Make HTTP requests to actual REST API
    - Handle authentication and headers
    - Process pagination
    - Handle errors and retries

    Example Usage:
    --------------
    >>> client = FrameService()
    >>> data = client.download()  # Returns mock frame data
    """

    def __init__(self):
        super().__init__()

    def download(self) -> Any:
        """
        Download frame data from REST API.

        In production, this would make actual HTTP requests. Currently returns
        mock data for demonstration purposes.

        Returns:
            dict: Frame data with pagination metadata and data array
        """
        print("FrameService.get() has been called")
        return {
            "start": 0,
            "offset": 0,
            "limit": 500,
            "data": [
                {"id": 1, "name": "frame1"},
                {"id": 2, "name": "frame2"},
                {"id": 3, "name": "frame3"},
            ],
        }
