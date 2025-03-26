import json
import time
from pathlib import Path
from typing import Optional

import pandas as pd
import typer
from loguru import logger
from selenium import webdriver
from selenium.common import (
    NoSuchElementException,
    ElementNotInteractableException,
    TimeoutException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from tqdm.rich import tqdm

from src.cli.data.scrap_assets_metadata import OneAssetPackMetadata



app = typer.Typer()


def find_download_button(element: WebElement) -> Optional[WebElement]:
    try:
        return element.find_element(By.CLASS_NAME, "buy_btn")
    except NoSuchElementException:
        return None


def find_money_input(element: WebElement) -> Optional[WebElement]:
    try:
        return element.find_element(By.CLASS_NAME, "money_input")
    except NoSuchElementException:
        return None


def find_download_btn(element: WebElement) -> Optional[WebElement]:
    try:
        return element.find_element(By.CLASS_NAME, "download_btn")
    except NoSuchElementException:
        pass
    try:
        return element.find_element(By.CLASS_NAME, "buy_btn")
    except NoSuchElementException:
        pass
    return None


def download(driver: webdriver.Firefox, metadata: OneAssetPackMetadata, timeout=10):
    try:
        driver.get(metadata.asset_page_url)
        logger.info(f"Downloading {metadata.title}...")
        buy_btns = driver.find_elements(By.CLASS_NAME, "buy_btn")

        for buy_btn in buy_btns:
            try:
                buy_btn.click()
                break
            except ElementNotInteractableException:
                pass

        WebDriverWait(driver, timeout).until(
            ec.presence_of_element_located((By.CLASS_NAME, "money_input"))
        )

        money_input = driver.find_element(By.CLASS_NAME, "money_input")
        money_input.clear()
        money_input.send_keys("0")
        money_input.submit()

        WebDriverWait(driver, timeout).until(
            ec.presence_of_element_located((By.CLASS_NAME, "download_btn"))
        )

        download_btn = driver.find_element(By.CLASS_NAME, "download_btn")
        download_btn.click()
        WebDriverWait(driver, timeout).until(
            ec.presence_of_element_located(
                (By.CLASS_NAME, "after_download_lightbox_widget")
            )
        )
        time.sleep(1)
        logger.info(f"Downloaded {metadata.title}")
    except NoSuchElementException as e:
        logger.error(f"Could not find element: {e} @ {driver.current_url}")
        return
    except TimeoutException as e:
        logger.error(f"TimeoutException: {e} @ {driver.current_url}")
        return
    except StaleElementReferenceException as e:
        logger.error(f"StaleElementReferenceException: {e} @ {driver.current_url}")
        return


def close_all_except_first(driver: webdriver.Firefox):
    driver.switch_to.window(driver.window_handles[0])
    for handle in driver.window_handles[1:]:
        driver.switch_to.window(handle)
        driver.close()
    driver.switch_to.window(driver.window_handles[0])


@app.command(
    name="scrape_assets_packs",
    help="Scrape asset packs from the given metadata directory.",
)
def scrape_assets_packs(
    asset_metadata_dir: Path = typer.Option(
        "./output/assets/metadata",
        help="Directory containing the asset metadata files.",
    ),
    out_path: Path = typer.Option(
        "./output/assets/assets",
        help="Output path for the scraped metadata.",
    ),
    headless: bool = typer.Option(
        is_flag=True,
        help="Run the browser in headless mode.",
    ),
    geckodriver_path: str = typer.Option(
        help="Path to the geckodriver executable.",
    ),
):
    out_path = Path(out_path)
    out_path.mkdir(exist_ok=True, parents=True)
    cvs_path = out_path / "assets.csv"
    if not cvs_path.exists():
        df = pd.DataFrame(columns=OneAssetPackMetadata.model_fields.keys())
    else:
        df = pd.read_csv(cvs_path, index_col=0)

    try:
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", str(out_path.absolute()))

        driver = webdriver.Firefox(
            service=FirefoxService(executable_path=geckodriver_path),
            options=options,
        )

        jsons = list(asset_metadata_dir.glob("*.json"))
        for json_file in tqdm(jsons, desc="Parsing assets"):
            with open(json_file, "r") as f:
                metadata = OneAssetPackMetadata.model_validate(json.load(f))

            if metadata.title in df.index:
                logger.info(f"Skipping {metadata.title}")
                continue

            close_all_except_first(driver)
            download(driver, metadata)

            df = pd.concat(
                [df, pd.DataFrame([metadata.model_dump()], index=[metadata.title])]
            )

    finally:
        df.to_csv(cvs_path, index=True)
        driver.quit()


if __name__ == "__main__":
    app()
