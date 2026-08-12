# Bulk Import Guide

Populate the CSV templates in `templates/assessment/`, preserving stable lowercase identifiers with letters, digits, and hyphens. Example rows are synthetic. Validate references before import, retain Unknown when needed, and export a JSON backup before replacing a draft. Imported assessment JSON is migrated to the current schema then Pydantic-validated.
