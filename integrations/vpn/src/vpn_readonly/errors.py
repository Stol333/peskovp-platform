class VPNIntegrationError(Exception):
    """Базовая ошибка VPN read-only интеграции."""


class VPNConfigurationError(VPNIntegrationError):
    """Ошибка конфигурации интеграции."""


class VPNResponseError(VPNIntegrationError):
    """Ошибка ответа от VPN API."""
