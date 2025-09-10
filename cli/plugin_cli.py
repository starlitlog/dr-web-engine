"""
Plugin Management CLI Commands for DR Web Engine
"""

import typer
import json
import sys
import subprocess
import logging
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from engine.web_engine.plugin_discovery import PluginDiscovery
from engine.web_engine.plugin_manager import PluginManager
from engine.web_engine.processors import StepProcessorRegistry

console = Console()
logger = logging.getLogger(__name__)

# Create plugin CLI app
plugin_app = typer.Typer(
    name="plugin",
    help="Manage DR Web Engine plugins",
    rich_markup_mode="rich"
)


@plugin_app.command("list")
def list_plugins(
    installed_only: bool = typer.Option(False, "--installed-only", "-i", help="Show only installed plugins"),
    enabled_only: bool = typer.Option(False, "--enabled-only", "-e", help="Show only enabled plugins"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON")
):
    """List available plugins."""
    try:
        # Create temporary components to discover plugins
        registry = StepProcessorRegistry()
        manager = PluginManager(registry)
        
        # Discover plugins without auto-loading
        manager.discover_and_load_plugins(auto_load=False)
        plugins = manager.list_plugins()
        
        if not plugins:
            console.print("[yellow]No plugins found.[/yellow]")
            return
        
        # Filter plugins
        if installed_only:
            plugins = {k: v for k, v in plugins.items() if v["status"] in ["loaded", "available"]}
        
        if enabled_only:
            plugins = {k: v for k, v in plugins.items() if v["enabled"]}
        
        if json_output:
            console.print(json.dumps(plugins, indent=2))
            return
        
        # Create rich table
        table = Table(title="DR Web Engine Plugins")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Version", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Processors", justify="right", style="blue")
        table.add_column("Description", style="white")
        
        for name, info in sorted(plugins.items()):
            status_color = {
                "loaded": "green",
                "available": "yellow", 
                "disabled": "red"
            }.get(info["status"], "white")
            
            table.add_row(
                name,
                info["version"],
                f"[{status_color}]{info['status']}[/{status_color}]",
                str(info["processors"]),
                info["description"][:60] + "..." if len(info["description"]) > 60 else info["description"]
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error listing plugins: {e}[/red]")
        sys.exit(1)


@plugin_app.command("info")
def plugin_info(
    plugin_name: str = typer.Argument(..., help="Name of the plugin"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON")
):
    """Show detailed information about a plugin."""
    try:
        registry = StepProcessorRegistry()
        manager = PluginManager(registry)
        
        info = manager.get_plugin_info(plugin_name)
        if not info:
            console.print(f"[red]Plugin '{plugin_name}' not found.[/red]")
            sys.exit(1)
        
        if json_output:
            console.print(json.dumps(info, indent=2))
            return
        
        # Create rich panel with plugin info
        content = []
        content.append(f"[cyan]Name:[/cyan] {info['name']}")
        content.append(f"[cyan]Version:[/cyan] {info['version']}")
        content.append(f"[cyan]Author:[/cyan] {info['author']}")
        content.append(f"[cyan]Status:[/cyan] {info.get('status', 'unknown')}")
        content.append(f"[cyan]Enabled:[/cyan] {info.get('enabled', 'unknown')}")
        
        if info.get('homepage'):
            content.append(f"[cyan]Homepage:[/cyan] {info['homepage']}")
        
        content.append(f"[cyan]Description:[/cyan] {info['description']}")
        
        if info.get('supported_step_types'):
            types = ", ".join(info['supported_step_types'])
            content.append(f"[cyan]Supported Steps:[/cyan] {types}")
        
        if info.get('dependencies'):
            deps = ", ".join(info['dependencies'])
            content.append(f"[cyan]Dependencies:[/cyan] {deps}")
        
        content.append(f"[cyan]Min DR Web Version:[/cyan] {info.get('min_drweb_version', 'unknown')}")
        
        if info.get('processors'):
            content.append(f"[cyan]Processors:[/cyan] {len(info['processors'])}")
            for i, proc in enumerate(info['processors'], 1):
                content.append(f"  {i}. {proc['name']} (priority: {proc['priority']})")
        
        panel = Panel("\n".join(content), title=f"Plugin: {plugin_name}", border_style="blue")
        console.print(panel)
        
    except Exception as e:
        console.print(f"[red]Error getting plugin info: {e}[/red]")
        sys.exit(1)


@plugin_app.command("install")
def install_plugin(
    plugin_spec: str = typer.Argument(..., help="Plugin to install (name, git url, or local path)"),
    upgrade: bool = typer.Option(False, "--upgrade", "-U", help="Upgrade if already installed"),
    force: bool = typer.Option(False, "--force", help="Force installation")
):
    """Install a plugin."""
    try:
        console.print(f"Installing plugin: [cyan]{plugin_spec}[/cyan]")
        
        # Determine installation method
        if plugin_spec.startswith(("http://", "https://", "git+")):
            # Git URL
            cmd = ["pip", "install"]
            if upgrade:
                cmd.append("--upgrade")
            if force:
                cmd.append("--force-reinstall")
            cmd.append(plugin_spec)
        elif plugin_spec.startswith(("./", "/", "~/")):
            # Local path
            cmd = ["pip", "install"]
            if upgrade:
                cmd.append("--upgrade")
            if force:
                cmd.append("--force-reinstall")
            cmd.extend(["-e", plugin_spec])
        else:
            # PyPI package name
            cmd = ["pip", "install"]
            if upgrade:
                cmd.append("--upgrade")
            if force:
                cmd.append("--force-reinstall")
            cmd.append(plugin_spec)
        
        # Execute pip install
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(f"[green]Successfully installed: {plugin_spec}[/green]")
            console.print("\n[yellow]Note:[/yellow] Restart DR Web Engine to load the new plugin.")
        else:
            console.print(f"[red]Installation failed:[/red]")
            console.print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error installing plugin: {e}[/red]")
        sys.exit(1)


@plugin_app.command("uninstall")
def uninstall_plugin(
    plugin_name: str = typer.Argument(..., help="Name of plugin to uninstall"),
    force: bool = typer.Option(False, "--force", help="Force uninstallation")
):
    """Uninstall a plugin."""
    try:
        if not force:
            confirmed = typer.confirm(f"Are you sure you want to uninstall '{plugin_name}'?")
            if not confirmed:
                console.print("Uninstallation cancelled.")
                return
        
        console.print(f"Uninstalling plugin: [cyan]{plugin_name}[/cyan]")
        
        # Execute pip uninstall
        cmd = ["pip", "uninstall", "-y", plugin_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(f"[green]Successfully uninstalled: {plugin_name}[/green]")
        else:
            console.print(f"[red]Uninstallation failed:[/red]")
            console.print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error uninstalling plugin: {e}[/red]")
        sys.exit(1)


@plugin_app.command("enable")
def enable_plugin(
    plugin_name: str = typer.Argument(..., help="Name of plugin to enable")
):
    """Enable a disabled plugin."""
    try:
        registry = StepProcessorRegistry()
        manager = PluginManager(registry)
        
        if manager.enable_plugin(plugin_name):
            console.print(f"[green]Enabled plugin: {plugin_name}[/green]")
        else:
            console.print(f"[red]Failed to enable plugin: {plugin_name}[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error enabling plugin: {e}[/red]")
        sys.exit(1)


@plugin_app.command("disable")
def disable_plugin(
    plugin_name: str = typer.Argument(..., help="Name of plugin to disable")
):
    """Disable a plugin."""
    try:
        registry = StepProcessorRegistry()
        manager = PluginManager(registry)
        
        if manager.disable_plugin(plugin_name):
            console.print(f"[yellow]Disabled plugin: {plugin_name}[/yellow]")
        else:
            console.print(f"[red]Failed to disable plugin: {plugin_name}[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error disabling plugin: {e}[/red]")
        sys.exit(1)


@plugin_app.command("reload")
def reload_plugin(
    plugin_name: str = typer.Argument(..., help="Name of plugin to reload")
):
    """Reload a plugin."""
    try:
        registry = StepProcessorRegistry()
        manager = PluginManager(registry)
        
        if manager.reload_plugin(plugin_name):
            console.print(f"[green]Reloaded plugin: {plugin_name}[/green]")
        else:
            console.print(f"[red]Failed to reload plugin: {plugin_name}[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error reloading plugin: {e}[/red]")
        sys.exit(1)


@plugin_app.command("search")
def search_plugins(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum results to show")
):
    """Search for plugins (placeholder - would integrate with plugin registry)."""
    console.print(f"[yellow]Searching for plugins matching: {query}[/yellow]")
    console.print("[blue]Note:[/blue] Plugin search will be implemented in a future version.")
    console.print("For now, you can:")
    console.print("- Browse PyPI for packages starting with 'drweb-plugin-'")
    console.print("- Check the DR Web Engine documentation for recommended plugins")
    console.print("- Visit community repositories and forums")


@plugin_app.command("create")
def create_plugin_template(
    name: str = typer.Argument(..., help="Plugin name"),
    directory: Optional[str] = typer.Option(None, "--dir", help="Directory to create plugin in")
):
    """Create a plugin template (placeholder for future implementation)."""
    console.print(f"[yellow]Creating plugin template: {name}[/yellow]")
    console.print("[blue]Note:[/blue] Plugin template creation will be implemented in a future version.")
    console.print("For now, you can:")
    console.print("- Check the documentation for plugin development guide")
    console.print("- Look at existing plugins as examples")
    console.print("- Use the AI-Selector plugin as a reference implementation")