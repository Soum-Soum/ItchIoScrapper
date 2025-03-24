import shutil
import tempfile
from pathlib import Path
from typing import Optional, Union
from zipfile import ZipFile
import tarfile
import rarfile
import py7zr
from tqdm.rich import tqdm
import typer
from loguru import logger
from py7zr import SevenZipFile

app = typer.Typer()

ARCHIVE_EXTRENSIONS = {".zip", ".tar", ".gz", ".bz2", ".xz", ".rar", ".7z"}
ACCEPTED_EXTENSIONS = {".png", ".gif", ".svg"}


def merge_archive_name(
    archive_name: Optional[str],
    file_name: str,
) -> str:
    """
    Merge the archive name with the file name, replacing spaces with underscores.
    """
    if archive_name:
        return f"{archive_name}_{file_name}".replace(" ", "_")
    return file_name.replace(" ", "_")


def handle_one_file(
    file_path: Path,
    output_dir: Path,
    archive_name: Optional[str] = None,
) -> None:
    """
    Handle a single file by moving it to the appropriate directory based on its extension.
    If the file is an archive, it will be unpacked and its contents will be processed.
    """
    # logger.debug(f"Handling file {file_path}...")
    assert (
        file_path.exists() and file_path.is_file()
    ), f"File {file_path} does not exist or is not a file."

    if file_path.name.startswith(".") or file_path.suffix == "":
        return

    extension = file_path.suffix.lower()
    assert extension in ACCEPTED_EXTENSIONS, f"Unsupported file format: {extension}"

    if archive_name:
        archive_name = merge_archive_name(
            archive_name,
            file_path.stem,
        )
        file_name = f"{archive_name}_{file_path.name}".replace(" ", "_")
    else:
        file_name = file_path.name.replace(" ", "_")

    output_path = output_dir / extension.replace(".", "") / file_name
    output_path.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy(file_path, output_path)


def unfold_archive(
    archive: Union[ZipFile, tarfile.TarFile, rarfile.RarFile, SevenZipFile],
    output_dir: Path,
    archive_name: Optional[str] = None,
):
    with tempfile.TemporaryDirectory() as temp_dir:
        archive.extractall(temp_dir)
        files = list(filter(lambda x: x.is_file(), Path(temp_dir).rglob("*")))
        for file in files:
            if file.is_dir() or file.name.startswith(".") or file.suffix == "":
                continue

            handle_asset(file, output_dir, archive_name=archive_name)


def handle_archive(
    archive_path: Path,
    output_dir: Path,
    archive_name: Optional[str] = None,
) -> None:
    logger.info(f"Unpacking archive {archive_path}...")
    extension = archive_path.suffix.lower()

    archive_name = merge_archive_name(
        archive_name,
        archive_path.stem,
    )

    match extension:
        case ".zip":
            with ZipFile(archive_path, "r") as zip_ref:
                unfold_archive(zip_ref, output_dir, archive_name)
        case ".tar" | ".gz" | ".bz2" | ".xz":
            with tarfile.open(archive_path, "r:*") as tar_ref:
                unfold_archive(tar_ref, output_dir, archive_name)
        case ".rar":
            with rarfile.RarFile(archive_path) as rar_ref:
                unfold_archive(rar_ref, output_dir, archive_name)
        case ".7z":
            with py7zr.SevenZipFile(archive_path, mode="r") as seven_zip:
                unfold_archive(seven_zip, output_dir, archive_name)


def handle_asset(
    asset_path: Path,
    output_dir: Path,
    archive_name: Optional[str] = None,
) -> None:
    extension = asset_path.suffix.lower()

    if extension in ARCHIVE_EXTRENSIONS:
        handle_archive(
            asset_path, output_dir, archive_name=f"{archive_name}_{asset_path.stem}"
        )
    elif extension in ACCEPTED_EXTENSIONS:
        handle_one_file(asset_path, output_dir, archive_name=archive_name)
    else:
        # logger.debug(f"Skipping {asset_path}, unsupported file format.")
        return


@app.command()
def unfold(
    asset_dir: Path = typer.Argument(
        "./output/assets/assets",
        help="The directory containing the assets to unfold.",
    ),
    output_dir: Path = typer.Argument(
        "./output/assets/unfolded",
        help="The directory to save the unfolded assets.",
    ),
):
    all_assets_paths = list(asset_dir.glob("*"))

    for asset_path in tqdm(all_assets_paths, desc="Unfolding assets"):
        handle_asset(
            asset_path,
            output_dir,
        )


if __name__ == "__main__":
    app()
