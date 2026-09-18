import tomllib
from enum import Enum
from pathlib import Path
from typing import Annotated

import polars as pl
import yaml


class FileType(Enum):
    CSV = ("csv",)
    EXCEL = ("xls", "xlsb", "xlsm", "xlsx")
    JSON = ("json", "json5", "jsonc")
    ODS = ("ods",)
    TOML = ("toml",)
    YAML = ("yaml",)

    @classmethod
    def from_extension(self, ext: str) -> FileType:
        ext = ext.lstrip(".").lower()
        for file_type in self:
            if ext in file_type.value:
                return file_type
        raise ValueError(f"Unsupported file extension: {ext}")


class DataProcessing:
    def __init__(self, data_file_path: str, sheet_id: Annotated[int, ">= 1"] = 1):
        file_path = Path(data_file_path)
        self.file_path = (
            file_path if file_path.is_absolute() else Path(__file__).parent / file_path
        )
        self.file_type = FileType.from_extension(self.file_path.suffix)

        match self.file_type:
            case FileType.CSV:
                df = pl.read_csv(self.file_path)
            case FileType.EXCEL:
                df = pl.read_excel(self.file_path, sheet_id=sheet_id)
            case FileType.JSON:
                df = pl.read_json(self.file_path)
            case FileType.ODS:
                df = pl.read_ods(self.file_path, sheet_id=sheet_id)
            case FileType.TOML:
                with open(self.file_path, "rb") as f:
                    data = tomllib.load(f)
                df = pl.DataFrame(data)
            case FileType.YAML:
                with open(self.file_path, "rb") as f:
                    data = yaml.safe_load(f)
                df = pl.DataFrame(data)

        self.df = df

    def print(self):
        print(self.df)

    def write(
        self,
        df: pl.DataFrame | None = None,
        file_type: FileType | None = None,
        data_output_path: str | None = None,
    ):
        df = self.df if df is None else df

        file_type = self.file_type if file_type is None else file_type
        file_path = (
            (
                Path(__file__).parent / "../output"
                if data_output_path is None
                else Path(data_output_path)
            )
            / self.file_path.name
        ).with_suffix(f".{file_type.value[0]}")

        match file_type:
            case FileType.CSV:
                df.write_csv(file_path)
            case FileType.EXCEL:
                df.write_excel(file_path)
            case FileType.JSON:
                df.write_json(file_path)
            case FileType.ODS:
                # NOTE: Should revisit this at a later time
                raise ValueError("ODS is not supported as an output format.")
            case FileType.TOML:
                raise ValueError("TOML is not supported as an output format.")
            case FileType.YAML:
                with open(file_path, "w") as f:
                    yaml.dump(df.to_dicts(), f, sort_keys=False)
