import typer

app = typer.Typer(help="Mason CLI - A command line interface for managing Mason projects.")

@app.command()
def create_controller(name: str):
    """
    Create a new controller with the given NAME.
    """
    typer.echo(f"Creating controller: {name}")
    # Logic to create a controller would go here

@app.command()
def run():
    """
    Run the Mason application.
    """
    typer.echo("Running the Mason application...")
    # Logic to run the application would go here


if __name__ == "__main__":
    app()