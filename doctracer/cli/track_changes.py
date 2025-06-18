import click
import json
from datetime import datetime
from pathlib import Path
from ..models.gazette import GazetteData, MinisterEntry
from ..services.gazette_change_tracker import GazetteChangeTracker

def validate_gazette_data(data: dict, file_path: str) -> None:
    """Validate the structure of gazette data."""
    required_fields = ['gazette_id', 'published_date', 'ministers']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field '{field}' in {file_path}")
    
    if not isinstance(data['ministers'], list):
        raise ValueError(f"'ministers' must be a list in {file_path}")
    
    for i, minister in enumerate(data['ministers']):
        if not isinstance(minister, dict):
            raise ValueError(f"Minister at index {i} must be a dictionary in {file_path}")
        
        required_minister_fields = ['name', 'departments', 'laws', 'functions']
        for field in required_minister_fields:
            if field not in minister:
                raise ValueError(f"Missing required field '{field}' in minister at index {i} in {file_path}")
        
        if not isinstance(minister['departments'], list):
            raise ValueError(f"'departments' must be a list in minister at index {i} in {file_path}")
        if not isinstance(minister['laws'], list):
            raise ValueError(f"'laws' must be a list in minister at index {i} in {file_path}")
        if not isinstance(minister['functions'], list):
            raise ValueError(f"'functions' must be a list in minister at index {i} in {file_path}")

@click.command()
@click.argument('old_gazette_file', type=click.Path(exists=True))
@click.argument('new_gazette_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file for the changes (JSON format)')
@click.option('--summary-only', is_flag=True, help='Show only the summary of changes')
def track_changes(old_gazette_file, new_gazette_file, output, summary_only):
    """Track changes between two gazette files."""
    try:
        # Convert paths to Path objects
        old_path = Path(old_gazette_file)
        new_path = Path(new_gazette_file)
        
        # Load and validate the gazette files
        try:
            with open(old_path, 'r') as f:
                old_data = json.load(f)
            validate_gazette_data(old_data, str(old_path))
        except json.JSONDecodeError:
            raise click.ClickException(f"Invalid JSON format in {old_path}")
        except ValueError as e:
            raise click.ClickException(str(e))
        
        try:
            with open(new_path, 'r') as f:
                new_data = json.load(f)
            validate_gazette_data(new_data, str(new_path))
        except json.JSONDecodeError:
            raise click.ClickException(f"Invalid JSON format in {new_path}")
        except ValueError as e:
            raise click.ClickException(str(e))

        # Convert to GazetteData objects
        try:
            old_gazette = GazetteData(
                gazette_id=old_data['gazette_id'],
                published_date=datetime.strptime(old_data['published_date'], '%Y-%m-%d').date(),
                ministers=[
                    MinisterEntry(**minister) for minister in old_data['ministers']
                ]
            )

            new_gazette = GazetteData(
                gazette_id=new_data['gazette_id'],
                published_date=datetime.strptime(new_data['published_date'], '%Y-%m-%d').date(),
                ministers=[
                    MinisterEntry(**minister) for minister in new_data['ministers']
                ]
            )
        except ValueError as e:
            raise click.ClickException(f"Invalid date format in gazette data: {str(e)}")
        except Exception as e:
            raise click.ClickException(f"Error creating GazetteData objects: {str(e)}")

        # Compare gazettes
        try:
            tracker = GazetteChangeTracker()
            changes = tracker.compare_gazettes(old_gazette, new_gazette)
        except Exception as e:
            raise click.ClickException(f"Error comparing gazettes: {str(e)}")

        if summary_only:
            print(changes.summary)
        else:
            # Print detailed changes
            print("Gazette Changes Summary:")
            print("=======================")
            print(changes.summary)

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

        # Save changes to output file if specified
        if output:
            try:
                output_path = Path(output)
                with open(output_path, 'w') as f:
                    json.dump(changes.dict(), f, indent=2, default=str)
                print(f"\nChanges saved to {output_path}")
            except Exception as e:
                raise click.ClickException(f"Error saving changes to {output}: {str(e)}")

    except click.ClickException as e:
        click.echo(str(e), err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    track_changes() 