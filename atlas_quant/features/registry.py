"""Feature registry for managing and discovering features."""

from typing import Dict, List, Type
from .base import BaseFeature


class FeatureRegistry:
    """Registry for feature classes.

    This class maintains a mapping of feature keys to their classes.
    It allows for automatic discovery and instantiation of features.
    """

    def __init__(self):
        self._features: Dict[str, Type[BaseFeature]] = {}

    def register(self, feature_class: Type[BaseFeature]) -> None:
        """Register a feature class.

        Args:
            feature_class: The feature class to register.

        Raises:
            ValueError: If a feature with the same key is already registered.
        """
        # Get the key from class attribute `feature_key`; if not present, use class name lowercased
        if hasattr(feature_class, 'feature_key'):
            key = feature_class.feature_key
        else:
            # Fallback: use the class name converted to lowercase
            key = feature_class.__name__.lower()
        if key in self._features:
            raise ValueError(f'''Feature key ''{key}'' is already registered.''')
        self._features[key] = feature_class

    def get(self, key: str) -> Type[BaseFeature]:
        """Get a feature class by key.

        Args:
            key: The key of the feature (as used in registration).

        Returns:
            Type[BaseFeature]: The feature class.

        Raises:
            KeyError: If the feature is not found.
        """
        if key not in self._features:
            raise KeyError(f'''Feature ''{key}'' not found in registry.''')
        return self._features[key]

    def list_features(self) -> List[str]:
        """List all registered feature keys.

        Returns:
            List[str]: Sorted list of feature keys.
        """
        return sorted(self._features.keys())

    def get_categories(self) -> Dict[str, List[str]]:
        """Group features by their category.

        Returns:
            Dict[str, List[str]]: Mapping from category to list of feature keys.
        """
        categories: Dict[str, List[str]] = {}
        for key, cls in self._features.items():
            if hasattr(cls, 'category'):
                category = cls._category
            else:
                continue
            if category not in categories:
                categories[category] = []
            categories[category].append(key)
        return categories


# Global registry instance
registry = FeatureRegistry()
