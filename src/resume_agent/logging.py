import logging
import sys
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.theme import Theme

# Custom rich theme
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "highlight": "bold magenta",
})

console = Console(theme=custom_theme)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configure application logging using RichHandler."""
    level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                show_path=False,
                tracebacks_show_locals=False,
            )
        ],
        force=True,
    )

    logger = logging.getLogger("resume_agent")
    logger.setLevel(level)
    return logger


logger = logging.getLogger("resume_agent")


def print_success(message: str) -> None:
    """Print green success message with checkmark."""
    console.print(f"[success]✔[/success] {message}")


def print_error(message: str) -> None:
    """Print red error message with crossmark."""
    console.print(f"[error]✖[/error] {message}")



def print_warning(message: str) -> None:
    """Print yellow warning message with caution sign."""
    console.print(f"[warning]⚠[/warning] {message}")


def print_info(message: str) -> None:
    """Print blue/cyan info message."""
    console.print(f"[info]ℹ[/info] {message}")


def print_step(title: str, subtitle: str = "") -> None:
    """Print a prominent step panel in the console."""
    body = f"[bold cyan]{title}[/bold cyan]"
    if subtitle:
        body += f"\n[dim white]{subtitle}[/dim white]"
    console.print(Panel.fit(body, border_style="cyan"))

