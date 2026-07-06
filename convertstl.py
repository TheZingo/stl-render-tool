"""
Blender STL Import and Render Script

This script imports an STL file into Blender, applies specified transformations and
materials, and renders it to a PNG file.

Usage:
  blender -b <template.blend> -P render_stl.py -- [arguments]

Example:
  blender -b <template.blend> -P render_stl.py -- path/to/model.stl output/dir --material_name=Metal --z_rotation=45
"""

import bpy
import sys
import os
import math
import argparse
from mathutils import Vector 

# Constants
DEFAULT_RESOLUTION = 500
IMPORT_SCALE = 0.001  # Scale factor for imported STL (mm to m)
CAMERA_BORDER_FACTOR = 0.5  # Extra space around object in camera view

def parse_arguments():
    """Parse command line arguments passed after '--'."""
    argv = sys.argv
    if '--' in argv:
        argv = argv[argv.index('--') + 1:]
    else:
        print("Error: No arguments provided. Use -- to separate Blender args from script args.")
        sys.exit(1)
        
    parser = argparse.ArgumentParser(description="Import STL, apply material, rotate, and render to PNG.")
    parser.add_argument('stl_path', help="Path to the STL file")
    parser.add_argument('output_path', help="Path to save the rendered PNG")
    parser.add_argument('--material_name', help="Name of the material to apply")
    parser.add_argument('--width', type=int, default=DEFAULT_RESOLUTION, help="Render width in pixels")
    parser.add_argument('--height', type=int, default=DEFAULT_RESOLUTION, help="Render height in pixels")
    parser.add_argument('--orthographic', action='store_true', help="Use orthographic camera mode")
    parser.add_argument('--x_rotation', type=float, default=0.0, help="Rotation angle around X-axis in degrees")
    parser.add_argument('--y_rotation', type=float, default=0.0, help="Rotation angle around Y-axis in degrees")
    parser.add_argument('--z_rotation', type=float, default=0.0, help="Rotation angle around Z-axis in degrees")
    
    return parser.parse_args(argv)


def import_stl(file_path):
    """Import STL file and return the imported object."""
    try:
        bpy.ops.wm.stl_import(
            filepath=file_path,  
            forward_axis='Y',
            up_axis='Z',
            global_scale=IMPORT_SCALE
        )
    except RuntimeError as e:
        print(f"STL import failed: {str(e)}")
        sys.exit(1)
    
    # Verify import success
    if not bpy.context.selected_objects:
        print("No objects imported - check STL file validity")
        sys.exit(1)
    
    return bpy.context.active_object


def prepare_object(obj):
    """Prepare the object: apply scale and set origin correctly."""
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME', center='BOUNDS')
    return obj


def apply_material(obj, material_name):
    """Apply the specified material to the object if it exists."""
    if not material_name:
        return
    
    if material_name in bpy.data.materials:
        material = bpy.data.materials[material_name]
        if obj.data.materials:
            obj.data.materials[0] = material
        else:
            obj.data.materials.append(material)
    else:
        print(f"Warning: Material '{material_name}' not found in the Blender file")


def apply_rotation(obj, x_rotation=0.0, y_rotation=0.0, z_rotation=0.0):
    """Apply rotation to the object in radians."""
    if x_rotation:
        obj.rotation_euler[0] += math.radians(x_rotation)
    if y_rotation:
        obj.rotation_euler[1] += math.radians(y_rotation)
    if z_rotation:
        obj.rotation_euler[2] += math.radians(z_rotation)
    
    # Update the scene to apply the rotations
    bpy.context.view_layer.update()


def ensure_above_ground(obj):
    """Ensure the object is positioned above the ground plane (z=0)."""
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_z = min([v.z for v in bbox])
    if min_z < 0:
        obj.location.z -= min_z
    bpy.context.view_layer.update()


def setup_camera_for_object(obj, camera, use_orthographic=False):
    """Position and configure the camera to frame the object with a border."""
    # Calculate bounding box in world space so rotations are accounted for
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    bbox_min = [min([v[i] for v in bbox]) for i in range(3)]
    bbox_max = [max([v[i] for v in bbox]) for i in range(3)]
    bbox_size = [bbox_max[i] - bbox_min[i] for i in range(3)]
    max_dim = max(bbox_size)

    # Switch mode before framing so camera_to_view_selected computes
    # the correct orthographic scale
    if use_orthographic:
        camera.data.type = 'ORTHO'

    # Frame the object tightly
    bpy.context.view_layer.update()
    bpy.ops.view3d.camera_to_view_selected()

    # Add a border around the object
    if use_orthographic:
        camera.data.ortho_scale *= 1 + CAMERA_BORDER_FACTOR
    else:
        # Move camera along its local Z-axis (backwards)
        move_distance = max_dim * CAMERA_BORDER_FACTOR
        camera.location += camera.matrix_world.to_quaternion() @ Vector((0, 0, move_distance))

    bpy.context.view_layer.update()


def configure_render_settings(width, height):
    """Configure render settings."""
    scene = bpy.context.scene
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'



def get_output_filepath(stl_path, output_dir):
    """Generate the output PNG filepath based on the STL filename."""
    # Extract the filename without extension from the STL path
    stl_filename = os.path.splitext(os.path.basename(stl_path))[0]
    
    # Construct the output path with the new filename
    output_filename = f"{stl_filename}.png"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, output_filename)
    print(f"Output path: {output_path}")
    return output_path


def render_to_file(output_path):
    """Render the scene to the specified file path."""
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    print(f"Render completed successfully")


def main():
    """Main function to process the STL file and render it."""
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Validate input path
        if not os.path.isfile(args.stl_path):
            print(f"Error: STL file not found at {args.stl_path}")
            return 1
        
        # Import STL file
        obj = import_stl(args.stl_path)
        
        # Prepare the object
        obj = prepare_object(obj)
        
        # Apply material if specified
        apply_material(obj, args.material_name)
        
        # Apply rotations if specified
        apply_rotation(obj, args.x_rotation, args.y_rotation, args.z_rotation)
        
        # Ensure the object is above the ground
        ensure_above_ground(obj)
        
        # Configure render settings before framing the camera, since
        # camera_to_view_selected depends on the render aspect ratio
        configure_render_settings(args.width, args.height)

        # Configure camera
        camera = bpy.context.scene.camera
        setup_camera_for_object(obj, camera, args.orthographic)
        
        # Generate output path
        output_path = get_output_filepath(args.stl_path, args.output_path)
        
        # Render to file
        render_to_file(output_path)
        
        return 0  # Success
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1  # Failure

if __name__ == "__main__":
    sys.exit(main())
