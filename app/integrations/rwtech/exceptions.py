"""Exceções específicas da integração com relógios."""


class RwtechIntegrationError(Exception):
    """Erro base da integração RWTECH."""


class RwtechNotConfiguredError(RwtechIntegrationError):
    """Indica que a comunicação real ainda não foi configurada."""

