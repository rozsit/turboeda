@'
# Changelog
All notable changes to this project will be documented in this file.

## [0.2.1] - 2025-09-19
### Added
- GitHub Actions: Trusted Publishing workflow to PyPI.
- CI workflow (multi-Python import/smoke test).

### Changed
- README: prefer short CLI form (`turboeda "data.csv" --open`) over `report` subcommand in examples.
- Docs polish: Jupyter usage, defaults, tips.

### Links
- Release: https://github.com/rozsit/turboeda/releases/tag/v0.2.1
- Issues:  https://github.com/rozsit/turboeda/issues

## [Unreleased]
- (Add new entries here for the next version.)
'@ | Out-File -Encoding utf8 .\CHANGELOG.md
