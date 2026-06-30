"""Feature set for loading predefined groups of features from configuration."""

import yaml
from pathlib import Path
from typing import Dict, Any, List
from .pipeline import FeaturePipeline
import logging

logger = logging.getLogger(__name__)


class FeatureSet:
    """A collection of features defined by a configuration file.

    This class allows defining a set of features (with their parameters) in a
    YAML file and then instantiating a pipeline from it.

    Expected YAML format:
    ```yaml
    features:
      - name: sma_20
        params:
          period: 20
      - name: rsi_14
        params:
          period: 14
    ```
    """

    def __init__(self, config_path: str):
        """Initialize the feature set from a configuration file.

        Args:
            config_path: Path to the YAML configuration file.
        """
        self.config_path = Path(config_path)
        self.pipeline = FeaturePipeline()
        self._load_config()

    def _load_config(self) -> None:
        """Load the feature configuration from the YAML file."""
        if not self.config_path.is_file():
            raise FileNotFoundError(f"Feature configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {self.config_path}: {e}")

        if not isinstance(config, dict) or 'features' not in config:
            raise ValueError("Invalid configuration: expected a dictionary with a 'features' key")

        feature_configs = config['features']
        if not isinstance(feature_configs, list):
            raise ValueError("'features' must be a list")

        for feature_spec in feature_configs:
            if not isinstance(feature_spec, dict):
                raise ValueError("Each feature specification must be a dictionary")
            if 'name' not in feature_spec:
                raise ValueError("Each feature specification must have a 'name' field")
            name = feature_spec['name']
            params = feature_spec.get('params', {})
            self.pipeline.add_feature(name, **params)

        logger.info(f"Loaded {len(self.pipeline.get_feature_names())} features from {self.config_path}")

    def get_pipeline(self) -> FeaturePipeline:
        """Get the configured pipeline.

        Returns:
            FeaturePipeline: The pipeline with all features added.
        """
        return self.pipeline

    def add_feature(self, feature_name: str, **kwargs) -> None:
        """Add a feature to the existing set.

        Args:
            feature_name: The name of the feature to add.
            **kwargs: Configuration parameters for the feature.
        """
        self.pipeline.add_feature(feature_name, **kwargs)

    def remove_feature(self, feature_name: str) -> None:
        """Remove a feature from the set.

        Args:
            feature_name: The name of the feature to remove.
        """
        self.pipeline.remove_feature(feature_name)

    def list_features(self) -> List[str]:
        """List all features in the set.

        Returns:
            List[str]: List of feature names.
        """
        return self.pipeline.get_feature_names()