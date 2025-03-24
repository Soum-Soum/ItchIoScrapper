import json
import re
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from loguru import logger
from pydantic import BaseModel
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webelement import WebElement
from tqdm.rich import tqdm

app = typer.Typer()


def sanitize_filename(filename: str, replacement="_"):
    """
    Sanitize a filename by replacing invalid characters with a replacement character.
    """
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', replacement, filename).strip()


class OneAssetPackMetadata(BaseModel):
    title: str
    author: str
    text: Optional[str] = None
    asset_page_url: Optional[str] = None
    image_src: Optional[str] = None


def try_get_attribute(
    element: WebElement,
    children_class_name: str,
    attribute_getter: Callable[[WebElement], str],
) -> Optional[str]:
    try:
        children = element.find_element(By.CLASS_NAME, children_class_name)
        return attribute_getter(children)
    except NoSuchElementException:
        return None


def try_get_text(element: WebElement, children_class_name: str) -> Optional[str]:
    return try_get_attribute(element, children_class_name, lambda e: e.text.strip())


def try_get_href(element: WebElement, children_class_name: str) -> Optional[str]:
    return try_get_attribute(
        element, children_class_name, lambda e: e.get_attribute("href")
    )


def try_get_src(element: WebElement, children_class_name: str) -> Optional[str]:
    return try_get_attribute(
        element, children_class_name, lambda e: e.get_attribute("src")
    )


def parse_cell(game_cell: WebElement) -> OneAssetPackMetadata:
    try:
        image_src = game_cell.find_element(by=By.TAG_NAME, value="img").get_attribute(
            "src"
        )
    except NoSuchElementException:
        image_src = None

    return OneAssetPackMetadata(
        title=try_get_text(game_cell, "game_title"),
        author=try_get_text(game_cell, "game_author"),
        text=try_get_text(game_cell, "game_text"),
        asset_page_url=try_get_href(game_cell, "game_link"),
        image_src=image_src,
    )


def update_game_cells_list(driver, previous_game_cells_count: int) -> list[WebElement]:
    logger.info("Updating the cells list...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    start_waiting = datetime.now()
    updated_game_cells = []
    while (datetime.now() - start_waiting).seconds < 10:
        updated_game_cells = driver.find_elements(By.CLASS_NAME, "game_cell")
        if len(updated_game_cells) > previous_game_cells_count:
            break
        time.sleep(0.1)

    if len(updated_game_cells) == previous_game_cells_count:
        logger.info("No new cells found after 10 seconds of waiting.")
        return []

    logger.info(
        f"Found {len(updated_game_cells) - previous_game_cells_count} new cells."
    )
    return updated_game_cells[previous_game_cells_count:]


@app.command()
def scrape_metadata(
    base_url: str = typer.Argument(
        "https://itch.io/game-assets/free",
        help="Base URL to scrape from.",
    ),
    out_path: Path = typer.Argument(
        "./output/assets/metadata",
        help="Output path for the scraped metadata.",
    ),
    asset_count: int = typer.Option(
        1000,
        help="Number of assets to scrape.",
    ),
    headless: bool = typer.Option(
        True,
        help="Run the browser in headless mode.",
    ),
    geckodriver_path: str = typer.Option(
        help="Path to the geckodriver executable.",
    ),
):
    out_path = Path(out_path)
    out_path.mkdir(parents=True, exist_ok=True)

    options = Options()
    if headless:
        options.add_argument("--headless")

    driver = webdriver.Firefox(
        service=FirefoxService(executable_path=geckodriver_path), options=options
    )

    driver.get(base_url)

    games_metadata_count = 0
    game_cells_to_fetch = driver.find_elements(By.CLASS_NAME, "game_cell")

    while True:
        for cell in tqdm(game_cells_to_fetch, desc="Parsing assets", leave=False):
            metadata = parse_cell(cell)
            games_metadata_count += 1

            with open(out_path / f"{sanitize_filename(metadata.title)}.json", "w") as f:
                json.dump(metadata.model_dump(), f, indent=4)

            if games_metadata_count % 10 == 0:
                logger.info(f"Collected {games_metadata_count} assets.")

        if games_metadata_count >= asset_count:
            logger.info(f"Collected {games_metadata_count} assets.")
            break

        game_cells_to_fetch = update_game_cells_list(driver, games_metadata_count)
        if not game_cells_to_fetch:
            break

    driver.quit()


if __name__ == "__main__":
    app()
