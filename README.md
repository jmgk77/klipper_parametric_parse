# Klipper Parametric Parser

A lightweight configuration enhancement for Klipper that enables parametric parsing with cross-section variable references, user-defined variables, and basic arithmetic expressions.

## Overview

Stop manually calculating probe offsets for your bed screws! This module allows you to define hardware constants once and reference them mathematically across your printer configuration, reducing errors and improving maintainability.

Currently, users must manually synchronize coordinates across multiple sections (e.g., matching `screws_tilt_adjust` to `[probe]` offsets). This introduces a parametric parsing layer that allows hardware constants to be defined once and referenced mathematically, improving configuration maintainability and reducing human error during hardware changes.

## Features

- **User-defined variables**: Define your own named constants directly in `[parametric_parse]`
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
   wget https://raw.githubusercontent.com/jmgk77/klipper_parametric_parse/refs/heads/master/parametric_parse.py
   ```

2. Add to your `printer.cfg`:
   ```ini
   [parametric_parse]
   ```

3. Restart Klipper:
   ```bash
   sudo systemctl restart klipper
   ```

> **Important:** Always restart Klipper via the command line (`sudo systemctl restart klipper`) after editing `parametric_parse.py`. The Mainsail/Fluidd "RESTART" button only reloads the config, not the Python module itself.

### Method 2: Manual Installation

1. Copy `parametric_parse.py` to your Klipper extras directory:
   ```bash
   cp parametric_parse.py ~/klipper/klippy/extras/
   ```

2. Add the configuration section to the **very top** of your `printer.cfg` (before any movement or hardware sections).

3. Restart Klipper via command line to load the module.

## Configuration

Add the `[parametric_parse]` section at the top of your `printer.cfg`:

```ini
[parametric_parse]
inject:
   # Your parametric definitions here
   target_section.target_option: (source_section:source_option) + 10
```

## Syntax

### User-Defined Variables

You can define named constants directly inside `[parametric_parse]` and reference them in your formulas. Any key that is not `inject` is treated as a user variable.

```ini
[parametric_parse]
screw_margin: 10
probe_safe_margin: 5
inject:
   bed_screws.screw1: (parametric_parse:screw_margin), (parametric_parse:screw_margin)
```

> **Note:** Variable names are lowercased by ConfigParser. `MyVar: 100` is stored and referenced as `myvar`.
> **Note:** All references, including user variables, must use the `(section:option)` syntax with parentheses. Bare `section:option` without parentheses will not be resolved.

### Variable References

Reference any config value — including user variables — using the format: `(section:option)`

**Examples:**
- `(stepper_x:position_max)` — max position from stepper_x
- `(bltouch:x_offset)` — probe X offset
- `(parametric_parse:myvar)` — a user-defined variable

### Expressions
- **Arithmetic**: `+`, `-`, `*`, `/`
- **Conditionals**: `value_if_true if condition else value_if_false`
- **Grouping**: Use parentheses for complex expressions

### Injection Format
```
target_section.target_option: expression1, expression2, ...
```

Each comma-separated expression produces one value in the result. Results are formatted to 3 decimal places.

## Examples

### User-Defined Variables
```ini
[parametric_parse]
bed_margin: 10
inject:
   bed_screws.screw1: (parametric_parse:bed_margin), (parametric_parse:bed_margin)
   bed_screws.screw2: (stepper_x:position_max) - (parametric_parse:bed_margin), (parametric_parse:bed_margin)
```

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

### Full Real-World Example

```ini
[parametric_parse]
margin: 10
inject:
   # Safe Z Home: center of bed minus probe offset
   safe_z_home.home_xy_position: (stepper_x:position_max)/2 - (bltouch:x_offset), (stepper_y:position_max)/2 - (bltouch:y_offset)

   # Bed Mesh: probe must stay on the bed, with safety margin
   bed_mesh.mesh_min: (bltouch:x_offset) + (parametric_parse:margin) if (bltouch:x_offset) > 0 else (parametric_parse:margin), (bltouch:y_offset) + (parametric_parse:margin) if (bltouch:y_offset) > 0 else (parametric_parse:margin)
   bed_mesh.mesh_max: (stepper_x:position_max) + (bltouch:x_offset) - (parametric_parse:margin) if (bltouch:x_offset) < 0 else (stepper_x:position_max) - (parametric_parse:margin), (stepper_y:position_max) + (bltouch:y_offset) - (parametric_parse:margin) if (bltouch:y_offset) < 0 else (stepper_y:position_max) - (parametric_parse:margin)

   # Screws Tilt Adjust: probe must be over the screws
   screws_tilt_adjust.screw1: (parametric_parse:margin) - (bltouch:x_offset), (parametric_parse:margin) - (bltouch:y_offset)
   screws_tilt_adjust.screw2: (stepper_x:position_max) - (parametric_parse:margin) - (bltouch:x_offset), (parametric_parse:margin) - (bltouch:y_offset)
   screws_tilt_adjust.screw3: (stepper_x:position_max) - (parametric_parse:margin) - (bltouch:x_offset), (stepper_y:position_max) - (parametric_parse:margin) - (bltouch:y_offset)
   screws_tilt_adjust.screw4: (parametric_parse:margin) - (bltouch:x_offset), (stepper_y:position_max) - (parametric_parse:margin) - (bltouch:y_offset)

   # Bed Screws: nozzle directly over the screws
   bed_screws.screw1: (parametric_parse:margin), (parametric_parse:margin)
   bed_screws.screw2: (stepper_x:position_max) - (parametric_parse:margin), (parametric_parse:margin)
   bed_screws.screw3: (stepper_x:position_max) - (parametric_parse:margin), (stepper_y:position_max) - (parametric_parse:margin)
   bed_screws.screw4: (parametric_parse:margin), (stepper_y:position_max) - (parametric_parse:margin)
```

## Troubleshooting

**`Option 'X' is not valid in section 'parametric_parse'`** — You are running an old version of `parametric_parse.py`. User-defined variables require the current version. Restart Klipper via `sudo systemctl restart klipper` after updating the file; the Mainsail/Fluidd RESTART button is not sufficient for Python module changes.

**Formula not resolving / `invalid syntax` error** — Make sure all section:option references use the full `(section:option)` syntax with parentheses. Bare references like `section:option` without parentheses are not resolved.

**Changes to `parametric_parse.py` not taking effect** — Always restart the Klipper service from the command line, not from the web UI.
