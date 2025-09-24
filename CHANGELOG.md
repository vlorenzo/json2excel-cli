# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-01

### Added
- Initial release of JSON to Excel Converter
- CLI tool for converting large JSON files to CSV/XLSX formats
- Streaming JSON processing using `ijson` for memory efficiency
- Root path selection with support for dotted paths and JSON Pointer notation
- Nested object flattening with configurable separators
- Array explosion feature with cartesian product support
- Column exclusion by dotted path prefixes
- Header sampling and ordering control (stable/alphabetical)
- Column pinning with `--first-column` option
- Rich console output with progress tracking
- Support for Decimal types and safe type normalization
- Comprehensive documentation including user guide and technical notes
- Example data and command reference
- Test suite with CLI integration and unit tests
- MIT License

### Features
- **Memory Efficient**: Process large JSON files without loading them entirely into memory
- **Flexible Output**: Generate both CSV and XLSX formats with custom sheet names
- **Advanced Data Processing**: Handle nested structures, arrays, and complex data types
- **User-Friendly**: Clear error messages and rich console interface
- **Developer-Friendly**: Well-documented codebase with comprehensive test coverage

[0.1.0]: https://github.com/vlorenzo/json2excel-cli/releases/tag/v0.1.0