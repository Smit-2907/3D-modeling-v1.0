"""
Blender Script — OBJ to Optimized GLB Converter
Optimized for Food-to-3D Realism.
"""

import bpy
import os
import sys
import argparse

def clear_scene():
    """Wipe the Blender scene clean."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    # Delete everything
    if bpy.context.view_layer.objects:
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()

def convert_to_glb(input_obj, output_glb, max_polys=20000):
    """The full conversion pipeline."""
    clear_scene()
    
    # ─── Step 1: Import ───
    print(f"📥 [BLENDER] Importing: {input_obj}")
    try:
        # Standard OBJ import for newer Blender
        bpy.ops.wm.obj_import(filepath=input_obj)
    except:
        try:
            # Fallback for older Blender versions
            bpy.ops.import_scene.obj(filepath=input_obj)
        except Exception as e:
            print(f"❌ [BLENDER] Error importing: {e}")
            return False

    # Get the object
    obs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not obs:
        print("❌ [BLENDER] No mesh found")
        return False
    
    obj = obs[0]
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # ─── Step 2: Center & Normalize ───
    # Ensure it's centered in the world
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0, 0, 0)
    
    # ─── Step 3: Realism Polish (Smooth & Normals) ───
    print("[BLENDER] Applying Realism Shaders & Smoothness...")
    bpy.ops.object.shade_smooth()
    
    # Fix Normals
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')

    # ─── Step 4: Decimate (Optimization) ───
    poly_count = len(obj.data.polygons)
    if poly_count > max_polys:
        ratio = max_polys / poly_count
        print(f"[BLENDER] Optimizing: {poly_count} -> ~{max_polys} (Ratio: {ratio:.3f})")
        dec = obj.modifiers.new(name="Decimate", type='DECIMATE')
        dec.ratio = ratio
        bpy.ops.object.modifier_apply(modifier="Decimate")

    # ─── Step 5: Material & PBR ───
    # We want a 'Principled BSDF' with a bit of organic gloss
    if not obj.data.materials:
        mat = bpy.data.materials.new(name="FoodMaterial")
        obj.data.materials.append(mat)
    else:
         mat = obj.data.materials[0]
    
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    if bsdf:
        # Roughness 0.4 makes it look slightly 'oily/fresh' instead of 'plastic/dry'
        bsdf.inputs['Roughness'].default_value = 0.4
        bsdf.inputs['Metallic'].default_value = 0.0
        
        # If the input has vertex colors, we link them to base color
        if obj.data.vertex_colors:
            v_color = nodes.get("VertexColor") or nodes.new("ShaderNodeVertexColor")
            v_color.layer_name = obj.data.vertex_colors[0].name
            mat.node_tree.links.new(v_color.outputs['Color'], bsdf.inputs['Base Color'])

    # ─── Step 6: Export ───
    print(f"📤 [BLENDER] Exporting: {output_glb}")
    try:
        bpy.ops.export_scene.gltf(
            filepath=output_glb,
            export_format='GLB',
            export_apply=True,
            export_vertex_color=True
        )
    except Exception as e:
        print(f"❌ [BLENDER] Export failed: {e}")
        return False

    print("🏁 [BLENDER] Conversion Success!")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i")
    parser.add_argument("--output", "-o")
    parser.add_argument("--max-polys", "-m", type=int, default=20000)
    
    # Ignore unknown args from Blender
    args, unknown = parser.parse_known_args(sys.argv[sys.argv.index("--") + 1:])
    
    success = convert_to_glb(args.input, args.output, args.max_polys)
    sys.exit(0 if success else 1)
