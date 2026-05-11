# Klipper Parametric Parser

A lightweight configuration enhancement for Klipper that enables parametric parsing with cross-section variable references and basic arithmetic expressions.

## Overview

Stop manually calculating probe offsets for your bed screws! This module allows you to define hardware constants once and reference them mathematically across your printer configuration, reducing errors and improving maintainability.

Currently, users must manually synchronize coordinates across multiple sections (e.g., matching `screws_tilt_adjust` to `[probe]` offsets). This introduces a parametric parsing layer that allows hardware constants to be defined once and referenced mathematically, improving configuration maintainability and reducing human error during hardware changes.

## Features

- **Cross-section references**: Reference values from any config section
- **Arithmetic expressions**: Support for basic math operations (+, -, *, /)
- **Conditional expressions**: Use `if-else` for dynamic calculations
- **Comma-separated values**: Perfect for coordinate pairs
- **Safe evaluation**: Restricted `eval()` prevents code injection
- **Error logging**: Detailed logging for debugging

## Installation

### Method 1: Direct Download

1. Download the module:
   ```bash
   cd ~/klipper/klippy/extras
   wget https://raw.githubusercontent.com/your-username/klipper-parametric-parser/main/parametric_parse.py
   ```

2. Add to your `printer.cfg`:
   ```ini
   [parametric_parse]
   ```

3. Restart Klipper:
   ```bash
   sudo systemctl restart klipper
   ```

### Method 2: Manual Installation

1. Copy `parametric_parse.py` to your Klipper extras directory:
   ```bash
   cp parametric_parse.py ~/klipper/klippy/extras/
   ```

2. Add the configuration section to the **very top** of your `printer.cfg` (before any movement or hardware sections).

3. Restart Klipper to load the module.

## Configuration

Add the `[parametric_parse]` section at the top of your `printer.cfg`:

```ini
[parametric_parse]
inject:
   # Your parametric definitions here
   target_section.target_option: (source_section:source_option) + 10
```

## Syntax

### Variable References
Reference any config value using the format: `(section:option)`

**Examples:**
- `(stepper_x:position_max)` - Reference the max position from stepper_x
- `(bltouch:x_offset)` - Reference probe offset

### Expressions
- **Arithmetic**: `+`, `-`, `*`, `/`
- **Conditionals**: `if condition else value`
- **Grouping**: Use parentheses for complex expressions

### Injection Format
```
target_section.target_option: expression1, expression2, ...
```

## Examples

### Basic Arithmetic
```ini
[parametric_parse]
inject:
   safe_z_home.home_xy_position: (stepper_x:position_max)/2, (stepper_y:position_max)/2
```

### Conditional Calculations
```ini
[parametric_parse]
inject:
   bed_mesh.mesh_min: (bltouch:x_offset) + 10 if (bltouch:x_offset) > 0 else 10, (bltouch:y_offset) + 10 if (bltouch:y_offset) > 0 else 10
```

### Complex Coordinates
```ini
[parametric_parse]
inject:
   screws_tilt_adjust.screw1: 10 - (bltouch:x_offset), 10 - (bltouch:y_offset)
   screws_tilt_adjust.screw2: (stepper_x:position_max) - 10 - (bltouch:x_offset), 10 - (bltouch:y_offset)
```

