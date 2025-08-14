import os
import yaml
import logging
from typing import Any, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

class ConfigLoader:
    """Loads and manages configuration from YAML files and environment variables."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = {}
        self._load_environment()
        self._load_config_file()
        self._validate_config()
    
    def _load_environment(self):
        """Loads environment variables from .env file."""
        try:
            load_dotenv()
            logger.info("Environment variables loaded from .env file")
        except Exception as e:
            logger.warning(f"Could not load .env file: {e}")
    
    def _load_config_file(self):
        """Loads configuration from YAML file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                logger.warning(f"Configuration file {self.config_path} not found, using defaults")
                self.config = self._get_default_config()
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            self.config = self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Gets default configuration values if no file exists."""
        return {
            'app': {
                'name': 'Crypto Alert Dashboard',
                'version': '2.0.0',
                'debug': False,
                'log_level': 'INFO',
                'auto_refresh_interval': 60000
            },
            'api': {
                'coingecko': {
                    'base_url': 'https://api.coingecko.com/api/v3',
                    'timeout': 10,
                    'rate_limit_delay': 1.1,
                    'cache_ttl': 300
                }
            },
            'database': {
                'type': 'sqlite',
                'sqlite': {
                    'path': 'data/crypto_alert.db'
                }
            }
        }
    
    def _validate_config(self):
        """Makes sure the config has the essential parts."""
        required_keys = ['app', 'api']
        
        for key in required_keys:
            if key not in self.config:
                logger.warning(f"Missing required configuration key: {key}")
                if key == 'app':
                    self.config[key] = self._get_default_config()[key]
                elif key == 'api':
                    self.config[key] = self._get_default_config()[key]
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Gets a configuration value using dot notation.
        
        Args:
            key_path: Path to the config value (e.g., 'app.name', 'api.coingecko.timeout')
            default: What to return if the key doesn't exist
            
        Returns:
            The configuration value or the default
        """
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return self._resolve_environment_variable(key_path) or default
            
            # Handle environment variable placeholders
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                return os.getenv(env_var, default)
            
            return value
            
        except Exception as e:
            logger.error(f"Error getting configuration value for {key_path}: {e}")
            return default
    
    def _resolve_environment_variable(self, key_path: str) -> Optional[str]:
        """Tries to find a configuration key as an environment variable."""
        # Try different naming conventions
        env_vars = [
            key_path.upper(),
            key_path.upper().replace('.', '_'),
            key_path.upper().replace('.', '__')
        ]
        
        for env_var in env_vars:
            value = os.getenv(env_var)
            if value is not None:
                return value
        
        return None
    
    def get_all(self) -> Dict[str, Any]:
        """Gets the entire configuration dictionary."""
        return self.config.copy()
    
    def reload(self):
        """Reloads configuration from file."""
        self._load_config_file()
        self._validate_config()
        logger.info("Configuration reloaded")
    
    def update(self, updates: Dict[str, Any]):
        """Updates configuration with new values."""
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
        
        self.config = deep_update(self.config, updates)
        logger.info("Configuration updated")
    
    def save(self, file_path: Optional[str] = None):
        """Saves current configuration to file."""
        try:
            save_path = Path(file_path) if file_path else self.config_path
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False

# Create a global config instance
config = ConfigLoader()

# Helper functions for easy access
def get_config(key_path: str, default: Any = None) -> Any:
    """Gets a configuration value."""
    return config.get(key_path, default)

def get_all_config() -> Dict[str, Any]:
    """Gets all configuration values."""
    return config.get_all()

def reload_config():
    """Reloads configuration."""
    config.reload()

def update_config(updates: Dict[str, Any]):
    """Updates configuration."""
    config.update(updates)

def save_config(file_path: Optional[str] = None):
    """Saves configuration to file."""
    return config.save(file_path)
