"""Custom exceptions for Atlas Quant."""


class AtlasQuantError(Exception):
    """Base exception for Atlas Quant."""


class DownloadError(AtlasQuantError):
    """Raised when data download fails."""


class ValidationError(AtlasQuantError):
    """Raised when data validation fails."""


class CacheError(AtlasQuantError):
    """Raised when cache operations fail."""


class ConfigurationError(AtlasQuantError):
    """Raised when configuration is invalid."""
