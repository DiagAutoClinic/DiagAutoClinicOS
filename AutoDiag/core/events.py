"""
Unified Event System for AutoDiag Pro
Provides a centralized event management system for loose coupling between components
"""

import logging
import threading
from typing import Dict, List, Callable, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import weakref

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event type enumeration"""
    # UI Events
    UI_INITIALIZED = "ui.initialized"
    UI_THEME_CHANGED = "ui.theme_changed"
    UI_BRAND_CHANGED = "ui.brand_changed"
    UI_TAB_SWITCHED = "ui.tab_switched"
    UI_WINDOW_RESIZED = "ui.window_resized"
    
    # Diagnostic Events
    DIAGNOSTICS_STARTED = "diagnostics.started"
    DIAGNOSTICS_COMPLETED = "diagnostics.completed"
    DIAGNOSTICS_ERROR = "diagnostics.error"
    DTC_READ = "diagnostics.dtc_read"
    DTC_CLEARED = "diagnostics.dtc_cleared"
    LIVE_DATA_STARTED = "diagnostics.live_data_started"
    LIVE_DATA_STOPPED = "diagnostics.live_data_stopped"
    LIVE_DATA_UPDATED = "diagnostics.live_data_updated"
    QUICK_SCAN_STARTED = "diagnostics.quick_scan_started"
    QUICK_SCAN_COMPLETED = "diagnostics.quick_scan_completed"
    ECU_INFO_RETRIEVED = "diagnostics.ecu_info_retrieved"
    
    # Special Functions Events
    SPECIAL_FUNCTION_STARTED = "special_function.started"
    SPECIAL_FUNCTION_COMPLETED = "special_function.completed"
    SPECIAL_FUNCTION_ERROR = "special_function.error"
    
    # Calibration Events
    CALIBRATION_STARTED = "calibration.started"
    CALIBRATION_COMPLETED = "calibration.completed"
    CALIBRATION_ERROR = "calibration.error"
    
    # Advanced Functions Events
    ADVANCED_FUNCTION_STARTED = "advanced_function.started"
    ADVANCED_FUNCTION_COMPLETED = "advanced_function.completed"
    ADVANCED_FUNCTION_ERROR = "advanced_function.error"
    
    # System Events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    SYSTEM_INFO = "system.info"
    
    # Connection Events
    DEVICE_CONNECTED = "connection.device_connected"
    DEVICE_DISCONNECTED = "connection.device_disconnected"
    PROTOCOL_NEGOTIATED = "connection.protocol_negotiated"
    CONNECTION_ERROR = "connection.error"


@dataclass
class Event:
    """Event data structure"""
    event_type: EventType
    source: str
    data: Dict[str, Any]
    timestamp: datetime
    thread_id: int
    event_id: str = None
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = f"{self.event_type.value}_{self.timestamp.strftime('%Y%m%d_%H%M%S_%f')}"
    
    @classmethod
    def create(cls, event_type: EventType, source: str, data: Dict[str, Any] = None) -> 'Event':
        """Create a new event"""
        return cls(
            event_type=event_type,
            source=source,
            data=data or {},
            timestamp=datetime.now(),
            thread_id=threading.get_ident()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            'event_type': self.event_type.value,
            'source': self.source,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'thread_id': self.thread_id,
            'event_id': self.event_id
        }


class EventSubscriber:
    """Represents an event subscriber"""
    
    def __init__(self, callback: Callable[[Event], None], 
                 event_types: Set[EventType] = None, 
                 source_filter: str = None,
                 priority: int = 0):
        """Initialize event subscriber"""
        self.callback = callback
        self.event_types = event_types or set()
        self.source_filter = source_filter
        self.priority = priority
        self.is_active = True
        self.subscriber_id = f"subscriber_{id(self)}"
    
    def should_handle_event(self, event: Event) -> bool:
        """Check if this subscriber should handle the event"""
        if not self.is_active:
            return False
        
        # Check event type
        if self.event_types and event.event_type not in self.event_types:
            return False
        
        # Check source filter
        if self.source_filter and event.source != self.source_filter:
            return False
        
        return True


class EventManager:
    """Central event management system"""
    
    def __init__(self):
        """Initialize event manager"""
        self._subscribers: Dict[str, List[EventSubscriber]] = {}
        self._event_history: List[Event] = []
        self._max_history_size = 1000
        self._lock = threading.RLock()
        self._event_counter = 0
        self._is_shutdown = False
        
        logger.info("Event manager initialized")
    
    def subscribe(self, callback: Callable[[Event], None], 
                  event_types: List[EventType] = None,
                  source_filter: str = None,
                  priority: int = 0) -> str:
        """Subscribe to events"""
        with self._lock:
            event_types_set = set(event_types) if event_types else set()
            subscriber = EventSubscriber(callback, event_types_set, source_filter, priority)
            
            # Store subscriber
            self._subscribers[subscriber.subscriber_id] = [subscriber]
            
            logger.debug(f"Subscribed callback to events: {[et.value for et in event_types_set]}")
            return subscriber.subscriber_id
    
    def unsubscribe(self, subscriber_id: str) -> bool:
        """Unsubscribe from events"""
        with self._lock:
            if subscriber_id in self._subscribers:
                del self._subscribers[subscriber_id]
                logger.debug(f"Unsubscribed: {subscriber_id}")
                return True
            return False
    
    def subscribe_to_type(self, event_type: EventType, 
                         callback: Callable[[Event], None],
                         source_filter: str = None,
                         priority: int = 0) -> str:
        """Subscribe to a specific event type"""
        return self.subscribe(callback, [event_type], source_filter, priority)
    
    def subscribe_to_source(self, source: str,
                           callback: Callable[[Event], None],
                           priority: int = 0) -> str:
        """Subscribe to all events from a specific source"""
        return self.subscribe(callback, None, source, priority)
    
    def emit(self, event: Event) -> int:
        """Emit an event to all subscribers"""
        with self._lock:
            if self._is_shutdown:
                logger.warning("Cannot emit event: event manager is shutdown")
                return 0
            
            # Add to history
            self._add_to_history(event)
            
            # Find matching subscribers
            subscribers = []
            for sub_list in self._subscribers.values():
                for subscriber in sub_list:
                    if subscriber.should_handle_event(event):
                        subscribers.append(subscriber)
            
            # Sort by priority (higher priority first)
            subscribers.sort(key=lambda s: s.priority, reverse=True)
            
            # Deliver to subscribers
            delivered_count = 0
            for subscriber in subscribers:
                try:
                    subscriber.callback(event)
                    delivered_count += 1
                except Exception as e:
                    logger.error(f"Error delivering event to subscriber {subscriber.subscriber_id}: {e}")
            
            logger.debug(f"Event {event.event_type.value} delivered to {delivered_count} subscribers")
            return delivered_count
    
    def emit_event(self, event_type: EventType, source: str, 
                  data: Dict[str, Any] = None) -> Event:
        """Create and emit an event"""
        event = Event.create(event_type, source, data)
        self.emit(event)
        return event
    
    def emit_ui_event(self, event_type: EventType, data: Dict[str, Any] = None) -> Event:
        """Emit a UI event"""
        return self.emit_event(event_type, "ui", data)
    
    def emit_diagnostic_event(self, event_type: EventType, data: Dict[str, Any] = None) -> Event:
        """Emit a diagnostic event"""
        return self.emit_event(event_type, "diagnostics", data)
    
    def emit_system_event(self, event_type: EventType, data: Dict[str, Any] = None) -> Event:
        """Emit a system event"""
        return self.emit_event(event_type, "system", data)
    
    def emit_connection_event(self, event_type: EventType, data: Dict[str, Any] = None) -> Event:
        """Emit a connection event"""
        return self.emit_event(event_type, "connection", data)
    
    def _add_to_history(self, event: Event):
        """Add event to history"""
        self._event_history.append(event)
        
        # Trim history if too large
        if len(self._event_history) > self._max_history_size:
            self._event_history = self._event_history[-self._max_history_size:]
    
    def get_event_history(self, event_type: EventType = None, 
                         source: str = None,
                         limit: int = 100) -> List[Event]:
        """Get event history with optional filtering"""
        with self._lock:
            events = self._event_history
            
            # Filter by event type
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            
            # Filter by source
            if source:
                events = [e for e in events if e.source == source]
            
            # Return last 'limit' events
            return events[-limit:] if limit > 0 else events
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get event manager statistics"""
        with self._lock:
            # Count events by type
            event_type_counts = {}
            for event in self._event_history:
                event_type_counts[event.event_type.value] = \
                    event_type_counts.get(event.event_type.value, 0) + 1
            
            return {
                'total_subscribers': sum(len(subs) for subs in self._subscribers.values()),
                'total_events': len(self._event_history),
                'event_types': list(event_type_counts.keys()),
                'event_type_counts': event_type_counts,
                'is_shutdown': self._is_shutdown
            }
    
    def clear_history(self):
        """Clear event history"""
        with self._lock:
            self._event_history.clear()
            logger.info("Event history cleared")
    
    def shutdown(self):
        """Shutdown event manager"""
        with self._lock:
            self._is_shutdown = True
            self._subscribers.clear()
            logger.info("Event manager shutdown")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown()


# Global event manager instance
_global_event_manager: Optional[EventManager] = None


def get_event_manager() -> EventManager:
    """Get global event manager instance"""
    global _global_event_manager
    if _global_event_manager is None:
        _global_event_manager = EventManager()
    return _global_event_manager


def emit_event(event_type: EventType, source: str, data: Dict[str, Any] = None) -> Event:
    """Convenience function to emit events"""
    return get_event_manager().emit_event(event_type, source, data)


def subscribe_to_events(callback: Callable[[Event], None], 
                       event_types: List[EventType] = None,
                       source_filter: str = None) -> str:
    """Convenience function to subscribe to events"""
    return get_event_manager().subscribe(callback, event_types, source_filter)


# Event helper functions
def create_diagnostic_start_event(operation: str, brand: str = None) -> Event:
    """Create diagnostic start event"""
    data = {'operation': operation}
    if brand:
        data['brand'] = brand
    return Event.create(EventType.DIAGNOSTICS_STARTED, 'diagnostics', data)


def create_diagnostic_complete_event(operation: str, result: Dict[str, Any]) -> Event:
    """Create diagnostic complete event"""
    data = {
        'operation': operation,
        'result': result,
        'success': result.get('status') != 'error'
    }
    return Event.create(EventType.DIAGNOSTICS_COMPLETED, 'diagnostics', data)


def create_error_event(source: str, error_message: str, 
                      error_type: str = "general", context: Dict[str, Any] = None) -> Event:
    """Create error event"""
    data = {
        'error_message': error_message,
        'error_type': error_type,
        'context': context or {}
    }
    
    # Choose appropriate event type based on source
    event_type_map = {
        'diagnostics': EventType.DIAGNOSTICS_ERROR,
        'special_function': EventType.SPECIAL_FUNCTION_ERROR,
        'calibration': EventType.CALIBRATION_ERROR,
        'advanced_function': EventType.ADVANCED_FUNCTION_ERROR,
        'connection': EventType.CONNECTION_ERROR,
        'system': EventType.SYSTEM_ERROR
    }
    
    event_type = event_type_map.get(source, EventType.SYSTEM_ERROR)
    return Event.create(event_type, source, data)


def create_status_event(message: str, level: str = "info", source: str = "system") -> Event:
    """Create status event"""
    event_type_map = {
        'info': EventType.SYSTEM_INFO,
        'warning': EventType.SYSTEM_WARNING,
        'error': EventType.SYSTEM_ERROR
    }
    
    event_type = event_type_map.get(level.lower(), EventType.SYSTEM_INFO)
    data = {'message': message, 'level': level}
    return Event.create(event_type, source, data)