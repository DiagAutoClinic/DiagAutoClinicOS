"""
Dependency Injection Container for AutoDiag Pro
Provides centralized service management and dependency injection
"""

import logging
import threading
from typing import Dict, Any, Optional, Callable, Type, TypeVar, Union, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
import inspect

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class ServiceRegistration:
    """Service registration information"""
    service_type: Type
    implementation: Any
    singleton: bool = True
    factory: Optional[Callable] = None
    args: tuple = ()
    kwargs: Dict[str, Any] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.tags is None:
            self.tags = []
    
    def create_instance(self) -> Any:
        """Create service instance"""
        if self.factory:
            return self.factory(*self.args, **self.kwargs)
        elif inspect.isclass(self.implementation):
            return self.implementation(*self.args, **self.kwargs)
        else:
            return self.implementation


class DIContainer:
    """Dependency Injection Container"""
    
    def __init__(self):
        """Initialize DI container"""
        self._services: Dict[str, ServiceRegistration] = {}
        self._singletons: Dict[str, Any] = {}
        self._lock = threading.RLock()
        logger.info("DI container initialized")
    
    def register(self, service_type: Type[T], 
                implementation: Union[T, Callable[[], T]], 
                singleton: bool = True,
                tags: List[str] = None,
                **kwargs) -> None:
        """Register a service"""
        with self._lock:
            # Generate service key
            if isinstance(service_type, type):
                key = f"{service_type.__module__}.{service_type.__name__}"
            else:
                key = str(service_type)
            
            # Create registration
            registration = ServiceRegistration(
                service_type=service_type,
                implementation=implementation,
                singleton=singleton,
                kwargs=kwargs
            )
            
            self._services[key] = registration
            logger.debug(f"Registered service: {key}")
    
    def register_singleton(self, service_type: Type[T], 
                          implementation: Union[T, Callable[[], T]], 
                          tags: List[str] = None,
                          **kwargs) -> None:
        """Register a singleton service"""
        self.register(service_type, implementation, singleton=True, tags=tags, **kwargs)
    
    def register_transient(self, service_type: Type[T],
                          implementation: Union[T, Callable[[], T]],
                          tags: List[str] = None,
                          **kwargs) -> None:
        """Register a transient service (new instance each time)"""
        self.register(service_type, implementation, singleton=False, tags=tags, **kwargs)
    
    def register_factory(self, service_type: Type[T],
                        factory: Callable[[], T],
                        singleton: bool = True,
                        tags: List[str] = None,
                        **kwargs) -> None:
        """Register a factory function"""
        with self._lock:
            key = f"{service_type.__module__}.{service_type.__name__}"
            
            registration = ServiceRegistration(
                service_type=service_type,
                implementation=factory,  # Use factory as implementation
                singleton=singleton,
                factory=factory,
                kwargs=kwargs
            )
            
            self._services[key] = registration
            logger.debug(f"Registered factory for service: {key}")
    
    def get(self, service_type: Type[T]) -> T:
        """Get service instance"""
        with self._lock:
            # Generate service key
            if isinstance(service_type, type):
                key = f"{service_type.__module__}.{service_type.__name__}"
            else:
                key = str(service_type)
            
            # Check if service is registered
            if key not in self._services:
                raise ValueError(f"Service not registered: {service_type}")
            
            registration = self._services[key]
            
            # Return existing singleton or create new instance
            if registration.singleton:
                if key not in self._singletons:
                    self._singletons[key] = registration.create_instance()
                return self._singletons[key]
            else:
                return registration.create_instance()
    
    def get_optional(self, service_type: Type[T]) -> Optional[T]:
        """Get service instance if registered, None otherwise"""
        try:
            return self.get(service_type)
        except ValueError:
            return None
    
    def get_all_with_tag(self, tag: str) -> List[Any]:
        """Get all services with a specific tag"""
        with self._lock:
            services = []
            for registration in self._services.values():
                if tag in registration.tags:
                    services.append(self.get(registration.service_type))
            return services
    
    def has_service(self, service_type: Type[T]) -> bool:
        """Check if service is registered"""
        with self._lock:
            if isinstance(service_type, type):
                key = f"{service_type.__module__}.{service_type.__name__}"
            else:
                key = str(service_type)
            return key in self._services
    
    def unregister(self, service_type: Type[T]) -> bool:
        """Unregister a service"""
        with self._lock:
            if isinstance(service_type, type):
                key = f"{service_type.__module__}.{service_type.__name__}"
            else:
                key = str(service_type)
            
            if key in self._services:
                # Remove from singletons if exists
                if key in self._singletons:
                    del self._singletons[key]
                
                # Remove service registration
                del self._services[key]
                logger.debug(f"Unregistered service: {key}")
                return True
            
            return False
    
    def clear(self):
        """Clear all services"""
        with self._lock:
            self._services.clear()
            self._singletons.clear()
            logger.info("DI container cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get container statistics"""
        with self._lock:
            singleton_count = len(self._singletons)
            total_registrations = len(self._services)
            
            # Count services by type
            service_types = []
            for registration in self._services.values():
                if hasattr(registration.service_type, '__name__'):
                    service_types.append(registration.service_type.__name__)
                else:
                    service_types.append(str(registration.service_type))
            
            return {
                'total_services': total_registrations,
                'active_singletons': singleton_count,
                'service_types': list(set(service_types)),
                'singleton_ratio': singleton_count / max(total_registrations, 1)
            }
    
    def __contains__(self, service_type: Type[T]) -> bool:
        """Check if service is registered"""
        return self.has_service(service_type)
    
    def __getitem__(self, service_type: Type[T]) -> T:
        """Get service using square bracket notation"""
        return self.get(service_type)


# Global DI container instance
_global_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """Get global DI container instance"""
    global _global_container
    if _global_container is None:
        _global_container = DIContainer()
    return _global_container


def register_service(service_type: Type[T], 
                    implementation: Union[T, Callable[[], T]], 
                    singleton: bool = True,
                    **kwargs) -> None:
    """Convenience function to register a service"""
    get_container().register(service_type, implementation, singleton, **kwargs)


def get_service(service_type: Type[T]) -> T:
    """Convenience function to get a service"""
    return get_container().get(service_type)


def has_service(service_type: Type[T]) -> bool:
    """Convenience function to check if service is registered"""
    return get_container().has_service(service_type)


# Auto-registration decorator
def auto_register(singleton: bool = True, tags: List[str] = None):
    """Decorator for automatic service registration"""
    def decorator(cls: Type[T]) -> Type[T]:
        def register():
            register_service(cls, cls, singleton=singleton, tags=tags)
            return cls()
        
        # Register on module import
        register_service(cls, cls, singleton=singleton, tags=tags)
        
        return cls
    return decorator


# Module initializer for AutoDiag
class AutoDiagModuleInitializer:
    """Initializes AutoDiag Pro services in the DI container"""
    
    def __init__(self, container: DIContainer = None):
        """Initialize with DI container"""
        self.container = container or get_container()
        self._initialized = False
    
    def initialize_all(self):
        """Initialize all AutoDiag services"""
        if self._initialized:
            logger.warning("Services already initialized")
            return
        
        try:
            self._register_core_services()
            self._register_ui_services()
            self._register_diagnostic_services()
            self._register_utility_services()
            
            self._initialized = True
            logger.info("AutoDiag services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise
    
    def _register_core_services(self):
        """Register core services"""
        from .events import EventManager
        
        # Event Manager
        self.container.register_singleton(EventManager, EventManager())
        
        # UI Strategy Manager
        from ..ui.ui_strategy import UIManager
        self.container.register_singleton(UIManager, UIManager())
    
    def _register_ui_services(self):
        """Register UI services"""
        # These would be registered when the UI components are created
        logger.debug("UI services registration deferred to runtime")
    
    def _register_diagnostic_services(self):
        """Register diagnostic services"""
        from .diagnostics import DiagnosticsController
        
        # Diagnostics Controller
        self.container.register_transient(DiagnosticsController, DiagnosticsController)
    
    def _register_utility_services(self):
        """Register utility services"""
        # Configuration Manager (will be implemented)
        # Logger Manager (will be implemented)
        # Theme Manager (will be implemented)
        logger.debug("Utility services registration deferred")
    
    def reinitialize(self):
        """Reinitialize all services"""
        logger.info("Reinitializing AutoDiag services")
        self.container.clear()
        self._initialized = False
        self.initialize_all()


# Global initializer
_global_initializer: Optional[AutoDiagModuleInitializer] = None


def initialize_autodiag_services(container: DIContainer = None) -> AutoDiagModuleInitializer:
    """Initialize AutoDiag services"""
    global _global_initializer
    _global_initializer = AutoDiagModuleInitializer(container)
    _global_initializer.initialize_all()
    return _global_initializer


# Service locator pattern for backward compatibility
class ServiceLocator:
    """Service locator for accessing common services"""
    
    def __init__(self, container: DIContainer = None):
        """Initialize service locator"""
        self.container = container or get_container()
    
    @property
    def event_manager(self):
        """Get event manager"""
        from .events import EventManager
        return self.container.get(EventManager)
    
    @property
    def ui_manager(self):
        """Get UI manager"""
        from ..ui.ui_strategy import UIManager
        return self.container.get(UIManager)
    
    @property
    def diagnostics_controller(self):
        """Get diagnostics controller"""
        from .diagnostics import DiagnosticsController
        return self.container.get(DiagnosticsController)
    
    def get_service(self, service_type: Type[T]) -> T:
        """Get service by type"""
        return self.container.get(service_type)


# Global service locator
_global_locator: Optional[ServiceLocator] = None


def get_service_locator() -> ServiceLocator:
    """Get global service locator"""
    global _global_locator
    if _global_locator is None:
        _global_locator = ServiceLocator()
    return _global_locator