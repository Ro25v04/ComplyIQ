import os
from backend.config import settings

# Langfuse reads credentials from env vars at import time, so they must be set
# before the langfuse module is imported — the out-of-order import is intentional
os.environ["LANGFUSE_PUBLIC_KEY"] = settings.langfuse_public_key
os.environ["LANGFUSE_SECRET_KEY"] = settings.langfuse_secret_key
os.environ["LANGFUSE_HOST"] = settings.langfuse_host

from langfuse import observe, get_client  # noqa: E402, F401
