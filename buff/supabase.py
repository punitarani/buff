"""buff/supabase.py"""


import os

from supabase import Client, create_client
from supabase.client import ClientOptions

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

assert url is not None, "SUPABASE_URL environment variable is not set"
assert key is not None, "SUPABASE_KEY environment variable is not set"

supabase: Client = create_client(
    url,
    key,
    options=ClientOptions(postgrest_client_timeout=10, storage_client_timeout=10),
)
