"""
buff/schemas.py

Database Schemas
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for sql database models"""

    pass


class Work(Base):
    __tablename__ = "works"

    id = Column(Text, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    doi = Column(Text, unique=True, nullable=True)
    pdf_url = Column(Text, nullable=True)
    embed = Column(Boolean, default=False, nullable=False)


class WorkChunk(Base):
    __tablename__ = "work_chunks"

    id = Column(Text, primary_key=True, index=True)
    work_id = Column(Text, ForeignKey(Work.id, ondelete="CASCADE"), nullable=False)
    index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
