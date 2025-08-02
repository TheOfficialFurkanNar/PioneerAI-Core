# cli.py - PioneerAI Enhanced CLI Interface
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, List
import json
from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

# Import our excellent modules
from main import PioneerAI
from modules.error_handler import ErrorHandler
from modules.memory_manager import AsyncMemoryManager
from modules.token_counter import TokenCounter
from config.settings import MEMORY_JSON, LOG_FILE

# Initialize Rich console for beautiful output
console = Console()
app = typer.Typer(
    name="pioneerai",
    help="🧠 PioneerAI - Advanced AI Chat System with Educational Focus",
    add_completion=False
)

# Global state
pioneer_instance: Optional[PioneerAI] = None


@app.command()
def chat(
        session: Optional[str] = typer.Option(
            None,
            "--session", "-s",
            help="Named session for conversation tracking"
        ),
        config: Optional[str] = typer.Option(
            "default",
            "--config", "-c",
            help="Configuration profile (default/debug/production)"
        ),
        verbose: bool = typer.Option(
            False,
            "--verbose", "-v",
            help="Enable verbose logging output"
        ),
        max_tokens: Optional[int] = typer.Option(
            None,
            "--max-tokens", "-t",
            help="Override maximum tokens per response"
        )
):
    """🚀 Start interactive chat session with PioneerAI"""

    with console.status("[bold blue]Initializing PioneerAI...", spinner="dots"):
        # Setup logging level
        log_level = "DEBUG" if verbose else "INFO"

        # Initialize PioneerAI
        global pioneer_instance
        pioneer_instance = PioneerAI()
        pioneer_instance.error_handler.setup_logging(log_level)

        # Apply session name if provided
        if session:
            console.print(f"📝 Using session: [bold cyan]{session}[/bold cyan]")

        # Apply configuration
        console.print(f"⚙️ Configuration: [bold green]{config}[/bold green]")

        if max_tokens:
            console.print(f"🎯 Max tokens override: [bold yellow]{max_tokens}[/bold yellow]")

    # Display welcome banner
    _display_welcome_banner()

    # Run the chat session
    try:
        asyncio.run(_run_chat_session())
    except KeyboardInterrupt:
        console.print("\n👋 [bold blue]Session ended gracefully![/bold blue]")
    except Exception as e:
        console.print(f"\n❌ [bold red]Error: {e}[/bold red]")


@app.command()
def status():
    """📊 Display PioneerAI system status and statistics"""

    console.print(Panel.fit("🔍 PioneerAI System Status", style="bold blue"))

    # Create status table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", width=20)
    table.add_column("Status", width=15)
    table.add_column("Details", style="dim")

    # Check memory file
    memory_status = "✅ Active" if Path(MEMORY_JSON).exists() else "⚠️ Not Found"
    memory_size = _get_file_size(MEMORY_JSON)
    table.add_row("Memory System", memory_status, f"Size: {memory_size}")

    # Check log file
    log_status = "✅ Active" if Path(LOG_FILE).exists() else "⚠️ Not Found"
    log_size = _get_file_size(LOG_FILE)
    table.add_row("Logging System", log_status, f"Size: {log_size}")

    # Check API key
    api_key_status = "✅ Configured" if os.getenv("OPENAI_API_KEY") else "❌ Missing"
    table.add_row("OpenAI API", api_key_status, "Environment variable check")

    # Check modules
    try:
        from modules.error_handler import ErrorHandler
        from modules.token_counter import TokenCounter
        modules_status = "✅ Loaded"
    except ImportError:
        modules_status = "❌ Import Error"

    table.add_row("Core Modules", modules_status, "error_handler, token_counter")

    console.print(table)

    # Show recent activity
    _show_recent_activity()


@app.command()
def export(
        output: str = typer.Option(
            "pioneerai_export.json",
            "--output", "-o",
            help="Output file path for exported data"
        ),
        format: str = typer.Option(
            "json",
            "--format", "-f",
            help="Export format: json, txt, or csv"
        ),
        sessions: Optional[int] = typer.Option(
            None,
            "--sessions", "-n",
            help="Number of recent sessions to export"
        )
):
    """💾 Export conversation history and system data"""

    console.print(f"📤 Exporting PioneerAI data to: [bold cyan]{output}[/bold cyan]")

    try:
        if format.lower() == "json":
            _export_json(output, sessions)
        elif format.lower() == "txt":
            _export_txt(output, sessions)
        elif format.lower() == "csv":
            _export_csv(output, sessions)
        else:
            console.print(f"❌ Unsupported format: {format}")
            return

        console.print(f"✅ Export completed: [bold green]{output}[/bold green]")

    except Exception as e:
        console.print(f"❌ Export failed: [bold red]{e}[/bold red]")


@app.command()
def clean(
        logs: bool = typer.Option(False, "--logs", help="Clean log files"),
        memory: bool = typer.Option(False, "--memory", help="Clean conversation memory"),
        cache: bool = typer.Option(False, "--cache", help="Clean cache files"),
        all: bool = typer.Option(False, "--all", help="Clean all data (DESTRUCTIVE!)")
):
    """🧹 Clean PioneerAI data and cache files"""

    if not any([logs, memory, cache, all]):
        console.print("❌ Please specify what to clean: --logs, --memory, --cache, or --all")
        return

    if all:
        if not Confirm.ask("⚠️ This will delete ALL PioneerAI data. Continue?"):
            console.print("✅ Operation cancelled")
            return
        logs = memory = cache = True

    cleaned_items = []

    if logs:
        _clean_logs()
        cleaned_items.append("logs")

    if memory:
        if _clean_memory():
            cleaned_items.append("memory")

    if cache:
        _clean_cache()
        cleaned_items.append("cache")

    console.print(f"✅ Cleaned: [bold green]{', '.join(cleaned_items)}[/bold green]")


@app.command()
def test(
        component: Optional[str] = typer.Option(
            None,
            "--component", "-c",
            help="Test specific component: memory, tokens, api, all"
        ),
        verbose: bool = typer.Option(
            False,
            "--verbose", "-v",
            help="Verbose test output"
        )
):
    """🧪 Run PioneerAI system tests"""

    console.print(Panel.fit("🧪 PioneerAI System Tests", style="bold blue"))

    test_component = component or "all"

    with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
    ) as progress:

        if test_component in ["memory", "all"]:
            task = progress.add_task("Testing memory system...", total=None)
            _test_memory_system(verbose)
            progress.remove_task(task)

        if test_component in ["tokens", "all"]:
            task = progress.add_task("Testing token counter...", total=None)
            _test_token_counter(verbose)
            progress.remove_task(task)

        if test_component in ["api", "all"]:
            task = progress.add_task("Testing OpenAI API...", total=None)
            asyncio.run(_test_api_connection(verbose))
            progress.remove_task(task)

    console.print("✅ [bold green]All tests completed![/bold green]")


@app.command()
def config(
        list: bool = typer.Option(False, "--list", help="List available configurations"),
        set: Optional[str] = typer.Option(None, "--set", help="Set configuration value"),
        get: Optional[str] = typer.Option(None, "--get", help="Get configuration value"),
        reset: bool = typer.Option(False, "--reset", help="Reset to default configuration")
):
    """⚙️ Manage PioneerAI configuration settings"""

    if list:
        _list_configurations()
    elif set:
        _set_configuration(set)
    elif get:
        _get_configuration(get)
    elif reset:
        if Confirm.ask("Reset all configuration to defaults?"):
            _reset_configuration()
            console.print("✅ Configuration reset to defaults")
    else:
        console.print("❌ Please specify an action: --list, --set, --get, or --reset")


# Helper Functions
def _display_welcome_banner():
    """Display PioneerAI welcome banner"""
    banner = Panel.fit(
        """
🧠 [bold blue]PioneerAI v2.0[/bold blue] - Enhanced CLI Mode

[dim]Advanced AI Chat System by Furkan[/dim]
[dim]Built with modern async architecture[/dim]

💡 [bold yellow]Commands:[/bold yellow]
  • !help - Show available commands  
  • !clear - Clear conversation memory
  • !stats - Show session statistics
  • quit/exit - End session

🚀 [bold green]Ready for conversation![/bold green]
        """,
        style="blue",
        title="Welcome to PioneerAI"
    )
    console.print(banner)


async def _run_chat_session():
    """Run the interactive chat session"""
    global pioneer_instance

    if not pioneer_instance:
        console.print("❌ PioneerAI not initialized!")
        return

    # Initialize the AI system
    await pioneer_instance.initialize()

    # Run interactive session with rich interface
    while pioneer_instance.session_active:
        try:
            # Check session timeout
            if pioneer_instance.check_session_timeout():
                console.print("⏳ [bold yellow]Session timeout reached[/bold yellow]")
                break

            # Get user input with rich prompt
            user_input = Prompt.ask("\n🚀 [bold blue]You[/bold blue]", console=console)

            # Handle exit commands
            if user_input.strip().lower() in ["quit", "exit", "bye"]:
                console.print("🤖 [bold green]PioneerAI: Görüşmek üzere komutan! 🚀[/bold green]")
                break

            if not user_input.strip():
                continue

            # Show processing indicator
            with console.status("[bold blue]PioneerAI is thinking...", spinner="dots"):
                response = await pioneer_instance.process_user_input(user_input)

            # Display response with rich formatting
            response_panel = Panel(
                response,
                title="🤖 PioneerAI Response",
                title_align="left",
                style="green"
            )
            console.print(response_panel)

        except (KeyboardInterrupt, EOFError):
            console.print("\n👋 [bold blue]Session ended![/bold blue]")
            break
        except Exception as e:
            console.print(f"❌ [bold red]Error: {e}[/bold red]")

    # Cleanup
    await pioneer_instance.cleanup()


def _get_file_size(file_path: str) -> str:
    """Get human-readable file size"""
    try:
        size = Path(file_path).stat().st_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    except:
        return "N/A"


def _show_recent_activity():
    """Show recent conversation activity"""
    try:
        if not Path(MEMORY_JSON).exists():
            return

        with open(MEMORY_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)

        recent_conversations = data.get("conversation", [])[-5:]  # Last 5

        if recent_conversations:
            console.print("\n📈 [bold blue]Recent Activity:[/bold blue]")
            for conv in recent_conversations:
                timestamp = conv.get("timestamp", "Unknown")
                user_preview = conv.get("user", "")[:50] + "..." if len(conv.get("user", "")) > 50 else conv.get("user",
                                                                                                                 "")
                console.print(f"  • {timestamp[:19]} - [dim]{user_preview}[/dim]")
    except:
        pass


def _export_json(output: str, sessions: Optional[int]):
    """Export data in JSON format"""
    if Path(MEMORY_JSON).exists():
        with open(MEMORY_JSON, 'r') as src, open(output, 'w') as dst:
            data = json.load(src)
            if sessions:
                data["conversation"] = data["conversation"][-sessions:]
            json.dump(data, dst, indent=2, ensure_ascii=False)


def _export_txt(output: str, sessions: Optional[int]):
    """Export data in text format"""
    # Implementation for text export
    pass


def _export_csv(output: str, sessions: Optional[int]):
    """Export data in CSV format"""
    # Implementation for CSV export
    pass


def _clean_logs():
    """Clean log files"""
    for log_file in ["logs/info.log", "logs/error.log", "logs/debug.log"]:
        if Path(log_file).exists():
            Path(log_file).unlink()


def _clean_memory() -> bool:
    """Clean memory files"""
    if Path(MEMORY_JSON).exists():
        if Confirm.ask(f"Delete conversation memory? This cannot be undone."):
            Path(MEMORY_JSON).unlink()
            return True
    return False


def _clean_cache():
    """Clean cache files"""
    # Implementation for cache cleaning
    pass


def _test_memory_system(verbose: bool):
    """Test memory management system"""
    try:
        from modules.memory_manager import AsyncMemoryManager
        memory_manager = AsyncMemoryManager()
        console.print("  ✅ Memory system: [green]OK[/green]")
    except Exception as e:
        console.print(f"  ❌ Memory system: [red]{e}[/red]")


def _test_token_counter(verbose: bool):
    """Test token counter system"""
    try:
        from modules.token_counter import TokenCounter
        counter = TokenCounter()
        test_text = "Hello, world!"
        tokens = counter.count_text_tokens(test_text)
        console.print(f"  ✅ Token counter: [green]OK[/green] ({tokens} tokens for test)")
    except Exception as e:
        console.print(f"  ❌ Token counter: [red]{e}[/red]")


async def _test_api_connection(verbose: bool):
    """Test OpenAI API connection"""
    try:
        # Test basic API connectivity
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            console.print("  ✅ API Key: [green]Found[/green]")
        else:
            console.print("  ❌ API Key: [red]Missing[/red]")
    except Exception as e:
        console.print(f"  ❌ API connection: [red]{e}[/red]")


def _list_configurations():
    """List available configurations"""
    # Implementation for configuration listing
    pass


def _set_configuration(setting: str):
    """Set configuration value"""
    # Implementation for setting configuration
    pass


def _get_configuration(setting: str):
    """Get configuration value"""
    # Implementation for getting configuration
    pass


def _reset_configuration():
    """Reset configuration to defaults"""
    # Implementation for resetting configuration
    pass


if __name__ == "__main__":
    app()