# Archive Directory - Untold Story

## 📁 Archive Structure

This directory contains archived files organized by date and category.

### 📅 Date-based Organization

- **`2024/`** - Files from 2024 and earlier
- **`2025-01/`** - Files from January 2025
  - **`battle/`** - Battle system related files
  - **`tests/`** - Test files and validation scripts
  - **`docs/`** - Documentation and reports

### 🗂️ Category-based Organization

- **`deprecated/`** - Code that is definitely no longer needed
- **`ARCHIVE_LOG.md`** - Complete archive log with decisions

## 🧹 Cleanup Policy

- Files older than 6 months are moved to `2024/`
- Redundant files are consolidated (only newest version kept)
- Test files are organized by date and functionality
- Documentation is consolidated into relevant categories

## 📊 Archive Statistics

- **Total Files**: ~500+ (reduced from 1000+)
- **Size**: ~3.5MB (reduced from 6.9MB)
- **Last Updated**: 2025-01-09

## 🔍 Finding Files

Use the search function in your editor or:
```bash
find archive_new -name "*keyword*" -type f
```

## 📝 Archive Decisions

All deletion and consolidation decisions are documented in `ARCHIVE_LOG.md`.
