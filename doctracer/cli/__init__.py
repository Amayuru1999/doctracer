import click
from doctracer.cli.extract import extract
from doctracer.cli.track import track

@click.group()
def cli():
    """Doctracer command line interface."""
    pass

# Register subcommands
cli.add_command(extract, name='extract')
cli.add_command(track,   name='track')

if __name__ == "__main__":
    cli()
