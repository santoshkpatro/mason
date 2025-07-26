import typer
from pathlib import Path
import subprocess
from jinja2 import Environment, FileSystemLoader

project_cli = typer.Typer(help="Mason Project CLI")

TEMPLATE_DIR = Path(__file__).parent / "templates" / "project"

@project_cli.command("generate")
def generate(resource: str, name: str):
    """
    Generate resources like controllers, models, etc.
    Example: python launch.py generate controller items
    """
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

    if resource == "controller":
        class_name = name.capitalize()
        output_path = Path("app/controllers") / f"{name.lower()}_controller.py"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        template = env.get_template("controller.py.tpl")
        content = template.render(name=name.lower(), class_name=class_name)

        output_path.write_text(content)
        typer.secho(f"✅ Controller created at {output_path}", fg=typer.colors.GREEN)

    else:
        typer.secho(f"❌ Unsupported resource: {resource}", fg=typer.colors.RED)


@project_cli.command("runserver")
def runserver(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    """
    Start the Mason development server.
    Example: python launch.py runserver --host 0.0.0.0 --port 8080
    """
    typer.secho(f"🚀 Starting Mason server at http://{host}:{port}", fg=typer.colors.GREEN)
    cmd = [
        "uvicorn",
        "launch:app",  # The app object in launch.py
        "--host", host,
        "--port", str(port)
    ]
    if reload:
        cmd.append("--reload")
    subprocess.run(cmd)

