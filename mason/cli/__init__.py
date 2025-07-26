import typer
from mason.cli.new import create_new_project
from mason.cli.version import show_version


app = typer.Typer(help="Mason CLI - Manage Mason projects")

@app.command("version")
def version():
    show_version()

@app.command("new")
def new():
    create_new_project()
