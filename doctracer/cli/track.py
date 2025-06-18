
import click
import json
from doctracer.extract.gazette.diff import GazetteDiffProcessor
from doctracer.neo4j_interface import Neo4jInterface


@click.command("track")
@click.option("--old",     type=click.Path(exists=False), required=False, help="Path to old gazette JSON")
@click.option("--new",     type=click.Path(exists=True), required=True, help="Path to new gazette JSON")
@click.option("--output",  type=click.Path(),            help="Save diff JSON to this file")
@click.option("--to-neo4j/--no-neo4j", default=False,   help="Also push changes to Neo4j")
def track(old, new, output, to_neo4j):
    """
    Compare two gazette JSON files and optionally persist the diffs to Neo4j.
    """
    # 1. Load JSON blobs
    old_json = open(old, "r").read()
    new_json = open(new, "r").read()

    # 2. Compute diffs
    changes = GazetteDiffProcessor.diff(old_json, new_json)

    # 3. Write or print
    if output:
        with open(output, "w") as f:
            json.dump(changes, f, indent=2)
        click.echo(f"Wrote {len(changes)} changes to {output}")
    else:
        for c in changes:
            click.echo(c)

    # 4. Optionally push to Neo4j
    if to_neo4j:
        neo = Neo4jInterface()
        for c in changes:
            neo.create_change_event(c)
        neo.close()
        click.echo("Pushed changes to Neo4j")
