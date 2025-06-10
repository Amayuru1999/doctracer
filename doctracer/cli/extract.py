import os
import click
from pathlib import Path
from doctracer.extract.gazette.extragazetteamendment import ExtraGazetteAmendmentProcessor
from doctracer.extract.gazette.extragazettetable import ExtraGazetteTableProcessor

# === Available processors ===
PROCESSOR_TYPES = {
    'extragazette_amendment': ExtraGazetteAmendmentProcessor,
    'extragazette_table': ExtraGazetteTableProcessor,
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
    processor_class = PROCESSOR_TYPES[processor_type]

    if processor_type == 'extragazette_amendment':
        if not input_path.is_file():
            raise click.BadParameter("Input must be a single PDF file for 'extragazette_amendment'")

        processor = processor_class(input_path)
        output: str = processor.process_gazettes()

        with open(output_path, 'w') as text_file:
            text_file.write(output)

        click.echo(f"✓ Processed. Results saved to {output_path}")

    elif processor_type == 'extragazette_table':
        if not input_path.is_dir():
            raise click.BadParameter("Input must be a directory for 'extragazette_table'")

        image_filenames = sorted(
            [f for f in os.listdir(input_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        )

        results = {}

        for image_filename in image_filenames:
            print(f"Processing file: {os.path.join(input_path, image_filename)}\n")
            processor = processor_class(os.path.join(input_path, image_filename))
            results[image_filename] = processor.process_gazettes()

        with open(output_path, 'w', encoding='utf-8') as file:
            for image, response in results.items():
                file.write(f"{response}\n\n")

        click.echo(f"✓ Processed all files in the directory. Results saved to {output_path}")


@click.command()
@click.option("--old", "old_file", required=True, type=click.Path(exists=True))
@click.option("--new", "new_file", required=True, type=click.Path(exists=True))
@click.option("--output", "output_file", required=True, type=click.Path())
def compare(old_file, new_file, output_file):
    """Compare two gazette JSON files and output structured changes."""
    from doctracer.extract.gazette.change_tracker import load_gazette, compare_gazettes, save_diff
    old_data = load_gazette(old_file)
    new_data = load_gazette(new_file)
    changes = compare_gazettes(old_data, new_data)
    save_diff(changes, output_file)
    click.echo(f"✓ Comparison complete. Changes saved to {output_file}")
