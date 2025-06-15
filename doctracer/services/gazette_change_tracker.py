from datetime import datetime
from typing import List, Dict, Set, Type, TypeVar, Generic
from ..models.gazette import GazetteData, MinisterEntry
from ..models.gazette_change import (
    GazetteChange,
    MinisterChange,
    DepartmentChange,
    LawChange,
    FunctionChange,
    ChangeType
)

T = TypeVar('T', DepartmentChange, LawChange, FunctionChange)

class GazetteChangeTracker:
    @staticmethod
    def compare_gazettes(old_gazette: GazetteData, new_gazette: GazetteData) -> GazetteChange:
        """
        Compare two gazettes and return the changes between them.
        """
        minister_changes = []
        
        # Create dictionaries for easy lookup
        old_ministers = {m.name: m for m in old_gazette.ministers}
        new_ministers = {m.name: m for m in new_gazette.ministers}
        
        # Get all unique minister names
        all_ministers = set(old_ministers.keys()) | set(new_ministers.keys())
        
        for minister_name in all_ministers:
            old_minister = old_ministers.get(minister_name)
            new_minister = new_ministers.get(minister_name)
            
            if not old_minister:
                # Minister was added
                minister_change = MinisterChange(
                    minister_name=minister_name,
                    change_type=ChangeType.ADDED,
                    department_changes=[
                        DepartmentChange(
                            department=dept,
                            change_type=ChangeType.ADDED,
                            new_value=dept
                        ) for dept in new_minister.departments
                    ],
                    law_changes=[
                        LawChange(
                            law=law,
                            change_type=ChangeType.ADDED,
                            new_value=law
                        ) for law in new_minister.laws
                    ],
                    function_changes=[
                        FunctionChange(
                            function=func,
                            change_type=ChangeType.ADDED,
                            new_value=func
                        ) for func in new_minister.functions
                    ]
                )
            elif not new_minister:
                # Minister was removed
                minister_change = MinisterChange(
                    minister_name=minister_name,
                    change_type=ChangeType.REMOVED,
                    department_changes=[
                        DepartmentChange(
                            department=dept,
                            change_type=ChangeType.REMOVED,
                            old_value=dept
                        ) for dept in old_minister.departments
                    ],
                    law_changes=[
                        LawChange(
                            law=law,
                            change_type=ChangeType.REMOVED,
                            old_value=law
                        ) for law in old_minister.laws
                    ],
                    function_changes=[
                        FunctionChange(
                            function=func,
                            change_type=ChangeType.REMOVED,
                            old_value=func
                        ) for func in old_minister.functions
                    ]
                )
            else:
                # Minister was modified
                department_changes = GazetteChangeTracker._compare_lists(
                    old_minister.departments,
                    new_minister.departments,
                    DepartmentChange,
                    'department'
                )
                law_changes = GazetteChangeTracker._compare_lists(
                    old_minister.laws,
                    new_minister.laws,
                    LawChange,
                    'law'
                )
                function_changes = GazetteChangeTracker._compare_lists(
                    old_minister.functions,
                    new_minister.functions,
                    FunctionChange,
                    'function'
                )
                
                minister_change = MinisterChange(
                    minister_name=minister_name,
                    change_type=ChangeType.MODIFIED,
                    department_changes=department_changes,
                    law_changes=law_changes,
                    function_changes=function_changes
                )
            
            minister_changes.append(minister_change)
        
        # Generate a summary of changes
        summary = GazetteChangeTracker._generate_summary(minister_changes)
        
        return GazetteChange(
            old_gazette_id=old_gazette.gazette_id,
            new_gazette_id=new_gazette.gazette_id,
            change_date=datetime.now(),
            minister_changes=minister_changes,
            summary=summary
        )
    
    @staticmethod
    def _compare_lists(old_list: List[str], new_list: List[str], change_class: Type[T], field_name: str) -> List[T]:
        """
        Compare two lists and return a list of changes.
        """
        changes = []
        old_set = set(old_list)
        new_set = set(new_list)
        
        # Find added items
        for item in new_set - old_set:
            changes.append(change_class(
                **{field_name: item},
                change_type=ChangeType.ADDED,
                new_value=item
            ))
        
        # Find removed items
        for item in old_set - new_set:
            changes.append(change_class(
                **{field_name: item},
                change_type=ChangeType.REMOVED,
                old_value=item
            ))
        
        return changes
    
    @staticmethod
    def _generate_summary(minister_changes: List[MinisterChange]) -> str:
        """
        Generate a human-readable summary of the changes.
        """
        summary_parts = []
        
        for change in minister_changes:
            if change.change_type == ChangeType.ADDED:
                summary_parts.append(f"Added Minister: {change.minister_name}")
            elif change.change_type == ChangeType.REMOVED:
                summary_parts.append(f"Removed Minister: {change.minister_name}")
            else:
                summary_parts.append(f"Modified Minister: {change.minister_name}")
                
                if change.department_changes:
                    dept_changes = [f"{c.department} ({c.change_type.value})" 
                                  for c in change.department_changes]
                    summary_parts.append(f"  Department changes: {', '.join(dept_changes)}")
                
                if change.law_changes:
                    law_changes = [f"{c.law} ({c.change_type.value})" 
                                 for c in change.law_changes]
                    summary_parts.append(f"  Law changes: {', '.join(law_changes)}")
                
                if change.function_changes:
                    func_changes = [f"{c.function} ({c.change_type.value})" 
                                  for c in change.function_changes]
                    summary_parts.append(f"  Function changes: {', '.join(func_changes)}")
        
        return "\n".join(summary_parts) 