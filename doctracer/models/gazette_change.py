from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from enum import Enum

class ChangeType(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"

class DepartmentChange(BaseModel):
    department: str
    change_type: ChangeType
    old_value: Optional[str] = None
    new_value: Optional[str] = None

class LawChange(BaseModel):
    law: str
    change_type: ChangeType
    old_value: Optional[str] = None
    new_value: Optional[str] = None

class FunctionChange(BaseModel):
    function: str
    change_type: ChangeType
    old_value: Optional[str] = None
    new_value: Optional[str] = None

class MinisterChange(BaseModel):
    minister_name: str
    change_type: ChangeType
    department_changes: List[DepartmentChange] = []
    law_changes: List[LawChange] = []
    function_changes: List[FunctionChange] = []

class GazetteChange(BaseModel):
    old_gazette_id: str
    new_gazette_id: str
    change_date: datetime
    minister_changes: List[MinisterChange]
    summary: str 