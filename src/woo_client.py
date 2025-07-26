from woocommerce import API
from pathlib import Path
import json
import logging
from typing import Dict, List, Optional, Any
logger = logging.getLogger(__name__)

class WooClient:
    def __init__(self, config_path: str = "./config.json"):
        if not Path(config_path).is_absolute():
            current_dir = Path(__file__).parent
            config_path = current_dir.parent / config_path

        self.config = self._load_config(str(config_path))
        self.api = self._create_api_client()

    def _load_config(self, config_path: str) -> Dict[str, str]:
        """Load WooCommerce configuration from JSON file."""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_path}")

            with open(config_file, 'r') as f:
                config = json.load(f)

            required_keys = ['store_url', 'consumer_key', 'consumer_secret', 'api_version']
            missing_keys = [key for key in required_keys if key not in config]

            if missing_keys:
                raise ValueError(f"Missing required configuration keys: {missing_keys}")

            return config

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    def _create_api_client(self) -> API:
        """Create WooCommerce API client."""
        try:
            return API(
                url=self.config['store_url'],
                consumer_key=self.config['consumer_key'],
                consumer_secret=self.config['consumer_secret'],
                version=self.config['api_version'],
                timeout=30
            )

        except Exception as e:
            logger.error(f"Failed to create WooCommerce API client: {e}")
            raise

    def get_products(self, **params) -> List[Dict[str, Any]]:
        try:
            response = self.api.get("products", params=params)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Failed to fetch products: {e}")
            raise

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        try:
            response = self.api.get(f"products/{product_id}")
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Failed to fetch product by ID: {e}")
            raise

    def update_product(self, product_id: int, data: Dict[str, Any]):
        try:
            response = self.api.put(f"products/{product_id}", data)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Failed to update product {product_id}: {e}")
            raise

    def get_categories(self, **params) -> List[Dict[str, Any]]:
        """Fetch product categories."""
        try:
            response = self.api.get("products/categories", params=params)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Failed to fetch categories: {e}")
            raise

    def get_store_info(self) -> Dict[str, Any]:
        """Get basic store information."""
        try:
            # Get system status for store info
            response = self.api.get("system_status")
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"API request failed: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Failed to fetch store info: {e}")
            raise