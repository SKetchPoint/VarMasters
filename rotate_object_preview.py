import maya.cmds as cmds

def duplicate_and_rotate(obj_name, translation=50, rotation_step=45, x_rotation_step=45):
    if not cmds.objExists(obj_name):
        print(f"Object '{obj_name}' not found.")
        return
    
    # Freeze transformations on the original object before starting
    cmds.makeIdentity(obj_name, apply=True, translate=True, rotate=True, scale=True, normal=False)
    
    # Rotate in steps until a full 360 degrees
    current_translation = translation
    current_height = translation
    for y_angle in range(0, 360, rotation_step):
        # Duplicate the original object for the Y rotation
        y_rotated_obj = cmds.duplicate(obj_name, name=f"{obj_name}_Y_{y_angle}")[0]
        
        # Freeze the duplicate's transformations
        cmds.makeIdentity(y_rotated_obj, apply=True, translate=True, rotate=True, scale=True, normal=False)
        
        # Apply translation (relative to the original each time)
        cmds.move(current_translation, 0, 0, y_rotated_obj, relative=True)
        
        # Apply Y-axis rotation
        cmds.rotate(0, y_angle, 0, y_rotated_obj, relative=True)
        current_translation += translation
        
        # Now create X-axis rotations for this Y-rotated copy
        current_sub_height = current_height
        for x_angle in range(0, 360, x_rotation_step):
            x_rotated_obj = cmds.duplicate(y_rotated_obj, name=f"{y_rotated_obj}_X_{x_angle}")[0]
            cmds.move(0, current_sub_height, 0, x_rotated_obj, relative=True)
            cmds.rotate(x_angle, 0, 0, x_rotated_obj, relative=True)
            current_sub_height += translation
            print(f"Created {x_rotated_obj} at +{current_translation} units X and +{current_sub_height} units Y with Y rotation {y_angle} and X rotation {x_angle} degrees.")

# Replace 'SQR' with the name of your model
duplicate_and_rotate('Laptop')
