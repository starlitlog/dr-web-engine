import os
import subprocess
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from datasets import load_dataset
from omegaconf import DictConfig
from rich.console import Console

from src.utils.environment import get_default_data_source_type

console = Console()


class DataSource(ABC):
    """Abstract base class for data sources."""
    
    @abstractmethod
    def load_dataset(self, pattern: Optional[str] = None):
        """Load dataset from the data source."""
        pass


class LocalDataSource(DataSource):
    """Local filesystem data source."""

    def __init__(self, path: str, data_format: str = "prompt_completion"):
        self.path = path
        self.data_format = data_format

    def load_dataset(self, pattern: Optional[str] = None, config=None):
        """Load dataset from local filesystem."""
        from datasets import load_from_disk
        from pathlib import Path

        # Check if we should use pre-tokenized data
        use_tokenized = config.get("use_tokenized", True) if config else True
        tokenized_path = config.get("tokenized_path") if config else None

        if use_tokenized and tokenized_path:
            tokenized_dataset_path = Path(tokenized_path)
            if tokenized_dataset_path.exists() and (tokenized_dataset_path / "dataset_info.json").exists():
                # Pre-tokenized dataset exists
                console.print(f"[green]Loading pre-tokenized dataset from:[/green] {tokenized_path}")
                return load_from_disk(str(tokenized_dataset_path))
            else:
                console.print(f"[yellow]Warning:[/yellow] Tokenized dataset not found at {tokenized_path}")
                console.print(f"[yellow]Falling back to raw JSONL. Run 'make tokenize' to speed up training.[/yellow]")

        # Load raw JSONL files
        from .loader import load_jsonl_dataset
        return load_jsonl_dataset(self.path, pattern, data_format=self.data_format)


class LakeFSDataSource(DataSource):
    """LakeFS data source that downloads files to temp directory."""
    
    def __init__(self, config: DictConfig):
        self.endpoint = config.get("endpoint", "http://localhost:8000")
        self.repo = config.repo
        self.branch = config.branch
        self.path = config.get("path", "")
        self.access_key = config.get("access_key") or os.getenv("LAKEFS_ACCESS_KEY")
        self.secret_key = config.get("secret_key") or os.getenv("LAKEFS_SECRET_KEY")
        
        # Validate required config
        if not self.repo or not self.branch:
            raise ValueError("LakeFS repo and branch are required")
    
    def _setup_lakectl_config(self):
        """Configure lakectl with credentials if provided."""
        if self.access_key and self.secret_key:
            # Configure lakectl
            subprocess.run([
                "lakectl", "config", "set", "credentials.access_key_id", self.access_key
            ], check=True, capture_output=True)
            subprocess.run([
                "lakectl", "config", "set", "credentials.secret_access_key", self.secret_key
            ], check=True, capture_output=True)
        
        if self.endpoint != "http://localhost:8000":
            subprocess.run([
                "lakectl", "config", "set", "server.endpoint_url", self.endpoint
            ], check=True, capture_output=True)
    
    def _list_lakefs_files(self, pattern: Optional[str] = None) -> List[str]:
        """List files in LakeFS that match the pattern."""
        lakefs_path = f"lakefs://{self.repo}/{self.branch}/{self.path}".rstrip("/") + "/"
        
        try:
            result = subprocess.run([
                "lakectl", "fs", "ls", lakefs_path
            ], capture_output=True, text=True, check=True)
            
            files = []
            for line in result.stdout.strip().split('\n'):
                if line and not line.startswith('object'):  # Skip header
                    # Parse lakectl ls output format
                    parts = line.strip().split()
                    if parts and parts[0].startswith('lakefs://'):
                        file_path = parts[0]
                        filename = file_path.split('/')[-1]
                        
                        # Apply pattern filter
                        if pattern:
                            if pattern == "*.jsonl" and filename.endswith('.jsonl'):
                                files.append(file_path)
                            elif filename.endswith(pattern.replace("*", "")):
                                files.append(file_path)
                        else:
                            files.append(file_path)
            
            return files
            
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to list LakeFS files:[/red] {e.stderr}")
            raise
    
    def _download_file(self, lakefs_path: str, local_path: Path):
        """Download a single file from LakeFS."""
        try:
            subprocess.run([
                "lakectl", "fs", "download", lakefs_path, str(local_path)
            ], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to download {lakefs_path}:[/red] {e.stderr}")
            raise
    
    def load_dataset(self, pattern: Optional[str] = None):
        """Download files from LakeFS to temp directory and load dataset."""
        self._setup_lakectl_config()
        
        console.print(f"[cyan]Listing files from LakeFS:[/cyan] {self.repo}/{self.branch}/{self.path}")
        lakefs_files = self._list_lakefs_files(pattern)
        
        if not lakefs_files:
            raise FileNotFoundError(f"No files found in LakeFS path: {self.repo}/{self.branch}/{self.path}")
        
        console.print(f"[green]Found {len(lakefs_files)} files in LakeFS[/green]")
        
        # Create temporary directory for downloaded files
        temp_dir = Path(tempfile.mkdtemp(prefix="lakefs_data_"))
        local_files = []
        
        try:
            for lakefs_file in lakefs_files:
                filename = lakefs_file.split('/')[-1]
                local_file = temp_dir / filename
                
                console.print(f"[yellow]Downloading:[/yellow] {filename}")
                self._download_file(lakefs_file, local_file)
                local_files.append(str(local_file))
            
            # Load dataset from downloaded files
            console.print(f"[green]Loading dataset from {len(local_files)} files[/green]")
            dataset = load_dataset("json", data_files=local_files)
            return dataset["train"]
            
        except Exception as e:
            # Cleanup temp directory on error
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e


class DataSourceFactory:
    """Factory for creating data sources based on configuration."""
    
    @staticmethod
    def create_data_source(config: DictConfig) -> DataSource:
        """Create appropriate data source based on config."""
        data_source_config = config.get("data_source", {})
        
        # Auto-detect source type if not specified
        source_type = data_source_config.get("type")
        if not source_type:
            source_type = get_default_data_source_type()
            console.print(f"[yellow]Auto-detected data source type:[/yellow] {source_type}")
        
        if source_type == "lakefs":
            lakefs_config = data_source_config.get("lakefs", {})
            if not lakefs_config:
                raise ValueError("LakeFS configuration required when data_source.type=lakefs")
            return LakeFSDataSource(lakefs_config)
        elif source_type == "local":
            # Fallback to existing dataset_path for backward compatibility
            dataset_path = config.get("dataset_path", "./data")
            data_format = config.get("data_format", "prompt_completion")
            return LocalDataSource(dataset_path, data_format=data_format)
        else:
            raise ValueError(f"Unsupported data source type: {source_type}. Supported types: local, lakefs")