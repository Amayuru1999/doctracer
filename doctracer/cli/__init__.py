import click
from doctracer.cli.extract import extract, compare
# from doctracer.cli.run import run  # Uncomment when ready

@click.group()
def cli():
    """Doctracer command line interface."""
    pass

# Register CLI subcommands
cli.add_command(extract, name='extract')
cli.add_command(compare, name='compare')
# cli.add_command(run, name='run')  # Uncomment when implemented

if __name__ == "__main__":
    cli()
