import click
from doctracer.cli.extract import extract

@click.group()
def cli():
    """Doctracer command line interface."""
    pass

# Register subcommands
cli.add_command(extract, name='extract')

if __name__ == "__main__":
    cli()
