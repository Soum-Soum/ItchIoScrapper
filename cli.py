import sys
from loguru import logger
from tqdm import tqdm
import typer

from src.cli.data.scrap_assets_metadata import app as scrap_assets_metadata_app
from src.cli.data.scrap_assets import app as scrap_assets_app
from src.cli.data.unfold_assets import app as unfold_assets_app

app = typer.Typer()

app.add_typer(scrap_assets_metadata_app)
app.add_typer(scrap_assets_app)
app.add_typer(unfold_assets_app)

if __name__ == "__main__":
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
    )
    logger_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [<level>{level: ^12}</level>] <level>{message}</level>"
    logger.configure(
        handlers=[
            dict(
                sink=lambda msg: tqdm.write(msg, end=""),
                format=logger_format,
                colorize=True,
            )
        ]
    )
    app()
