import os
import shutil
from pathlib import Path

from rich.console import Console

console = Console()

MODEL_CARD_TEMPLATE = Path(__file__).parent.parent.parent / "templates" / "MODEL_CARD.md"


def push_model(model_path: str, repo_id: str = None, private: bool = True):
    """
    Push merged model and GGUF to Hugging Face Hub.

    Args:
        model_path: Path to the run directory (e.g., outputs/runs/latest)
        repo_id: HuggingFace repo ID (e.g., 'username/model-name')
                 If not provided, uses HF_REPO_ID env var
        private: Whether to create a private repo (default: True)
    """
    console.rule("[bold magenta]Publishing to Hugging Face")

    src = Path(model_path)
    if not src.exists():
        console.print(f"[red]Model path not found:[/red] {src}")
        return False

    # Check for merged model directory
    merged_dir = src / "merged" if (src / "merged").exists() else src.parent / "merged"
    if not merged_dir.exists():
        console.print(f"[red]Merged model not found:[/red] {merged_dir}")
        console.print("[yellow]Run 'make merge' first to create merged model[/yellow]")
        return False

    # Get repo ID from argument or environment
    repo_id = repo_id or os.environ.get("HF_REPO_ID")
    if not repo_id:
        console.print("[red]Error:[/red] No repo_id provided and HF_REPO_ID not set")
        console.print("Set HF_REPO_ID environment variable or pass repo_id argument")
        return False

    # Check for HF token
    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not hf_token:
        console.print("[red]Error:[/red] HF_TOKEN not set")
        console.print("Set HF_TOKEN environment variable with your Hugging Face token")
        return False

    try:
        from huggingface_hub import HfApi, create_repo
        from transformers import AutoTokenizer
        from peft import PeftModel, PeftConfig
    except ImportError as e:
        console.print(f"[red]Missing dependency:[/red] {e}")
        console.print("Run: pip install huggingface_hub")
        return False

    console.print(f"[cyan]Model path:[/cyan] {src}")
    console.print(f"[cyan]Merged model:[/cyan] {merged_dir}")
    console.print(f"[cyan]Target repo:[/cyan] {repo_id}")

    try:
        # Create repo if it doesn't exist
        api = HfApi(token=hf_token)
        try:
            create_repo(repo_id, private=private, token=hf_token, exist_ok=True)
            console.print(f"[green]Repository ready:[/green] {repo_id}")
        except Exception as e:
            console.print(f"[yellow]Repo exists or error:[/yellow] {e}")

        # Copy model card to merged model directory if template exists
        readme_dest = merged_dir / "README.md"
        if MODEL_CARD_TEMPLATE.exists():
            shutil.copy(MODEL_CARD_TEMPLATE, readme_dest)
            console.print(f"[green]Added model card:[/green] {readme_dest}")

        # Upload the merged model directory (includes GGUF files if present)
        console.print("[yellow]Uploading merged model files...[/yellow]")

        # Check for GGUF files in merged directory
        gguf_files = list(merged_dir.glob("*.gguf"))
        if gguf_files:
            console.print(f"[cyan]Found {len(gguf_files)} GGUF file(s) in merged directory[/cyan]")
            for gguf_file in gguf_files:
                console.print(f"  - {gguf_file.name}")

        api.upload_folder(
            folder_path=str(merged_dir),
            repo_id=repo_id,
            token=hf_token,
            commit_message="Upload merged model and GGUF files from training pipeline",
        )

        console.print(f"[green]Successfully pushed to:[/green] https://huggingface.co/{repo_id}")
        console.rule("[bold magenta]Publishing Complete")
        return True

    except Exception as e:
        console.print(f"[red]Failed to push:[/red] {e}")
        return False


def push_model_local(model_path: str):
    """
    Copy model to local artifacts directory (for testing/backup).
    """
    import shutil

    console.rule("[bold magenta]Local Publishing")

    src = Path(model_path)
    if not src.exists():
        console.print(f"[red]Model path not found:[/red] {src}")
        return

    dest = Path("artifacts/models")
    dest.mkdir(parents=True, exist_ok=True)
    published = dest / src.name

    if src.is_dir():
        shutil.copytree(src, published, dirs_exist_ok=True)
    else:
        shutil.copy2(src, published)

    console.print(f"[green]Published model locally:[/green] {published}")
    console.rule("[bold magenta]Local Publishing Complete")
