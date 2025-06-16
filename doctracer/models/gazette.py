# models/gazette.py
from pydantic import BaseModel
from datetime import date
from typing import List

class MinisterEntry(BaseModel):
    name: str
    departments: List[str]
    laws: List[str]
    functions: List[str]

class GazetteData(BaseModel):
    gazette_id: str
    published_date: date
    ministers: List[MinisterEntry]
