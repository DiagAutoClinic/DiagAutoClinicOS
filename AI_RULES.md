# AI Development Rules for DiagAutoClinicOS

## Theme System Rules

### DACOS Theme Authority
**RULE: Only `shared/themes/dacos_theme.py` shall contain DACOS_THEME and DACOS_STYLESHEET definitions.**

- `DACOS_THEME`: Dictionary containing all DACOS color constants and theme values
- `DACOS_STYLESHEET`: Complete QSS stylesheet string for the DACOS unified theme

### Rationale
- Prevents theme definition duplication across the codebase
- Ensures single source of truth for DACOS theme constants
- Maintains consistency in theme application
- Simplifies theme maintenance and updates

### Usage Guidelines
- Import DACOS_THEME and DACOS_STYLESHEET only from `shared/themes/dacos_theme.py`
- Do not redefine these constants in other files
- Use `get_dacos_color()` function for accessing theme colors
- Use `apply_dacos_theme()` function for applying the theme to QApplication instances

### Enforcement
- All AI-generated code must adhere to this rule
- Theme-related modifications should only affect `shared/themes/dacos_theme.py`
- Other theme files (dark.qss, light.qss, etc.) are separate and independent

### Development Stage Note
The DACOS theme serves as the default development theme and may be replaced or modified for production use.