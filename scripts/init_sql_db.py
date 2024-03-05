#!/usr/bin/env python3

# NOTE: This script creates the database tables.
#   It should be run only once when the database is first created.

from sqlalchemy.orm import sessionmaker

from buff.schemas import Base
from buff.store.sql import get_engine

print("Creating database tables")

print("Getting the engine")
engine = get_engine(echo=True)

# Bind the engine to the metadata of the Base class
# This allows declaratives to be accessed through the DBSession instance
print("Binding the engine to the metadata of the Base class")
Base.metadata.bind = engine

# Create a session
print("Creating a database session")
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create all tables in the engine
print("Creating all tables in the engine")
Base.metadata.create_all(engine)
