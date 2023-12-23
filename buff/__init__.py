"""buff package"""

from .secrets import Secrets

SECRETS = Secrets.load()

__all__ = ["SECRETS"]
