from datetime import date
from ..models.gazette import GazetteData, MinisterEntry
from ..services.gazette_change_tracker import GazetteChangeTracker

def main():
    # Create an example old gazette
    old_gazette = GazetteData(
        gazette_id="2023-01",
        published_date=date(2023, 1, 1),
        ministers=[
            MinisterEntry(
                name="John Smith",
                departments=["Finance", "Education"],
                laws=["Law A", "Law B"],
                functions=["Budget Management", "Policy Development"]
            ),
            MinisterEntry(
                name="Jane Doe",
                departments=["Health"],
                laws=["Law C"],
                functions=["Healthcare Management"]
            )
        ]
    )

    # Create an example new gazette with some changes
    new_gazette = GazetteData(
        gazette_id="2023-02",
        published_date=date(2023, 2, 1),
        ministers=[
            MinisterEntry(
                name="John Smith",
                departments=["Finance", "Education", "Technology"],  # Added Technology
                laws=["Law A", "Law D"],  # Removed Law B, Added Law D
                functions=["Budget Management", "Digital Transformation"]  # Changed Policy Development to Digital Transformation
            ),
            # Jane Doe was removed
            MinisterEntry(
                name="Robert Johnson",  # New minister
                departments=["Health", "Social Services"],
                laws=["Law C", "Law E"],
                functions=["Healthcare Management", "Social Welfare"]
            )
        ]
    )

    # Create the tracker and compare gazettes
    tracker = GazetteChangeTracker()
    changes = tracker.compare_gazettes(old_gazette, new_gazette)

    # Print the summary of changes
    print("Gazette Changes Summary:")
    print("=======================")
    print(changes.summary)

    # Print detailed changes
    print("\nDetailed Changes:")
    print("================")
    for minister_change in changes.minister_changes:
        print(f"\nMinister: {minister_change.minister_name}")
        print(f"Change Type: {minister_change.change_type.value}")
        
        if minister_change.department_changes:
            print("\nDepartment Changes:")
            for dept_change in minister_change.department_changes:
                print(f"- {dept_change.department}: {dept_change.change_type.value}")
                if dept_change.old_value:
                    print(f"  Old value: {dept_change.old_value}")
                if dept_change.new_value:
                    print(f"  New value: {dept_change.new_value}")
        
        if minister_change.law_changes:
            print("\nLaw Changes:")
            for law_change in minister_change.law_changes:
                print(f"- {law_change.law}: {law_change.change_type.value}")
                if law_change.old_value:
                    print(f"  Old value: {law_change.old_value}")
                if law_change.new_value:
                    print(f"  New value: {law_change.new_value}")
        
        if minister_change.function_changes:
            print("\nFunction Changes:")
            for func_change in minister_change.function_changes:
                print(f"- {func_change.function}: {func_change.change_type.value}")
                if func_change.old_value:
                    print(f"  Old value: {func_change.old_value}")
                if func_change.new_value:
                    print(f"  New value: {func_change.new_value}")

if __name__ == "__main__":
    main() 