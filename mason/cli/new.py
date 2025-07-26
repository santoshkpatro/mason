import typer
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent / "templates" / "new"

def create_new_project():
    project_path_input = typer.prompt("Enter project path (default: current directory)", default=".")
    project_path = Path(project_path_input).resolve()

    project_name = typer.prompt("Enter project name")
    author_name = typer.prompt("Enter author name")

    directories = [
        "app/commands", "app/controllers", "app/jobs", "app/models",
        "app/serializers", "app/services", "app/static", "app/views",
        "config/migrations", "public", "tests"
    ]
    for directory in directories:
        (project_path / directory).mkdir(parents=True, exist_ok=True)

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    render_template(env, "launch.py.tpl", project_path / "launch.py", project_name, author_name)
    render_template(env, "settings.py.tpl", project_path / "config/settings.py", project_name, author_name)
    render_template(env, "home_controller.py.tpl", project_path / "app/controllers/home_controller.py", project_name, author_name)

    typer.echo(f"✅ Mason project '{project_name}' created at {project_path}")

def render_template(env, template_name, output_path, project_name, author_name):
    template = env.get_template(template_name)
    content = template.render(project_name=project_name, author_name=author_name)
    output_path.write_text(content)
