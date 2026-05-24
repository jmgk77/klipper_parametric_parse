# klipper_parametric_parse

A Klipper extra that lets you use values from your `printer.cfg` — and basic math — to set other values, at config load time.

## The problem it solves

Several Klipper sections require coordinates that are derived from values defined elsewhere. For example, `screws_tilt_adjust` screw positions depend on `[probe]` offsets and axis limits. When you change a probe mount or swap hardware, you update one value and then manually recalculate and update five others. This module does those calculations for you.

## How it works

Add a `[parametric_parse]` section to your `printer.cfg`. Inside `inject:`, write formulas that reference any `section:option` already present in your config. The module resolves and evaluates them during `__init__`, before Klipper validates the affected sections, by writing the results directly into the live `ConfigParser` instance.

**The `[parametric_parse]` section must appear before any section it modifies.**

References use the syntax `(section:option)`. The result of each formula replaces the target value as if you had typed it manually.

## Installation

```bash
cd ~/klipper/klippy/extras
wget https://raw.githubusercontent.com/jmgk77/klipper_parametric_parse/master/parametric_parse.py
```

Then restart Klipper via the command line:

```bash
sudo systemctl restart klipper
```

> **Note:** The Mainsail/Fluidd "RESTART" button only reloads the config, not the Python module. Always use `systemctl restart klipper` after installing or updating `parametric_parse.py`.

## Configuration

```ini
[parametric_parse]
inject:
    target_section.target_option: (source_section:source_option) + 10
```

### User-defined variables

Any key inside `[parametric_parse]` other than `inject` is treated as a user variable and can be referenced in formulas:

```ini
[parametric_parse]
screw_margin: 10
inject:
    bed_screws.screw1: (parametric_parse:screw_margin), (parametric_parse:screw_margin)
```

### Syntax

Each inject line follows this structure:

```
target_section.target_option: formula using (source_section:source_option)
```

Dot notation (`section.option`) is the write target. Colon notation (`section:option`) inside parentheses is a read reference. The distinction is intentional — it makes the data flow direction unambiguous at a glance.

| Element | Description |
|---|---|
| `section.option` | Write target (left-hand side) |
| `(section:option)` | Read reference to any value in your config |
| `+  -  *  /` | Basic arithmetic |
| `A if condition else B` | Conditional expression (Python ternary) |
| `value1, value2` | Comma-separated output (for coordinate pairs) |
| `# comment` | Inline comments are supported |

Injection is processed **line by line, in order**. A value set in one line is immediately available to subsequent lines:

```ini
inject:
    stepper_x.position_max: 200
    safe_z_home.home_xy_position: (stepper_x:position_max) / 2, 100
    # home_xy_position becomes 100, 100
    stepper_x.position_max: 100
    bed_screws.screw1: (stepper_x:position_max) / 2, 100
    # screw1 becomes 50, 100
```

## Example

The probe name and axis names below are from a specific machine. Replace them with whatever is in your config — the module makes no assumptions about hardware.

```ini
[parametric_parse]
safe_margin: 10
inject:
    # Safe Z Home: center of the bed, accounting for probe offset
    safe_z_home.home_xy_position: (stepper_x:position_max) / 2 - (bltouch:x_offset), (stepper_y:position_max) / 2 - (bltouch:y_offset)

    # Bed Mesh: keep the probe inside the bed with a safety margin
    bed_mesh.mesh_min: (bltouch:x_offset) + (parametric_parse:safe_margin) if (bltouch:x_offset) > 0 else (parametric_parse:safe_margin), (bltouch:y_offset) + (parametric_parse:safe_margin) if (bltouch:y_offset) > 0 else (parametric_parse:safe_margin)
    bed_mesh.mesh_max: (stepper_x:position_max) + (bltouch:x_offset) - (parametric_parse:safe_margin) if (bltouch:x_offset) < 0 else (stepper_x:position_max) - (parametric_parse:safe_margin), (stepper_y:position_max) + (bltouch:y_offset) - (parametric_parse:safe_margin) if (bltouch:y_offset) < 0 else (stepper_y:position_max) - (parametric_parse:safe_margin)

    # Screws Tilt Adjust: probe must be over the screws (nozzle pos = screw pos - probe offset)
    screws_tilt_adjust.screw1: (parametric_parse:safe_margin) - (bltouch:x_offset), (parametric_parse:safe_margin) - (bltouch:y_offset)
    screws_tilt_adjust.screw2: (stepper_x:position_max) - (parametric_parse:safe_margin) - (bltouch:x_offset), (parametric_parse:safe_margin) - (bltouch:y_offset)
    screws_tilt_adjust.screw3: (stepper_x:position_max) - (parametric_parse:safe_margin) - (bltouch:x_offset), (stepper_y:position_max) - (parametric_parse:safe_margin) - (bltouch:y_offset)
    screws_tilt_adjust.screw4: (parametric_parse:safe_margin) - (bltouch:x_offset), (stepper_y:position_max) - (parametric_parse:safe_margin) - (bltouch:y_offset)

    # Bed Screws: nozzle directly over screws
    bed_screws.screw1: (parametric_parse:safe_margin), (parametric_parse:safe_margin)
    bed_screws.screw2: (stepper_x:position_max) - (parametric_parse:safe_margin), (parametric_parse:safe_margin)
    bed_screws.screw3: (stepper_x:position_max) - (parametric_parse:safe_margin), (stepper_y:position_max) - (parametric_parse:safe_margin)
    bed_screws.screw4: (parametric_parse:safe_margin), (stepper_y:position_max) - (parametric_parse:safe_margin)
```

In `klippy.log`, each substitution is logged:

```
Parametric: safe_z_home:home_xy_position updated to 112.500, 152.500 (was 112.5, 112.5)
Parametric: bed_mesh:mesh_min updated to 10.000, 10.000 (was 5, 5)
```

## Notes and limitations

- Formulas are evaluated with Python's `eval()` with builtins disabled. If you have write access to `printer.cfg`, you already have shell access — this is not an additional attack surface.
- The module accesses `config.fileconfig` (Klipper's internal `ConfigParser`) directly. The public config API does not expose cross-section reads during `__init__`, so there is no alternative.
- `position_min`/`position_max` are axis travel limits, not necessarily bed dimensions. Make sure your formulas reflect your actual machine geometry.
- Variable names inside `[parametric_parse]` are lowercased by ConfigParser. `MyVar: 100` must be referenced as `(parametric_parse:myvar)`.
