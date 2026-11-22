# Changelog  
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-11-23
First stable release: from here on, breaking changes bump the major version.

### Breaking
- Python >= 3.11.
- Config and page index live in the user config dir (`typer.get_app_dir`: `~/Library/Application Support/notion-cli-list-manager` on macOS, `~/.config/notion-cli-list-manager` on Linux), no longer inside the installed package. To migrate, copy the old `config.toml` there (or run `list set --id DATABASE_ID` again).
- The token is stored in the system keyring (macOS Keychain, Windows Credential Locker, Linux Secret Service/KWallet), never in `config.toml`; a token left in an old config file is ignored and removed on the next save. Run `list set --token TOKEN` once after upgrading. Systems without a keyring (e.g. headless Linux) are not supported.
- `list gen [TITLE]`: the title is optional and defaults to the date, replacing the `d4t35` keyword. The year defaults to the current one.
- Notion API `2026-03-11`: databases are accessed through their data source; `rm` moves pages to the Notion trash.

### Changed
- Project managed with uv (hatchling build, `src/` layout).
- The index column is now `#`, so a property may be called `Index`.
- Without `--db`, commands use the `Default` database if configured, otherwise the first one.

### Fixed
- Requests send `Authorization: Bearer <token>` and are JSON-encoded (titles with quotes no longer break).
- Listings follow pagination (previously capped at 100 pages).
- API and config errors exit with code 1 and a message; tracebacks no longer show local variables.

## [0.1.6] - 2022-01-05
### Fixed
- Formula type property
- Properties not unique name runtime bug

## [0.1.5] - 2022-01-05
### Added
- Properties support! 🌈 At the present, properties are fully supported (except Relations and Rolls up that are __NS__ - Not supported) but read-only. Writeable ones will be supported in the next versions.  
- Use `list db --prop [LABEL]` to edit the displayed properties of an already saved database labeled [LABEL]
- Error display color (yellow/orange)
- Added CHANGELOG file.

### Changed
- After a database submission, a prompt will ask you which properties you want to display.

### Fixed
- Some typos
