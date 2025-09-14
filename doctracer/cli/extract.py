import os
import click
from pathlib import Path
from doctracer.extract.gazette.extragazetteamendment import ExtraGazetteAmendmentProcessor

from doctracer.extract.gazette.extragazettetable import ExtraGazetteTableProcessor

PROCESSOR_TYPES = {
    'extragazette_amendment': ExtraGazetteAmendmentProcessor,
    'extragazette_table': ExtraGazetteTableProcessor,
    # Add more processor types here
}

@click.command()
@click.option(
    '--type',
    'processor_type',
    type=click.Choice(PROCESSOR_TYPES.keys()),
    required=True,
    help='Type of gazette processor to use'
)
@click.option(
    '--input',
    'input_path',
    type=click.Path(exists=True),
    required=True,
    help='Input PDF file or directory'
)
@click.option(
    '--output',
    'output_path',
    type=click.Path(),
    required=True,
    help='Output file path'
)
def extract(processor_type: str, input_path: str, output_path: str):
    """Extract information from gazette PDFs."""
    input_path = Path(input_path)
    
    # Initialize the appropriate processor class
    processor_class = PROCESSOR_TYPES[processor_type]

    # For 'extragazette_amendment', process a single file
    if processor_type == 'extragazette_amendment':
        if not input_path.is_file():
            raise click.BadParameter("Input must be a single PDF file for 'extragazette_amendment'")
        
        processor = processor_class(input_path)
        output: str = processor.process_gazettes()

        with open(output_path, 'w') as text_file:
            text_file.write(output)
        
        click.echo(f"✓ Processed. Results saved to {output_path}")

    # For 'extragazette_table', process all files in a directory
    elif processor_type == 'extragazette_table':
        if not input_path.is_file():
            raise click.BadParameter("Input must be a single PDF file for 'extragazette_table'")

        processor = processor_class(input_path)
        output: str = processor.process_gazettes()

        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(output)

        click.echo(f"✓ Processed. Results saved to {output_path}")
