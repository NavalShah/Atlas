"""Feature pipeline for executing features in the correct order."""

import pandas as pd
from typing import List, Dict, Any
from .registry import registry
from .base import BaseFeature
import logging

logger = logging.getLogger(__name__)


class FeaturePipeline:
    """Pipeline for executing a list of features.

    The pipeline handles:
    - Instantiating feature classes
    - Validating input data
    - Executing features in the order they are added
    - Handling dependencies (features that require other features to be computed first)
    - Combining results into a single DataFrame

    Note: This version does not automatically resolve dependencies.
    Users must specify features in an order that respects dependencies.
    Future versions could implement a dependency graph.
    """

    def __init__(self):
        self._features: List[BaseFeature] = []
        self._feature_configs: List[Dict[str, Any]] = []

    def add_feature(self, feature_name: str, **kwargs) -> None:
        """Add a feature to the pipeline.

        Args:
            feature_name: The name of the feature to add (as registered in the registry).
            **kwargs: Configuration parameters for the feature.

        Raises:
            KeyError: If the feature is not registered.
        """
        feature_class = registry.get(feature_name)
        # Instantiate the feature with the given configuration
        feature_instance = feature_class(**kwargs)
        self._features.append(feature_instance)
        self._feature_configs.append({'name': feature_name, 'config': kwargs})
        logger.debug(f"Added feature '{feature_name}' with config {kwargs}")

    def remove_feature(self, feature_name: str) -> None:
        """Remove a feature from the pipeline.

        Args:
            feature_name: The name of the feature to remove.

        Note: This removes the first occurrence if there are duplicates.
        """
        for i, config in enumerate(self._feature_configs):
            if config['name'] == feature_name:
                del self._features[i]
                del self._feature_configs[i]
                logger.debug(f"Removed feature '{feature_name}'")
                return
        logger.warning(f"Feature '{feature_name}' not found in pipeline.")

    def clear(self) -> None:
        """Remove all features from the pipeline."""
        self._features.clear()
        self._feature_configs.clear()
        logger.debug("Cleared all features from pipeline.")

    def execute(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Execute all features in the pipeline on the input data.

        Args:
            dataframe: Input DataFrame with OHLCV data.

        Returns:
            DataFrame: The input data with all feature columns appended.

        Raises:
            ValueError: If any feature fails validation or calculation.
        """
        if dataframe is None or dataframe.empty:
            raise ValueError("Input DataFrame is None or empty")

        # Start with a copy of the input to avoid modifying the original
        result = dataframe.copy()

        for feature in self._features:
            feature_name = feature.__class__.__name__
            try:
                # Validate the input for this feature
                feature.validate(result)
                # Calculate the feature
                result = feature.calculate(result)
                logger.debug(f"Successfully executed feature '{feature_name}'")
            except Exception as e:
                logger.error(f"Failed to execute feature '{feature_name}': {e}")
                raise

        return result

    def get_feature_names(self) -> List[str]:
        """Get the names of all features in the pipeline.

        Returns:
            List[str]: List of feature names.
        """
        return [config['name'] for config in self._feature_configs]

    def get_feature_configs(self) -> List[Dict[str, Any]]:
        """Get the configuration of all features in the pipeline.

        Returns:
            List[Dict[str, Any]]: List of feature configurations.
        """
        return self._feature_configs.copy()