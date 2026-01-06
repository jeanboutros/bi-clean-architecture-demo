"""\nApplication Context and Configuration\n\nThis module provides configuration management and dynamic class loading for dependency\ninjection. It demonstrates Clean Architecture's flexibility by allowing different\nimplementations to be wired based on configuration.\n\nKey Concepts:\n-------------\n1. **ClassImportPath**: String-based dynamic class loading\n2. **Context**: Configuration container specifying which implementations to use\n3. **Environment-Specific Configuration**: Different contexts for dev, test, production\n\nBenefits:\n---------\n- **Flexibility**: Change implementations without code changes\n- **Testability**: Different contexts for testing vs. production\n- **Deployment**: Environment-specific configurations\n- **Experimentation**: Easy to A/B test different implementations\n\"\""\n\nfrom typing import NamedTuple\nimport importlib\n\n\nclass ClassImportPath(NamedTuple):\n    \"\"\"\n    String-based class import specification enabling dynamic dependency loading.\n    \n    This class enables the dependency injection pattern by allowing dependencies to be\n    specified as strings (module path + class name) rather than direct imports. This\n    provides several key benefits:\n    \n    Benefits:\n    ---------\n    1. **Configuration-Driven**: Change implementations via configuration files\n    2. **Lazy Loading**: Import classes only when needed\n    3. **Circular Import Prevention**: Break circular dependencies\n    4. **Plugin Architecture**: Load implementations discovered at runtime\n    5. **Environment-Specific Loading**: Different classes for dev/test/prod\n    \n    Why Not Direct Imports:\n    -----------------------\n    Direct imports create tight coupling:\n        from example_project.interface.graphql_service import GraphQLService\n        \n    With ClassImportPath, we can change implementations via configuration:\n        frames_class = ClassImportPath.from_string(\"example_project.interface.graphql_service.GraphQLService\")\n        # Change to: \"example_project.interface.frame_service.FrameService\"\n    \n    This allows switching implementations without code changes, supporting:\n    - A/B testing different implementations\n    - Environment-specific implementations\n    - Feature flags\n    - Plugin systems\n    \n    Attributes:\n        module_name: Python module path (e.g., 'example_project.interface.graphql_service')\n        class_name: Class name within the module (e.g., 'GraphQLService')\n    \n    Example Usage:\n    --------------\n    >>> path = ClassImportPath.from_string(\"example_project.interface.graphql_service.GraphQLService\")\n    >>> service_class = path.import_class()  # Returns GraphQLService class\n    >>> service_instance = service_class()  # Create instance\n    >>> # Or use __call__ shorthand:\n    >>> service_class = path()  # Same as import_class()\n    \"\"\"

    module_name: str
    class_name: str

    def __str__(self):
        return f"{self.module_name}.{self.class_name}"

    @classmethod\n    def from_string(cls, fully_qualified_module_name: str):\n        \"\"\"\n        Parse fully qualified class name into ClassImportPath.\n        \n        Splits string like \"module.path.ClassName\" into module_name and class_name.\n        \n        Parameters:\n            fully_qualified_module_name: Dot-separated module path with class name\n        \n        Returns:\n            ClassImportPath: Parsed import path specification\n        \n        Example:\n            >>> ClassImportPath.from_string(\"example_project.interface.graphql_service.GraphQLService\")\n            ClassImportPath(module_name='example_project.interface.graphql_service', class_name='GraphQLService')\n        \"\"\"
        last_dot = fully_qualified_module_name.rfind(".")

        if last_dot == -1:
            return cls(module_name=".", class_name=fully_qualified_module_name)

        else:
            return cls(
                module_name=fully_qualified_module_name[:last_dot],
                class_name=fully_qualified_module_name[last_dot + 1 :],
            )

    def import_class(self):\n        \"\"\"\n        Dynamically import and return the class.\n        \n        Uses importlib to import the module and getattr to retrieve the class.\n        \n        Returns:\n            type: The imported class (not an instance)\n        \n        Raises:\n            ModuleNotFoundError: If module doesn't exist\n            AttributeError: If class doesn't exist in module\n        \"\"\"
        module = importlib.import_module(self.module_name)

        return getattr(module, self.class_name)

    def __call__(self):\n        \"\"\"Convenience method to call import_class().\"\"\"
        return self.import_class()


class Context(NamedTuple):
    """
    Application configuration container specifying dependency implementations.
    
    Context is the heart of dependency injection in this application. It specifies
    which concrete implementations to use for each protocol, enabling the application
    to run with different configurations for different environments.
    
    Configuration Pattern:
    ----------------------
    Rather than hard-coding implementations throughout the application, all dependency
    decisions are centralised in Context. The composition layer reads the Context and
    wires dependencies accordingly.
    
    Benefits:
    ---------
    1. **Environment-Specific Configuration**: Different implementations for dev/test/prod
    2. **A/B Testing**: Multiple contexts for comparing implementations
    3. **Feature Flags**: Enable/disable features via context
    4. **Testability**: Test contexts with mock implementations
    5. **Documentation**: Context serves as documentation of all dependencies
    
    Context Methods:
    ----------------
    - default(): Standard configuration for local development
    - notebook_default(): Configuration for Databricks notebooks
    - test(): Configuration with test doubles (could be added)
    - production(): Configuration for production environment (could be added)
    
    Clean Architecture Benefit:
    ---------------------------
    Context enables the Dependency Inversion Principle. Instead of:
        use_case = DownloadAndStore(GraphQLService(), AsIsParser(), StorageService())
    
    We have:
        context = Context.default()
        # Composition layer wires dependencies based on context
    
    This allows changing implementations without modifying use case instantiation code.
    
    Attributes:
    -----------
    environment : str
        Environment identifier (e.g., 'dev', 'staging', 'prod')
    project_package_name : str
        Base package name for the project
    frames_class : ClassImportPath
        API client implementation to use
    frames_parser_class : ClassImportPath
        Parser implementation to use
    storage_class : ClassImportPath
        Storage backend implementation to use
    
    Example Usage:
    --------------
    >>> context = Context.default()
    >>> print(context.environment)  # 'dev'
    >>> api_class = context.frames_class.import_class()  # Get GraphQLService class
    """
    environment: str
    project_package_name: str
    
    frames_class: ClassImportPath
    frames_parser_class: ClassImportPath
    storage_class: ClassImportPath

    def __str__(self):
        return (
            f"Context("
            f"environment={self.environment}, "
            f"project_package_name={self.project_package_name}, "
            f"frames_class={self.frames_class}, "
            f"frames_parser_class={self.frames_parser_class}, "
            f"storage_class={self.storage_class}"
            f"base_catalog_name={self.base_catalog_name}"
            ")"
        )

    @property
    def base_catalog_name(self):
        """Construct base catalog name from environment."""
        return f"{self.environment}_catalog_base"

    @classmethod
    def default(cls):
        """
        Create default context for local development.
        
        This configuration uses:
        - GraphQLService for API calls
        - AsIsParser for pass-through parsing
        - StorageService for local filesystem storage
        
        Returns:
            Context: Configuration for local development environment
        """
        return cls(
            environment="dev",
            project_package_name="example_project",
            frames_class=ClassImportPath.from_string(
                # "example_project.interface.frame_service.FrameService"
                "example_project.interface.graphql_service.GraphQLService"
            ),
            frames_parser_class=ClassImportPath.from_string(
                "example_project.parser.AsIsParser"
            ),
            storage_class=ClassImportPath.from_string(
                # "example_project.storage.UnityCatalogVolumeStorageService"
                "example_project.storage.StorageService"

            ),
        )
    
    @classmethod
    def notebook_default(cls):
        """
        Create context for Databricks notebook environment.
        
        This configuration is optimised for running in Databricks notebooks.
        Currently uses same implementations as default(), but provides flexibility
        to use notebook-specific implementations (e.g., Unity Catalog storage).
        
        Returns:
            Context: Configuration for Databricks notebook environment
        """
        return cls(
            environment="dev",
            project_package_name="example_project",
            frames_class=ClassImportPath.from_string(
                # "example_project.interface.frame_service.FrameService"
                "example_project.interface.graphql_service.GraphQLService"
            ),
            frames_parser_class=ClassImportPath.from_string(
                "example_project.parser.AsIsParser"
            ),
            storage_class=ClassImportPath.from_string(
                # "example_project.storage.UnityCatalogVolumeStorageService"
                "example_project.storage.StorageService"

            ),
        )