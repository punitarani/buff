"""
buff/schemas.py

Database Schemas
"""

from sqlalchemy import ARRAY, Boolean, Column, ForeignKey, Integer, Text
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


class WorkCitations(Base):
    __tablename__ = "work_citations"

    id = Column(Text, primary_key=True, index=True)
    work_id = Column(Text, ForeignKey(Work.id, ondelete="CASCADE"), nullable=False)
    citations = Column(ARRAY(Text), default=[], nullable=False)
    count = Column(Integer, nullable=False)


class WorkReferences(Base):
    __tablename__ = "work_references"

    id = Column(Text, primary_key=True, index=True)
    work_id = Column(Text, ForeignKey(Work.id, ondelete="CASCADE"), nullable=False)
    references = Column(ARRAY(Text), default=[], nullable=False)
    count = Column(Integer, nullable=False)


class WorkChunk(Base):
    __tablename__ = "work_chunks"

    id = Column(Text, primary_key=True, index=True)
    work_id = Column(Text, ForeignKey(Work.id, ondelete="CASCADE"), nullable=False)
    index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
