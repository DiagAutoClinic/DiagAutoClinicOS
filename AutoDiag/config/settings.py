"""
Configuration Management System for AutoDiag Pro
Provides centralized configuration handling with persistence and validation
"""

import logging
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Type, TypeVar
from dataclasses import dataclass, field, asdict
from enum import Enum
import threading
from datetime import datetime

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ConfigScope(Enum):
    """Configuration scope enumeration"""
    SYSTEM = "system"  # System-wide settings
    USER = "user"      # User-specific settings
    SESSION = "session"  # Session-specific settings


class ConfigFormat(Enum):
    """Configuration file format enumeration"""
    JSON = "json"
    YAML = "yaml"  # Future support
    INI = "ini"    # Future support


@dataclass
class ConfigEntry:
    """Configuration entry with metadata"""
    key: str
    value: Any
    default_value: Any
    description: str = ""
    scope: ConfigScope = ConfigScope.SYSTEM
    requires_restart: bool = False
    validator: Optional[callable] = None
    secret: bool = False  # For sensitive data like passwords
    category: str = "general"
    
    def __post_init__(self):
        """Validate configuration entry after initialization"""
        if self.validator and not self.validator(self.value):
            logger.warning(f"Configuration validation failed for {self.key}: {self.value}")


class ConfigurationManager:
    """Centralized configuration management"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager"""
        self._config_dir = config_dir or self._get_default_config_dir()
        self._config_dir.mkdir(parents=True, exist_ok=True)
        
        self._configurations: Dict[str, ConfigEntry] = {}
        self._file_locks: Dict[str, threading.Lock] = {}
        self._lock = threading.RLock()
        
        # Initialize default configurations
        self._initialize_defaults()
        
        # Load configurations from files
        self._load_all_configurations()
        
        logger.info(f"Configuration manager initialized with dir: {self._config_dir}")
    
    def _get_default_config_dir(self) -> Path:
        """Get default configuration directory"""
        home_dir = Path.home()
        config_dir = home_dir / ".autodiag" / "config"
        return config_dir
    
    def _initialize_defaults(self):
        """Initialize default configurations"""
        # UI Configuration
        self.register_config(
            key="ui.window_width",
            default_value=1366,
            description="Main window width",
            category="ui"
        )
        
        self.register_config(
            key="ui.window_height",
            default_value=768,
            description="Main window height",
            category="ui"
        )
        
        self.register_config(
            key="ui.window_minimized",
            default_value=False,
            description="Start minimized",
            category="ui"
        )
        
        self.register_config(
            key="ui.theme",
            default_value="dacos_cyber_teal",
            description="UI theme",
            category="ui"
        )
        
        # Diagnostics Configuration
        self.register_config(
            key="diagnostics.update_interval",
            default_value=2000,
            description="Live data update interval in milliseconds",
            category="diagnostics",
            validator=lambda x: x > 0
        )
        
        self.register_config(
            key="diagnostics.max_log_entries",
            default_value=1000,
            description="Maximum log entries to keep",
            category="diagnostics",
            validator=lambda x: x > 0
        )
        
        self.register_config(
            key="diagnostics.auto_scan_on_connect",
            default_value=False,
            description="Automatically run quick scan on device connect",
            category="diagnostics"
        )
        
        # System Configuration
        self.register_config(
            key="system.language",
            default_value="en",
            description="System language",
            category="system"
        )
        
        self.register_config(
            key="system.debug_mode",
            default_value=False,
            description="Enable debug mode",
            category="system"
        )
        
        self.register_config(
            key="system.log_level",
            default_value="INFO",
            description="Logging level",
            category="system",
            validator=lambda x: x in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        )
        
        # Connection Configuration
        self.register_config(
            key="connection.timeout",
            default_value=30,
            description="Connection timeout in seconds",
            category="connection",
            validator=lambda x: x > 0
        )
        
        self.register_config(
            key="connection.auto_reconnect",
            default_value=True,
            description="Auto reconnect on disconnection",
            category="connection"
        )
        
        # User Preferences
        self.register_config(
            key="user.last_brand",
            default_value="Toyota",
            description="Last selected vehicle brand",
            scope=ConfigScope.USER,
            category="user"
        )
        
        self.register_config(
            key="user.confirm_dtc_clear",
            default_value=True,
            description="Show confirmation dialog before clearing DTCs",
            scope=ConfigScope.USER,
            category="user"
        )

        # Tier Configuration
        self.register_config(
            key="user.tier_level",
            default_value=1,  # Free tier by default
            description="User's current tier level (1-5)",
            scope=ConfigScope.USER,
            category="user",
            validator=lambda x: isinstance(x, int) and 1 <= x <= 5
        )

        self.register_config(
            key="tier.enforce_access",
            default_value=True,
            description="Enforce tier-based access control",
            category="tier"
        )

        self.register_config(
            key="tier.show_acknowledgements",
            default_value=True,
            description="Show tier acknowledgement dialogs",
            category="tier"
        )
    
    def register_config(self, key: str, default_value: Any, 
                       description: str = "", scope: ConfigScope = ConfigScope.SYSTEM,
                       requires_restart: bool = False, validator: Optional[callable] = None,
                       secret: bool = False, category: str = "general") -> None:
        """Register a new configuration entry"""
        with self._lock:
            self._configurations[key] = ConfigEntry(
                key=key,
                value=default_value,
                default_value=default_value,
                description=description,
                scope=scope,
                requires_restart=requires_restart,
                validator=validator,
                secret=secret,
                category=category
            )
            
            # Initialize value to default if not already set
            if key not in [c.key for c in self._configurations.values()]:
                self._set_config_value(key, default_value, scope)
            
            logger.debug(f"Registered configuration: {key}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        with self._lock:
            if key not in self._configurations:
                if default is not None:
                    return default
                raise KeyError(f"Configuration key not found: {key}")
            
            config = self._configurations[key]
            return config.value
    
    def get_typed(self, key: str, type_class: Type[T], default: T = None) -> T:
        """Get configuration value with type conversion"""
        value = self.get(key, default)
        if value is None:
            return default
            
        try:
            return type_class(value)
        except (ValueError, TypeError) as e:
            logger.error(f"Type conversion failed for config {key}: {e}")
            return default or type_class()
    
    def set(self, key: str, value: Any, scope: ConfigScope = None) -> bool:
        """Set configuration value"""
        with self._lock:
            if key not in self._configurations:
                logger.warning(f"Setting unregistered configuration: {key}")
                # Auto-register with default scope
                self.register_config(key, value)
            
            config = self._configurations[key]
            
            # Use provided scope or default from config
            if scope is None:
                scope = config.scope
            
            # Validate value if validator exists
            if config.validator and not config.validator(value):
                logger.error(f"Validation failed for config {key}: {value}")
                return False
            
            # Update value
            old_value = config.value
            config.value = value
            
            # Save to file if not session scope
            if scope != ConfigScope.SESSION:
                self._save_configuration(key, scope)
            
            # Log change if not secret
            if not config.secret:
                logger.debug(f"Updated config {key}: {old_value} -> {value}")
            else:
                logger.debug(f"Updated secret config {key}")
            
            return True
    
    def reset_to_default(self, key: str) -> bool:
        """Reset configuration to default value"""
        with self._lock:
            if key not in self._configurations:
                return False
            
            config = self._configurations[key]
            old_value = config.value
            config.value = config.default_value
            
            # Save to file
            if config.scope != ConfigScope.SESSION:
                self._save_configuration(key, config.scope)
            
            logger.info(f"Reset config {key} to default: {old_value} -> {config.default_value}")
            return True
    
    def reset_all_to_defaults(self) -> int:
        """Reset all configurations to defaults"""
        with self._lock:
            reset_count = 0
            for key in self._configurations:
                if self.reset_to_default(key):
                    reset_count += 1
            
            logger.info(f"Reset {reset_count} configurations to defaults")
            return reset_count
    
    def get_all_configs(self, category: str = None, scope: ConfigScope = None) -> Dict[str, Any]:
        """Get all configurations, optionally filtered by category or scope"""
        with self._lock:
            configs = {}
            
            for config in self._configurations.values():
                # Apply filters
                if category and config.category != category:
                    continue
                
                if scope and config.scope != scope:
                    continue
                
                # Return value (hide secrets in listings)
                if config.secret:
                    configs[config.key] = "***SECRET***"
                else:
                    configs[config.key] = config.value
            
            return configs
    
    def get_config_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get configuration metadata"""
        with self._lock:
            if key not in self._configurations:
                return None
            
            config = self._configurations[key]
            return {
                'key': config.key,
                'value': config.value,
                'default_value': config.default_value,
                'description': config.description,
                'scope': config.scope.value,
                'requires_restart': config.requires_restart,
                'category': config.category,
                'secret': config.secret
            }
    
    def export_config(self, file_path: Path, scope: ConfigScope = ConfigScope.USER,
                     include_secrets: bool = False) -> bool:
        """Export configuration to file"""
        try:
            configs = self.get_all_configs(scope=scope)
            
            # Remove secrets unless explicitly included
            if not include_secrets:
                for key, config in self._configurations.items():
                    if config.secret and config.scope == scope:
                        configs[key] = "***SECRET***"
            
            # Add metadata
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'scope': scope.value,
                'version': '1.0',
                'configurations': configs
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration exported to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export configuration: {e}")
            return False
    
    def import_config(self, file_path: Path, merge: bool = True) -> bool:
        """Import configuration from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if 'configurations' not in import_data:
                raise ValueError("Invalid configuration file format")
            
            imported_configs = import_data['configurations']
            imported_count = 0
            
            with self._lock:
                for key, value in imported_configs.items():
                    # Skip secrets in import unless explicit
                    if value == "***SECRET***":
                        continue
                    
                    # Skip if not merging and key exists
                    if not merge and key in self._configurations:
                        continue
                    
                    if self.set(key, value):
                        imported_count += 1
            
            logger.info(f"Imported {imported_count} configurations from: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False
    
    def _load_all_configurations(self):
        """Load all configurations from files"""
        for scope in ConfigScope:
            self._load_scope_configurations(scope)
    
    def _load_scope_configurations(self, scope: ConfigScope):
        """Load configurations for a specific scope"""
        config_file = self._get_config_file_path(scope)
        
        if not config_file.exists():
            logger.debug(f"Configuration file not found: {config_file}")
            return
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            with self._lock:
                for key, value in config_data.items():
                    if key in self._configurations:
                        config = self._configurations[key]
                        if config.scope == scope:
                            config.value = value
            
            logger.debug(f"Loaded {len(config_data)} configurations from {scope.value}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration file {config_file}: {e}")
    
    def _save_configuration(self, key: str, scope: ConfigScope):
        """Save configuration to file"""
        if scope == ConfigScope.SESSION:
            return  # Don't save session configs
        
        config_file = self._get_config_file_path(scope)
        file_lock = self._file_locks.get(str(config_file))
        if not file_lock:
            file_lock = threading.Lock()
            self._file_locks[str(config_file)] = file_lock
        
        with file_lock:
            try:
                # Load existing data
                config_data = {}
                if config_file.exists():
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                
                # Update specific key
                config_data[key] = self._configurations[key].value
                
                # Save back to file
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_data, f, indent=2, ensure_ascii=False)
                
            except Exception as e:
                logger.error(f"Failed to save configuration {key}: {e}")
    
    def _get_config_file_path(self, scope: ConfigScope) -> Path:
        """Get configuration file path for scope"""
        filename = f"{scope.value}_config.json"
        return self._config_dir / filename
    
    def _set_config_value(self, key: str, value: Any, scope: ConfigScope):
        """Set configuration value internally"""
        if key not in self._configurations:
            # Auto-register with default settings
            self.register_config(key, value, scope=scope)
        else:
            config = self._configurations[key]
            config.value = value
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get configuration statistics"""
        with self._lock:
            stats = {
                'total_configs': len(self._configurations),
                'by_category': {},
                'by_scope': {},
                'with_validators': 0,
                'secret_configs': 0
            }
            
            for config in self._configurations.values():
                # Count by category
                category = config.category
                stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
                
                # Count by scope
                scope = config.scope.value
                stats['by_scope'][scope] = stats['by_scope'].get(scope, 0) + 1
                
                # Count validators
                if config.validator:
                    stats['with_validators'] += 1
                
                # Count secrets
                if config.secret:
                    stats['secret_configs'] += 1
            
            return stats
    
    def validate_all(self) -> Dict[str, List[str]]:
        """Validate all configurations"""
        with self._lock:
            validation_results = {'valid': [], 'invalid': [], 'errors': []}
            
            for key, config in self._configurations.items():
                try:
                    if config.validator and not config.validator(config.value):
                        validation_results['invalid'].append(key)
                    else:
                        validation_results['valid'].append(key)
                except Exception as e:
                    validation_results['errors'].append(f"{key}: {e}")
            
            return validation_results
    
    def cleanup(self):
        """Cleanup resources"""
        with self._lock:
            # Clear file locks
            self._file_locks.clear()
            
            logger.info("Configuration manager cleaned up")


# Global configuration manager instance
_global_config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigurationManager()
    return _global_config_manager


def get_config(key: str, default: Any = None) -> Any:
    """Convenience function to get configuration"""
    return get_config_manager().get(key, default)


def set_config(key: str, value: Any) -> bool:
    """Convenience function to set configuration"""
    return get_config_manager().set(key, value)


# Configuration presets
class ConfigurationPresets:
    """Configuration presets for different use cases"""
    
    @staticmethod
    def developer_preset(config_manager: ConfigurationManager):
        """Apply developer configuration preset"""
        config_manager.set("system.debug_mode", True)
        config_manager.set("system.log_level", "DEBUG")
        config_manager.set("diagnostics.max_log_entries", 5000)
        logger.info("Applied developer configuration preset")
    
    @staticmethod
    def production_preset(config_manager: ConfigurationManager):
        """Apply production configuration preset"""
        config_manager.set("system.debug_mode", False)
        config_manager.set("system.log_level", "WARNING")
        config_manager.set("diagnostics.max_log_entries", 500)
        config_manager.set("diagnostics.update_interval", 1000)
        logger.info("Applied production configuration preset")
    
    @staticmethod
    def minimal_ui_preset(config_manager: ConfigurationManager):
        """Apply minimal UI configuration preset"""
        config_manager.set("ui.window_width", 1024)
        config_manager.set("ui.window_height", 600)
        logger.info("Applied minimal UI configuration preset")