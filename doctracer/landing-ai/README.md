# Government Gazette Structure Analyzer

A Python application that uses Landing AI to extract information from government gazettes and show the current government structure by comparing a base gazette with an amendment gazette.

## Features

- **PDF Processing**: Uses Landing AI's `agentic_doc` library to extract structured content from PDF gazettes
- **Government Structure Analysis**: Identifies ministers, state ministers, departments, laws, and functions
- **Amendment Processing**: Applies amendments to base gazettes to show current government structure
- **Multiple Interfaces**: Command-line tool and web interface
- **Comprehensive Reporting**: Generates detailed reports in JSON and Markdown formats
- **Visual Output**: Creates annotated images showing document structure

## Prerequisites

1. **Landing AI API Key**: You need a valid Landing AI API key
2. **Python Dependencies**: Install required packages
3. **PDF Files**: Base and amendment government gazettes in PDF format

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   cd doctracer/landing-ai
   ```

2. **Install dependencies**:
   ```bash
   pip install -r ../../requirements.txt
   pip install agentic-doc flask flask-cors
   ```

3. **Set up environment variables**:
   Create a `.env` file in the landing-ai directory:
   ```bash
   VISION_AGENT_API_KEY=your_landing_ai_api_key_here
   ```

## Usage

### Command Line Interface

#### Basic Usage
```bash
python gazette_structure_analyzer.py base_gazette.pdf amendment_gazette.pdf
```

#### With Custom API Key
```bash
python gazette_structure_analyzer.py base_gazette.pdf amendment_gazette.pdf --api-key your_api_key
```

#### With Custom Output Directory
```bash
python gazette_structure_analyzer.py base_gazette.pdf amendment_gazette.pdf --output-dir /path/to/output
```

### Web Interface

1. **Start the web server**:
   ```bash
   python web_interface.py
   ```

2. **Open your browser** and go to `http://localhost:5000`

3. **Upload files**:
   - Drag and drop or click to select your base gazette PDF
   - Drag and drop or click to select your amendment gazette PDF
   - Click "Analyze Government Structure"

4. **View results**:
   - Summary cards showing gazette information
   - Current government structure with ministers and state ministers
   - Download detailed results as JSON

### Example Usage

Run the example with existing gazette files:
```bash
python example_usage.py
```

This will process the sample gazettes in the `data/` directory and show you the current government structure.

## File Structure

```
landing-ai/
├── gazette_structure_analyzer.py    # Main command-line tool
├── web_interface.py                 # Flask web application
├── example_usage.py                 # Example usage script
├── templates/
│   └── index.html                   # Web interface template
├── data/                            # Sample gazette files
│   ├── 2289-43_E_2022_07_22.pdf    # Base gazette
│   └── 2297-78_E_2022_09_16.pdf    # Amendment gazette
├── output/                          # Generated output files
├── uploads/                         # Uploaded files (web interface)
└── README.md                        # This file
```

## Output Files

The analyzer generates several output files:

1. **`base_gazette_data.json`**: Extracted data from the base gazette
2. **`amendment_gazette_data.json`**: Extracted data from the amendment gazette
3. **`current_government_structure.json`**: Current structure after applying amendments
4. **`government_structure_report.md`**: Human-readable report in Markdown format
5. **Visual annotations**: Images showing document structure (in output directory)

## Data Structure

### Gazette Structure
```json
{
  "metadata": {
    "gazette_id": "2289/43",
    "published_date": "2022-07-22",
    "published_by": "Authority"
  },
  "structure": {
    "ministers": [
      {
        "name": "Minister of Finance",
        "departments": ["Department of Treasury", "Central Bank"],
        "laws": ["Finance Act", "Banking Act"],
        "functions": ["Budget management", "Financial regulation"],
        "purview": "Financial and economic policy",
        "special_priorities": ["Economic stability", "Growth"]
      }
    ],
    "state_ministers": [...],
    "departments": {...},
    "laws": {...}
  }
}
```

### Amendment Operations
The system recognizes these amendment types:
- **DELETE**: Remove a minister or department
- **INSERT**: Add a new minister or department
- **RENUMBER**: Change heading numbers
- **UPDATE**: Modify existing content

## API Endpoints (Web Interface)

- `GET /`: Main page
- `POST /upload`: Upload and process gazettes
- `GET /results/<filename>`: Download analysis results
- `GET /health`: Health check

## Troubleshooting

### Common Issues

1. **API Key Error**:
   ```
   ValueError: API key is not set. Please provide a valid VISION_AGENT_API_KEY.
   ```
   **Solution**: Set the `VISION_AGENT_API_KEY` environment variable

2. **File Not Found**:
   ```
   FileNotFoundError: [Errno 2] No such file or directory
   ```
   **Solution**: Check that the PDF files exist and are readable

3. **Import Error**:
   ```
   ModuleNotFoundError: No module named 'agentic_doc'
   ```
   **Solution**: Install the required dependencies:
   ```bash
   pip install agentic-doc
   ```

4. **Processing Error**:
   ```
   Error extracting content: Invalid PDF or corrupted file
   ```
   **Solution**: Ensure the PDF files are valid and not corrupted

### Performance Tips

- **Large Files**: Processing large PDF files may take several minutes
- **Memory Usage**: The system loads entire PDFs into memory
- **API Limits**: Be aware of Landing AI API rate limits

## Development

### Adding New Features

1. **New Amendment Types**: Extend the `_extract_amendment_operations` method
2. **Additional Metadata**: Modify the `_extract_metadata` method
3. **Custom Output Formats**: Add new methods to the `GazetteStructureAnalyzer` class

### Testing

Test with the provided sample files:
```bash
python example_usage.py
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Doctracer system. See the main LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the example usage
3. Check the Landing AI documentation for API details
4. Open an issue in the repository

## Acknowledgments

- Landing AI for providing the document processing capabilities
- The Doctracer team for the overall project structure
- Government of Sri Lanka for the sample gazette documents
