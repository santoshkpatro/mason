__VERSION__ = "0.0.1"
import typer


def show_version():
    """
    Show the Mason framework version.
    """
    typer.secho(f"Mason v{__VERSION__}", fg=typer.colors.GREEN)