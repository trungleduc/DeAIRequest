import pkg_resources
import click


@click.command()
def version():
    """Prints the version of this build."""

    try:
        click.echo(pkg_resources.get_distribution("bacalhauconnector").version+" BH")
    except Exception as e:
        click.echo(f"Unknown version (error getting version: {e})")

