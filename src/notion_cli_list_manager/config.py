import json
import tomllib
from pathlib import Path

import keyring
import tomli_w
import typer
from keyring.errors import KeyringError

APP_NAME = "notion-cli-list-manager"
APP_DIR = Path(typer.get_app_dir(APP_NAME))


class ConfigError(Exception):
    pass


class Config:
    def __init__(self, path: Path = APP_DIR / "config.toml"):
        self.path = path
        try:
            self.data = tomllib.loads(path.read_text()) if path.exists() else {}
        except tomllib.TOMLDecodeError as e:
            raise ConfigError(f"Invalid config file {path}: {e}") from e
        self.data.pop("token", None)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(tomli_w.dumps(self.data))

    @property
    def token(self) -> str:
        try:
            return keyring.get_password(APP_NAME, "token") or ""
        except KeyringError as e:
            raise ConfigError(f"Cannot read the token from the system keyring: {e}") from e

    @token.setter
    def token(self, value: str) -> None:
        try:
            keyring.set_password(APP_NAME, "token", value)
        except KeyringError as e:
            raise ConfigError(f"Cannot save the token to the system keyring: {e}") from e

    @property
    def databases(self) -> dict[str, dict]:
        return self.data.setdefault("databases", {})

    def resolve(self, label: str | None = None) -> str:
        """The given label, else 'Default', else the first configured database."""
        if label is None:
            if not self.databases:
                raise ConfigError("No databases configured: run `list set --id DATABASE_ID`.")
            label = "Default" if "Default" in self.databases else next(iter(self.databases))
        if label not in self.databases:
            raise ConfigError(f"Database '{label}' not found.")
        return label

    def database(self, label: str | None = None) -> dict:
        return self.databases[self.resolve(label)]


class PageIndex:
    """Page ids from the last listing, so `rm` can address pages by position."""

    def __init__(self, path: Path = APP_DIR / "pages.json"):
        self.path = path

    def save(self, ids: list[str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(ids))

    def load(self) -> list[str]:
        return json.loads(self.path.read_text()) if self.path.exists() else []
