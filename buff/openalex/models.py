"""buff/openalex/models.py"""

from typing import Optional

from pydantic import BaseModel, HttpUrl


class InvertedIndex(BaseModel):
    """Inverted index of the abstract of a paper"""

    terms: Optional[dict[str, list[int] | None] | list[int] | None] = None


class Author(BaseModel):
    """Author of a paper"""

    id: Optional[HttpUrl] = None
    display_name: Optional[str] = None
    orcid: Optional[HttpUrl] = None


class Institution(BaseModel):
    """Institution of an author of a paper"""

    id: Optional[HttpUrl] = None
    display_name: Optional[str] = None
    ror: Optional[HttpUrl] = None
    country_code: Optional[str] = None
    type: Optional[str] = None


class Authorship(BaseModel):
    """Authorship of a paper"""

    author_position: Optional[str] = None
    author: Optional[Author] = None
    institutions: Optional[list[Institution]] = None


class APC(BaseModel):
    """Article Processing Charge of a paper"""

    value: Optional[int] = None
    currency: Optional[str] = None
    provenance: Optional[str] = None
    value_usd: Optional[int] = None


class OALocation(BaseModel):
    """Open Access location of a paper"""

    is_oa: Optional[bool] = None
    landing_page_url: Optional[HttpUrl] = None
    pdf_url: Optional[HttpUrl] = None
    source: Optional[dict[str, bool | str | list[str] | HttpUrl | None]] = None
    license: Optional[str] = None
    version: Optional[str] = None


class Concept(BaseModel):
    """Concept of a paper"""

    id: Optional[HttpUrl] = None
    wikidata: Optional[HttpUrl] = None
    display_name: Optional[str] = None
    level: Optional[int] = None
    score: Optional[float] = None


class YearCount(BaseModel):
    """Year count of a paper"""

    year: Optional[int] = None
    cited_by_count: Optional[int] = None


class Ngram(BaseModel):
    """Ngram of a paper""" ""

    ngram: Optional[str] = None
    ngram_count: Optional[int] = None
    ngram_tokens: Optional[int] = None
    term_frequency: Optional[float] = None


class OpenAccess(BaseModel):
    """Open Access information of a paper""" ""

    is_oa: Optional[bool] = None
    oa_status: Optional[str] = None
    oa_url: Optional[HttpUrl] = None
    any_repository_has_fulltext: Optional[bool] = None


class MeshTag(BaseModel):
    """MeSH tag of a paper"""

    descriptor_ui: Optional[str] = None
    descriptor_name: Optional[str] = None
    qualifier_ui: Optional[str] = None
    qualifier_name: Optional[str] = None
    is_major_topic: Optional[bool] = None


class SDG(BaseModel):
    """Sustainable Development Goal of a paper"""

    id: Optional[HttpUrl] = None
    display_name: Optional[str] = None
    score: Optional[float] = None


class Grant(BaseModel):
    """Grant of a paper"""

    funder: Optional[HttpUrl] = None
    funder_display_name: Optional[str] = None
    award_id: Optional[str] = None


class WorkObject(BaseModel):
    """Work object of a paper"""

    abstract_inverted_index: Optional[InvertedIndex] = None
    authorships: Optional[list[Authorship]] = None
    apc_list: Optional[APC] = None
    apc_paid: Optional[APC] = None
    best_oa_location: Optional[OALocation] = None
    biblio: Optional[dict[str, str | None]] = None
    cited_by_api_url: Optional[HttpUrl] = None
    cited_by_count: Optional[int] = None
    concepts: Optional[list[Concept]] = None
    corresponding_author_ids: Optional[list[HttpUrl]] = None
    corresponding_institution_ids: Optional[list[HttpUrl]] = None
    countries_distinct_count: Optional[int] = None
    counts_by_year: Optional[list[YearCount]] = None
    created_date: Optional[str] = None
    display_name: Optional[str] = None
    doi: Optional[HttpUrl] = None
    fulltext_origin: Optional[str] = None
    grants: Optional[list[Grant]] = None
    has_fulltext: Optional[bool] = None
    id: Optional[HttpUrl] = None
    ids: Optional[dict[str, HttpUrl | int | None]] = None
    institutions_distinct_count: Optional[int] = None
    is_paratext: Optional[bool] = None
    is_retracted: Optional[bool] = None
    language: Optional[str] = None
    license: Optional[str] = None
    locations: Optional[list[OALocation]] = None
    locations_count: Optional[int] = None
    mesh: Optional[list[MeshTag]] = None
    ngrams_url: Optional[HttpUrl] = None
    open_access: Optional[OpenAccess] = None
    primary_location: Optional[OALocation] = None
    publication_date: Optional[str] = None
    publication_year: Optional[int] = None
    referenced_works: Optional[list[HttpUrl]] = None
    related_works: Optional[list[HttpUrl]] = None
    sustainable_development_goals: Optional[list[SDG]] = None
    title: Optional[str] = None
    type: Optional[str] = None
    type_crossref: Optional[str] = None
    updated_date: Optional[str] = None


class WorkNGram(BaseModel):
    """Ngram object of a paper"""

    ngram: Optional[str] = None
    ngram_count: Optional[int] = None
    ngram_tokens: Optional[int] = None
    term_frequency: Optional[float] = None


class WorkOpenAccess(BaseModel):
    """Open Access object of a paper"""

    any_repository_has_fulltext: Optional[bool] = None
    is_oa: Optional[bool] = None
    oa_status: Optional[str] = None
    oa_url: Optional[HttpUrl] = None
