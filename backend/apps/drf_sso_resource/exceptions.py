class SSOAuthError(Exception):
    """Raised when SSO authentication or token validation fails."""


class SSOConfigError(Exception):
    """Raised when required SSO settings are missing or invalid."""


class SSOUserSyncError(Exception):
    """Raised when the user-sync handler encounters an unrecoverable error."""
