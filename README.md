Feature: Basic Arithmetic and Cross-Section Variable References in Config Parsing  

"Stop manually calculating probe offsets for your bed screws!"


"Currently, users must manually synchronize coordinates across multiple sections (e.g., matching screws_tilt_adjust to [probe] offsets). This PR introduces a lightweight, define-before-use parametric parsing layer that allows hardware constants to be defined once and referenced mathematically, improving configuration maintainability and reducing human error during hardware changes."

Usage: copy parametric_parse.py to extras/ folder, and add [parametric_parse] as the first thing in your printer.cfg

Download the module:

Bash
cd ~/klipper/klippy/extras
wget https://raw.githubusercontent.com/your-username/klipper-parametric-parser/main/parametric_parse.py
Enable in printer.cfg:
Add the following line to the VERY TOP of your printer.cfg (before any movement or hardware sections):

Ini, TOML
[parametric_parse]
Restart Klipper:

### Syntax Example
Once enabled, you can define variables in a section and reference them elsewhere using math:

```ini
[parametric_parse] 
inject:   
   # 1. Safe Z Home: Center of the bed minus probe offset   
   safe_z_home.home_xy_position: (stepper_x:position_max)/2 - (bltouch:x_offset), (stepper_y:position_max)/2 - (bltouch:y_offset)    
   # 2. Bed Mesh: Ensure the PROBE stays on the bed (0 to position_max). We add a 10mm safety margin to the physical limits.   
   bed_mesh.mesh_min: (bltouch:x_offset) + 10 if (bltouch:x_offset) > 0 else 10, (bltouch:y_offset) + 10 if (bltouch:y_offset) > 0 else 10   
   bed_mesh.mesh_max: (stepper_x:position_max) + (bltouch:x_offset) - 10 if (bltouch:x_offset) < 0 else (stepper_x:position_max) - 10, (stepper_y:position_max) + (bltouch:y_offset) - 10 if (bltouch:y_offset) < 0 else (stepper_y:position_max) - 10    
   # 3. Screws Tilt Adjust: The PROBE must be over the screws   # Formula: Nozzle_Screw_Pos - Probe_Offset   
   screws_tilt_adjust.screw1: 10 - (bltouch:x_offset), 10 - (bltouch:y_offset)   
   screws_tilt_adjust.screw2: (stepper_x:position_max) - 10 - (bltouch:x_offset), 10 - (bltouch:y_offset)   
   screws_tilt_adjust.screw3: (stepper_x:position_max) - 10 - (bltouch:x_offset), (stepper_y:position_max) - 10 - (bltouch:y_offset)   
   screws_tilt_adjust.screw4: 10 - (bltouch:x_offset), (stepper_y:position_max) - 10 - (bltouch:y_offset)    
   # 4. Bed Screws: The NOZZLE over the screws (Direct position)   
   bed_screws.screw1: 10, 10   
   bed_screws.screw2: (stepper_x:position_max) - 10, 10   
   bed_screws.screw3: (stepper_x:position_max) - 10, (stepper_y:position_max) - 10   
   bed_screws.screw4: 10, (stepper_y:position_max) - 10
```

### Installation
Bash
sudo systemctl restart klipper