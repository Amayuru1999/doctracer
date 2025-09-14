# models/gazette.py
from pydantic import BaseModel
from datetime import date
from typing import List

class MinisterEntry(BaseModel):
    name: str
    number: str
    departments: List[str]
    laws: List[str]
    functions: List[str]

class GazetteData(BaseModel):
    gazette_id: str
    published_date: date
    published_by: str
    president: str
    gazette_type: str
    language: str
    pdf_url: str
    ministers: List[MinisterEntry]
