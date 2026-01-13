import typer
from rich.console import Console
from hydra import initialize, compose
from pathlib import Path

# Local imports
from src.train.pipeline import run_training
from src.eval.evaluator import run_evaluation
from src.deploy.push import push_model, push_model_local

app = typer.Typer(help="AnySecret-LLM CLI — manage training, evaluation, and publishing")
console = Console()

DEFAULT_CONFIG_NAME = "train"
#CONFIG_PATH = str(Path(__file__).resolve().parent.parent / "configs")
CONFIG_PATH = "../configs"


# === Commands ===

@app.command()
def train(config_name: str = DEFAULT_CONFIG_NAME):
    """Train a model using Hydra configuration"""
    console.rule("[bold cyan]Training Pipeline")
    with initialize(version_base=None, config_path=CONFIG_PATH):
        cfg = compose(config_name=config_name)
    console.print(f"[green]Using config:[/green] {config_name}")
    run_training(cfg)


@app.command()
def eval(config_name: str = DEFAULT_CONFIG_NAME):
    """Evaluate a trained model"""
    console.rule("[bold cyan]Evaluation Pipeline")
    with initialize(version_base=None, config_path=CONFIG_PATH):
        cfg = compose(config_name=config_name)
    console.print(f"[green]Using config:[/green] {config_name}")
    run_evaluation(cfg)


@app.command()
def publish(model_path: str = typer.Argument("outputs/runs/latest/model", help="Path to model directory")):
    """Publish trained model to local artifacts"""
    console.rule("[bold cyan]Local Publishing Pipeline")
    push_model_local(model_path)


@app.command("publish-hf")
def publish_hf(
    model_path: str = typer.Argument("outputs/runs/latest/model", help="Path to model directory"),
    repo_id: str = typer.Option(None, "--repo", "-r", help="HuggingFace repo ID (e.g., username/model-name)"),
    private: bool = typer.Option(True, "--private/--public", help="Create private repo"),
):
    """Publish trained model to HuggingFace Hub"""
    console.rule("[bold cyan]HuggingFace Publishing Pipeline")
    push_model(model_path, repo_id=repo_id, private=private)


@app.command("list-configs")
def list_configs():
    """List available Hydra configs"""
    conf_dir = Path(CONFIG_PATH)
    console.rule("[bold cyan]Available Configs")
    for path in conf_dir.rglob("*.yaml"):
        console.print(f"- {path.relative_to(conf_dir)}")


@app.command()
def version():
    """Show CLI version"""
    console.print("[bold magenta]AnySecret-LLM CLI v0.1[/bold magenta]")


if __name__ == "__main__":
    app()

