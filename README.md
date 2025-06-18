# DocTracer - Gazette Change Tracking System

DocTracer is a powerful system for tracking and analyzing changes in government gazettes. It helps you monitor modifications in ministerial appointments, departments, laws, and functions across different gazette publications.

## Features

- Track changes between different gazette publications
- Monitor ministerial appointments (additions, removals, modifications)
- Track changes in departments, laws, and functions
- Generate detailed change reports
- Export changes in JSON format
- Command-line interface for easy usage
- Python API for programmatic access

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/doctracer.git
cd doctracer
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

The CLI tool allows you to track changes between two gazette files:

```bash
python -m doctracer.cli.track_changes old_gazette.json new_gazette.json
```

#### Options

- `--output` or `-o`: Save the changes to a JSON file
  ```bash
  python -m doctracer.cli.track_changes old_gazette.json new_gazette.json --output changes.json
  ```

- `--summary-only`: Show only the summary of changes
  ```bash
  python -m doctracer.cli.track_changes old_gazette.json new_gazette.json --summary-only
  ```

### Gazette File Format

Gazette files should be in JSON format with the following structure:

```json
{
    "gazette_id": "2023-01",
    "published_date": "2023-01-01",
    "ministers": [
        {
            "name": "John Smith",
            "departments": ["Finance", "Education"],
            "laws": ["Law A", "Law B"],
            "functions": ["Budget Management", "Policy Development"]
        }
    ]
}
```

### Python API

You can also use the system programmatically:

```python
from doctracer.models.gazette import GazetteData, MinisterEntry
from doctracer.services.gazette_change_tracker import GazetteChangeTracker
from datetime import date

# Create gazette data
old_gazette = GazetteData(
    gazette_id="2023-01",
    published_date=date(2023, 1, 1),
    ministers=[
        MinisterEntry(
            name="John Smith",
            departments=["Finance", "Education"],
            laws=["Law A", "Law B"],
            functions=["Budget Management", "Policy Development"]
        )
    ]
)

new_gazette = GazetteData(
    gazette_id="2023-02",
    published_date=date(2023, 2, 1),
    ministers=[
        MinisterEntry(
            name="John Smith",
            departments=["Finance", "Education", "Technology"],
            laws=["Law A", "Law D"],
            functions=["Budget Management", "Digital Transformation"]
        )
    ]
)

# Track changes
tracker = GazetteChangeTracker()
changes = tracker.compare_gazettes(old_gazette, new_gazette)

# Access the changes
print(changes.summary)  # Get a human-readable summary
print(changes.dict())   # Get the full change data as a dictionary
```

### Change Types

The system tracks the following types of changes:

1. **Minister Changes**:
   - Added: New ministers appointed
   - Removed: Ministers removed from office
   - Modified: Changes in existing ministers' roles

2. **Department Changes**:
   - Added: New departments assigned
   - Removed: Departments removed
   - Modified: Changes in department assignments

3. **Law Changes**:
   - Added: New laws assigned
   - Removed: Laws removed
   - Modified: Changes in law assignments

4. **Function Changes**:
   - Added: New functions assigned
   - Removed: Functions removed
   - Modified: Changes in function assignments

### Example Output

The system generates both a summary and detailed changes:

```
Gazette Changes Summary:
=======================
Modified Minister: John Smith
  Department changes: Technology (added)
  Law changes: Law B (removed), Law D (added)
  Function changes: Policy Development (removed), Digital Transformation (added)
Removed Minister: Jane Doe
Added Minister: Robert Johnson

Detailed Changes:
================
Minister: John Smith
Change Type: modified

Department Changes:
- Technology: added
  New value: Technology

Law Changes:
- Law B: removed
  Old value: Law B
- Law D: added
  New value: Law D

Function Changes:
- Policy Development: removed
  Old value: Policy Development
- Digital Transformation: added
  New value: Digital Transformation
```

## Development

### Project Structure

```
doctracer/
├── models/
│   ├── gazette.py
│   └── gazette_change.py
├── services/
│   └── gazette_change_tracker.py
├── cli/
│   └── track_changes.py
└── examples/
    ├── track_gazette_changes.py
    ├── gazette_2023_01.json
    └── gazette_2023_02.json
```

### Running Tests

```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
