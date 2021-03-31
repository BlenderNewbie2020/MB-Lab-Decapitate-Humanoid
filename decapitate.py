
import bpy
import mathutils

''' 
Use list comprehension to get vertices in the 'head' group
see: https://blender.stackexchange.com/questions/75223/finding-vertices-in-a-vertex-group-using-blenders-python-api

convert vertices list to a set for O[1] rather than O[n]
see: https://stackoverflow.com/questions/20234935/python-in-operator-speed
and: https://wiki.python.org/moin/TimeComplexity
'''

obj = bpy.context.selected_objects[0]
grp_idx = obj.vertex_groups['head'].index
vertices = set([ v.index for v in obj.data.vertices if grp_idx in [ vg.group for vg in v.groups ] ])

''' Get the source object shape key values '''

srce = bpy.context.selected_objects[0]

base_key_block = srce.data.shape_keys.reference_key                                        # bpy.data.shape_keys['Key'].key_blocks["basis"]
srce_base_key_values = [item.co for item in base_key_block.data.values()]                  # len(base_key_block.data.values()) >>> 18210
key_blocks = srce.data.shape_keys.key_blocks

data = {}
data[srce.name] = {
                "base": base_key_block.name,
                "diffs": [],
}

for key_block_name in key_blocks.keys():                                                   # iterate over all the shape keys including basis
    key_block = key_blocks[key_block_name]                                                 # current shape key name

    key_values = [item.co for item in key_block.data.values()]                             # current shape key values
    
    if base_key_block == key_block:                                                   
        dest_base_key_values = [j for i, j in enumerate(key_values) if i in vertices]
        continue
    else:
        dest_key_values = [j for i, j in enumerate(key_values) if i in vertices]           # only keep vertices in the 'head' vertex group
            
    if len(dest_key_values) != len(dest_base_key_values):                                  # error if mesh vertex count is different
        raise RuntimeError("1. Source mesh vertex count is different: " + key_block_name)
    
    dest_diff_key_values = [a - b for a, b in zip(dest_key_values, dest_base_key_values)]   # calculate the differences
    
    '''
    dest_diff_key_values = []                                                              # calculate the differences
    for i in range(len(dest_key_values)):
        dest_diff_key_values.append((dest_key_values[i] - dest_base_key_values[i])[:])
    '''
        
    data[srce.name]["diffs"].append({
        "name": key_block_name,
        "values": dest_diff_key_values,
    })

''' Duplicate our humanoid's head See: https://blender.stackexchange.com/questions/75223/finding-vertices-in-a-vertex-group-using-blenders-python-api '''

# In edit mode
bpy.ops.object.mode_set( mode = 'EDIT' )
srce.vertex_groups.active = srce.vertex_groups['head']
bpy.ops.object.vertex_group_select()
bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "constraint_axis":(False, False, False),      "constraint_orientation":'GLOBAL', "mirror":False, "proportional":'DISABLED', "proportional_edit_falloff":'SMOOTH', "proportional_size":0.0323492, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False})
bpy.ops.mesh.separate(type='SELECTED')
bpy.ops.object.mode_set( mode = 'OBJECT' )

# Painfully make the copied head the active object
dest = bpy.context.selected_objects[0]
srce.select = False
bpy.context.scene.objects.active = dest

# Always clear and recreate the shapekeys
key_blocks = dest.data.shape_keys.key_blocks
for k in key_blocks:
    dest.shape_key_remove(k)
dest.shape_key_add('Basis')

base_key_block = dest.data.shape_keys.reference_key
base_key_values = [item.co for item in base_key_block.data.values()]
key_blocks = dest.data.shape_keys.key_blocks

for key_block_data in data[srce.name]["diffs"]:
    key_block_name = key_block_data["name"]
    key_block = key_blocks.get(key_block_name)
    if not key_block:
        dest.shape_key_add()
        key_blocks[-1].name = key_block_name
    if base_key_block == key_block:
        continue
    key_values = [mathutils.Vector(vec) for vec in key_block_data["values"]]
    if len(key_values) != len(base_key_values):
        raise RuntimeError("3. mesh vertex count is different: " + key_block_name)
    for i in range(len(key_values)):
        key_blocks[key_block_name].data[i].co = key_values[i] + base_key_values[i]