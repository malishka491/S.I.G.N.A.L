"""
extract.py
Extracts data from source folders or selected files.
"""

import json
import csv
import os
import glob

from etl.utils.logger_config import get_logger
from etl.adapters import weather, news, government, disaster, transport

logger = get_logger(__name__)

SOURCE_ADAPTERS = {
    "weather": ("json", weather),
    "news": ("csv", news),
    "government": ("json", government),
    "disaster": ("json", disaster),
    "transport": ("json", transport),
}


def read_json_file(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as err:
        logger.error(f"JSON read error in {file_path}: {err}")
        return None


def read_csv_file(file_path: str) -> list:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except (csv.Error, OSError) as err:
        logger.error(f"CSV read error in {file_path}: {err}")
        return []


def extract_source(
    source_type: str,
    folder_path: str,
    file_paths: list = None
) -> list:

    if source_type not in SOURCE_ADAPTERS:
        logger.error(f"Unknown source_type: {source_type}")
        return []

    file_format, adapter_module = SOURCE_ADAPTERS[source_type]
    records = []

    if file_paths is None:
        if not os.path.exists(folder_path):
            logger.warning(f"Folder nahi mila: {folder_path}")
            return []

        file_paths = glob.glob(
            os.path.join(folder_path, "**", f"*.{file_format}"),
            recursive=True
        )

    for file_path in file_paths:

        if not os.path.exists(file_path):
            logger.warning(f"File nahi mili: {file_path}")
            continue

        if file_format == "json":
            raw = read_json_file(file_path)

            if raw:
                records.append(adapter_module.adapt(raw))

        elif file_format == "csv":
            for row in read_csv_file(file_path):
                records.append(adapter_module.adapt(row))

    logger.info(
        f"Extracted {len(records)} records from "
        f"'{source_type}' ({len(file_paths)} files)"
    )

    return records


def extract_all_sources(
    raw_data_root: str = os.path.join("data", "raw"),
    selected_files: list = None
) -> list:

    all_records = []

    if selected_files is not None:
        # Realtime mode: process only the selected fresh files
        for source_type, file_path in selected_files:
            folder_path = os.path.dirname(file_path)

            all_records.extend(
                extract_source(
                    source_type,
                    folder_path,
                    file_paths=[file_path]
                )
            )

    else:
        # Existing behavior: process all available sources
        for source_type in SOURCE_ADAPTERS:
            folder_path = os.path.join(raw_data_root, source_type)
            all_records.extend(
                extract_source(source_type, folder_path)
            )

    logger.info(
        f"TOTAL extracted across all sources: {len(all_records)}"
    )

    return all_records


if __name__ == "__main__":
    records = extract_all_sources()

    print(f"\nTotal records extracted: {len(records)}")

    if records:
        print("\nSample record:")
        print(records[0])
    else:
        print("Koi record nahi mila.")