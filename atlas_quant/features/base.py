"""Base feature class for all technical indicators."""

from abc import ABC, abstractmethod
from typing import List
import pandas as pd


class BaseFeature(ABC):
    """Abstract base class for all features.

    Every feature must inherit from this class and implement the required properties and methods.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the feature.

        Returns:
            str: The name of the feature.
        """
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """Category of the feature (e.g., 'trend', 'momentum').

        Returns:
            str: The category.
        """
        pass

    @property
    @abstractmethod
    def required_columns(self) -> List[str]:
        """List of column names required from the input DataFrame.

        Returns:
            List[str]: Required column names.
        """
        pass

    @property
    @abstractmethod
    def generated_columns(self) -> List[str]:
        """List of column names that this feature will generate.

        Returns:
            List[str]: Generated column names.
        """
        pass

    @abstractmethod
    def calculate(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Calculate the feature and return a DataFrame with the generated columns.

        Args:
            dataframe: Input DataFrame with at least the required columns.

        Returns:
            DataFrame: Original dataframe with the generated columns appended.
        """
        pass

    def validate(self, dataframe: pd.DataFrame) -> None:
        """Validate that the input dataframe meets the requirements.

        This method checks for the presence of required columns and sufficient history.
        It can be overridden by subclasses for additional validation.

        Args:
            dataframe: Input DataFrame to validate.

        Raises:
            ValueError: If validation fails.
        """
        missing = set(self.required_columns) - set(dataframe.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Check that the dataframe is not empty
        if dataframe.empty:
            raise ValueError("Input DataFrame is empty")
