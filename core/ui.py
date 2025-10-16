# core/ui.py
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Tạo một đối tượng Console duy nhất để sử dụng trong toàn bộ ứng dụng
console = Console()

def print_panel(content, title, style="cyan"):
    """In ra một panel có tiêu đề và nội dung."""
    console.print(Panel(content, title=title, border_style=style, padding=(1, 2)))

def print_header(title):
    """In ra một tiêu đề lớn, bắt mắt."""
    console.rule(f"[bold bright_yellow]🚀 {title} 🚀[/bold bright_yellow]")

def print_success(message):
    """In thông báo thành công."""
    console.print(f"[bold green]✅ {message}[/bold green]")

def print_error(message):
    """In thông báo lỗi."""
    console.print(f"[bold red]❌ {message}[/bold red]")

def print_warning(message):
    """In thông báo cảnh báo."""
    console.print(f"[bold yellow]⚠️ {message}[/bold yellow]")

def print_info(message):
    """In thông báo thông tin."""
    console.print(f"[cyan]ℹ️ {message}[/cyan]")

def create_table(title, columns):
    """Tạo một đối tượng Table của Rich với các cột được định nghĩa."""
    table = Table(title=title, show_header=True, header_style="bold magenta", border_style="dim")
    for col_name, style in columns.items():
        table.add_column(col_name, style=style)
    return table
