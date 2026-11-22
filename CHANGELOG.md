# Changelog  
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-11-22
### Changed
- Project managed with uv (hatchling build, `src/` layout); Python >= 3.11.
- Config and page index moved to the user config dir (`typer.get_app_dir`), out of the package.
- `list gen [TITLE]`: title is optional and defaults to the date (replaces the `d4t35` keyword); year defaults to the current one.
- The index column is now `#`, so a property may be called `Index`.
### Fixed
- Requests send `Authorization: Bearer <token>` and are JSON-encoded (titles with quotes no longer break).
- Listings follow pagination (previously capped at 100 pages).
- API and config errors exit with code 1 and a message; tracebacks no longer show local variables.

## [0.1.6] - 2022-01-05
### Added
- Formula type property
- Properties not unique name runtime bug

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
