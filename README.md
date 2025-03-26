<!-- HEADER STYLE: CONSOLE -->
<div align="center">

```console
██████ ██████  ████  ██  ██ ██████  ████   ████   ████  ██████   ██   ██████ ██████ ██████ ██████         ████  ██████ ██████ 
  ██     ██   ██     ██  ██   ██   ██  ██ ██     ██     ██  ██  ████  ██  ██ ██  ██ ██     ██  ██        ██       ██     ██   
  ██     ██   ██     ██████   ██   ██  ██  ████  ██     ██████ ██  ██ ██████ ██████ ████   ██████   ██   ██ ███   ██     ██   
  ██     ██   ██     ██  ██   ██   ██  ██     ██ ██     ██ ██  ██████ ██     ██     ██     ██ ██    ██   ██  ██   ██     ██   
██████   ██    ████  ██  ██ ██████  ████  █████   ████  ██  ██ ██  ██ ██     ██     ██████ ██  ██         ████  ██████   ██   


```

# A very basic UNMAINTAINED itch.io scraper

</div>



# CLI

**Usage**:

```console
$ [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `scrape_metadata`: Scrape the metadata of the free game...
* `scrape_assets_packs`: Scrape asset packs from the given metadata...
* `unfold_assets`: Unfold assets from the given directory.

## `scrape_metadata`

Scrape the metadata of the free game assets from itch.io.

**Usage**:

```console
$ scrape_metadata [OPTIONS] [BASE_URL] [OUT_PATH]
```

**Arguments**:

* `[BASE_URL]`: Base URL to scrape from.  [default: https://itch.io/game-assets/free]
* `[OUT_PATH]`: Output path for the scraped metadata.  [default: ./output/assets/metadata]

**Options**:

* `--asset-count INTEGER`: Number of assets to scrape.  [default: 1000]
* `--headless / --no-headless`: Run the browser in headless mode.  [default: headless]
* `--geckodriver-path TEXT`: Path to the geckodriver executable.  [required]
* `--help`: Show this message and exit.

## `scrape_assets_packs`

Scrape asset packs from the given metadata directory.

**Usage**:

```console
$ scrape_assets_packs [OPTIONS]
```

**Options**:

* `--asset-metadata-dir PATH`: Directory containing the asset metadata files.  [default: ./output/assets/metadata]
* `--out-path PATH`: Output path for the scraped metadata.  [default: ./output/assets/assets]
* `--headless / --no-headless`: Run the browser in headless mode.  [required]
* `--geckodriver-path TEXT`: Path to the geckodriver executable.  [required]
* `--help`: Show this message and exit.

## `unfold_assets`

Unfold assets from the given directory.

**Usage**:

```console
$ unfold_assets [OPTIONS] [ASSET_DIR] [OUTPUT_DIR]
```

**Arguments**:

* `[ASSET_DIR]`: The directory containing the assets to unfold.  [default: ./output/assets/assets]
* `[OUTPUT_DIR]`: The directory to save the unfolded assets.  [default: ./output/assets/unfolded]

**Options**:

* `--help`: Show this message and exit.

