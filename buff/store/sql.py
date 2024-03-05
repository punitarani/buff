"""
buff/store/sql.py

SQL database connection and engine.
"""

import os

from sqlalchemy import Engine, create_engine

# Get Env vars
PGHOST = os.getenv("PGHOST")
PGPORT = os.getenv("PGPORT")
PGDATABASE = os.getenv("PGDATABASE")
PGUSER = os.getenv("PGUSER")
PGPASSWORD = os.getenv("PGPASSWORD")

# Ensure the Env vars are set
assert PGHOST is not None, "Env var PGHOST is not set."
assert PGPORT is not None, "Env var PGPORT is not set."
assert PGDATABASE is not None, "Env var PGDATABASE is not set."
assert PGUSER is not None, "Env var PGUSER is not set."
assert PGPASSWORD is not None, "Env var PGPASSWORD is not set."


# pylint: disable=too-many-arguments
def database_url(
        driver: str = "postgresql",
        host: str = PGHOST,
        port: str = PGPORT,
        username: str = PGDATABASE,
        password: str = PGUSER,
        database: str = PGPASSWORD,
        params: dict = None,
) -> str:
    """Construct a database URL"""
    url = f"{driver}://{username}:{password}@{host}:{port}/{database}"

    if params:
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{query_string}"

    return url


def get_engine(
        url: str = database_url(), echo: bool = False, args: dict = None
) -> Engine:
    """
    Get the SQLAlchemy engine.

    Args:
        url: The database URL.
        echo: Flag to enable SQL logging.
        args: The SQLAlchemy engine connect_args.

    Returns:
        The SQLAlchemy engine.
    """

    if args is None:
        args = {}

    engine = create_engine(
        url, echo=echo, connect_args=args, pool_size=10, max_overflow=10
    )
    return engine
