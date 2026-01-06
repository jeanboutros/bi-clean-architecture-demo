"""
Composition Layer - Dependency Injection and Application Wiring

This layer represents the outermost circle of Clean Architecture. It's responsible for:
1. Creating concrete implementations of protocols
2. Wiring dependencies together
3. Configuring the application for different environments
4. Providing entry points for orchestration systems

Key Principles:
--------------
- **Dependency Injection**: Creates and injects dependencies into use cases
- **Configuration Management**: Handles environment-specific settings
- **Composition Root**: Single place where all dependencies are wired
- **Isolation**: This layer knows about everything; nothing knows about this layer

Benefits:
---------
- **Flexibility**: Change implementations via configuration
- **Testability**: Easy to create test configurations with mock implementations
- **Environment Management**: Different configurations for dev/staging/production
- **Centralised Wiring**: All dependency decisions in one place

Files:
------
- context.py: Configuration and dependency specifications
- frames.py: Wiring and entry points for frame ingestion use cases

Clean Architecture Context:
---------------------------
The Composition layer is the only layer that depends on all other layers. It imports
concrete implementations and wires them according to configuration. All other layers
only depend on abstractions (protocols).
"""