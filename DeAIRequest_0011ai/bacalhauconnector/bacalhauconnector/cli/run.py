from bacalhauconnector.ops.runtime_options import validate_options, runtime_options, get_option_value
from bacalhauconnector.data.config import SameConfig
from io import BufferedReader
from pathlib import Path
import bacalhauconnector.ops.notebooks as notebooks
import bacalhauconnector.ops.backends as backends
import click


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.option(
    "-f",
    "--same-file",
    "same_file",
    default="same.yaml",
    show_default=True,
    type=click.File("r"),
    help="Path to SAME configuration file.",
)
@click.option(
    "-t",
    "--target",
    default="kubeflow",
    type=click.Choice(["aml", "kubeflow", "functions", "pachyderm", "bacalhau"]),
)
@click.option(
    "--persist-temp-files",
    "persist_temp_files",
    default=False,
    is_flag=True,
    type=bool,
    help="Persist compilation artifacts.",
)
@click.option(
    "--no-deploy",
    "no_deploy",
    default=False,
    is_flag=True,
    type=bool,
    help="Do not deploy compiled pipelines.",
)
@runtime_options
def run(
    target: str,
    same_file: BufferedReader,
    no_deploy: bool = False,
    persist_temp_files: bool = False,  # TODO: remove this
):
    """Compiles and deploys a pipeline from a SAME config file."""
    # Validate runtime options against the configured backend:
   
    try:
        validate_options(target)
    except SyntaxError as e:
        # Cerberus already prints out all the errors, so we just need to return if there's a Syntax Error
        return

    # TODO: Make SAME config object immutable (frozen_box=True).
    same_file_content = same_file.read()
    filepath = Path(same_file.name)
    if filepath.suffix == ".ipynb":
        config = SameConfig.from_ipynb(same_file_content, filepath, frozen_box=False)
    else:
        config = SameConfig.from_yaml(same_file_content, frozen_box=False)
    config = config.resolve(filepath.parent)
    config = config.inject_runtime_options()

    click.echo(f"Loading SAME config: {same_file.name}")
    base_path, root_file = notebooks.compile(config, target)
    if persist_temp_files:
        click.echo(f"Temporary files persisted here: {base_path}")

    if not no_deploy:
        # try:
        backends.deploy(target, base_path, root_file, config)
        # except Exception as err:
        #     click.echo(err, err=True)
        #     exit(1)
