"""
Parser Implementations

Parsers transform raw API data into formats suitable for storage or further processing.
They implement the Parser protocol, enabling different transformation strategies.
"""


class AsIsParser:
    """
    Pass-through parser that returns data unchanged.
    
    This parser implements the Parser protocol with no transformation logic. It's useful
    when the API data format is already suitable for storage, or when transformation
    should happen elsewhere (e.g., in the storage layer or downstream processing).
    
    Benefits:
    ---------
    1. **Performance**: No transformation overhead
    2. **Simplicity**: Maintains raw API data structure
    3. **Debugging**: Easy to inspect original API responses
    4. **Flexibility**: Defer transformation decisions to later stages
    
    When to Use:
    ------------
    - API data format matches storage requirements
    - Want to store raw data for later processing
    - Testing or debugging API responses
    - Prototyping before implementing actual transformation logic
    
    Alternative Parsers (Examples):
    -------------------------------
    - JsonToDomainEntityParser: Map JSON to domain model instances
    - JsonToDataFrameParser: Convert to pandas DataFrame
    - DataCleaningParser: Validate and clean data
    - EnrichmentParser: Add computed fields or external data
    
    Example Usage:
    --------------
    >>> parser = AsIsParser()
    >>> raw_data = {"id": 1, "name": "frame1"}
    >>> parsed = parser.parse(raw_data)
    >>> assert parsed == raw_data  # No transformation
    """
    
    def parse(self, s: Any):
        """
        Return input data unchanged.
        
        Parameters:
            s: Data in any format from API
        
        Returns:
            Same data structure as input
        """
        return s