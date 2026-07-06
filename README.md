# STL Render Tool

A Blender-based utility for rendering STL 3D models to high-quality PNG images with customizable parameters.

## Overview

This tool allows you to easily import STL files into Blender, apply materials, set various render parameters, and generate PNG renders — all from the command line without opening the Blender GUI.

## Requirements

* Blender (https://www.blender.org/download/), tested with 4.3 and 5.x
* Python: Included with Blender installation (no separate Python installation needed)

## Usage

Run the script from the command line using the following format:

### Required Arguments
* `stl_path`: Path to the STL file you want to render
* `output_path`: Directory where the output PNG will be saved. It uses the filename of the STL.

### Optional Arguments
* `--material_name`: Name of the Blender material to apply (must exist in your Blender file)
* `--x_rotation`: Rotation angle around X-axis in degrees
* `--y_rotation`: Rotation angle around Y-axis in degrees
* `--z_rotation`: Rotation angle around Z-axis in degrees
* `--width`: Render width in pixels (default: 500)
* `--height`: Render height in pixels (default: 500)
* `--orthographic`: Use orthographic camera mode instead of perspective

## Examples

Basic render of an STL file:

```bash
blender -b <template.blend> -P convertstl.py -- /path/to/model.stl /path/to/output
```

Render with material and rotation:

```bash
blender -b <template.blend> -P convertstl.py -- /path/to/model.stl /path/to/output --material_name=Metal --z_rotation=45
```

For Windows, the repository includes a CMD file `convertstl.cmd` to ease the use of calling Blender (the Blender location needs most likely to be adapted):

```bat
convertstl.cmd model.stl c:\out --material_name PLA
```

## Blender Template
The scene and lighing setup comme from a template file, like the one in this repository. Blender removes unused materials when saving the file. So, if you like to set up your template with multiple materials, you can assign them to a fake user to prevent that behavior. 

## Changelog

### 2026-07-05
* Verified compatibility with Blender 5.x; `convertstl.cmd` now points to Blender 5.1
* Fixed camera framing for non-square resolutions (resolution is now set before framing the camera)
* Camera framing now uses the world-space bounding box, so rotations are taken into account
* Orthographic mode now lets Blender compute the correct scale instead of estimating it
* Render resolution percentage is forced to 100% regardless of the template's setting

### 2025-03-09
* Initial version

## Contributing
If you would like to contribute to the project, please feel free to submit issues or pull requests on the GitHub repository. Contributions are welcome for features, bug fixes, documentation, and more.

## License
The source code is licensed under MIT.