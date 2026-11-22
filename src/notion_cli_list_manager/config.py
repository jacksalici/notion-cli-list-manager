import json
import tomllib
from pathlib import Path

import tomli_w
import typer

APP_DIR = Path(typer.get_app_dir("notion-cli-list-manager"))


class ConfigError(Exception):
    pass


class Config:
    def __init__(self, path: Path = APP_DIR / "config.toml"):
        self.path = path
        try:
            self.data = tomllib.loads(path.read_text()) if path.exists() else {}
        except tomllib.TOMLDecodeError as e:
            raise ConfigError(f"Invalid config file {path}: {e}") from e

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(tomli_w.dumps(self.data))

    @property
    def token(self) -> str:
        return self.data.get("token", "")

    @token.setter
    def token(self, value: str) -> None:
        self.data["token"] = value

    @property
    def databases(self) -> dict[str, dict]:
        return self.data.setdefault("databases", {})

    def database(self, label: str) -> dict:
        try:
            return self.databases[label]
        except KeyError:
            raise ConfigError(f"Database '{label}' not found.") from None


class PageIndex:
    """Page ids from the last listing, so `rm` can address pages by position."""

    def __init__(self, path: Path = APP_DIR / "pages.json"):
        self.path = path

    def save(self, ids: list[str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(ids))

    def load(self) -> list[str]:
        return json.loads(self.path.read_text()) if self.path.exists() else []
