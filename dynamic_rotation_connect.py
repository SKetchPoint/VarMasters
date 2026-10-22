import maya.cmds as cmds

def hide_nurbs_from_render():
    selection = cmds.ls(selection=True, type='transform')
    if not selection:
        cmds.warning("No NURBS surfaces selected.")
        return
    for obj in selection:
        nurbs_shapes = cmds.listRelatives(obj, shapes=True, type='nurbsSurface')
        if nurbs_shapes:
            for shape in nurbs_shapes:
                cmds.setAttr(shape + ".primaryVisibility", 0)
                cmds.setAttr(shape + ".castsShadows", 0)
                cmds.setAttr(shape + ".receiveShadows", 0)
                cmds.setAttr(shape + ".motionBlur", 0)
                cmds.setAttr(shape + ".visibleInReflections", 0)
                cmds.setAttr(shape + ".visibleInRefractions", 0)
                print(f"Set {shape} to be non-renderable.")
        else:
            cmds.warning(f"{obj} does not contain a NURBS surface.")

def match_pivot_rotation_only():
    selection = cmds.ls(selection=True, type='transform')
    if len(selection) < 2:
        cmds.warning("Select two objects: first the target, then the one to match.")
        return
    target = selection[0]
    to_match = selection[1]
    pivot_rotation = cmds.xform(target, query=True, worldSpace=True, rotation=True)
    cmds.xform(to_match, worldSpace=True, preserve=True, pivots=pivot_rotation)
    print(f"Matched pivot rotation of {to_match} to {target} without moving it.")

def inverse_rotate_dynamic(source, target, x_sign, y_sign, z_sign, x_target, y_target, z_target):
    # Create multiplyDivide nodes for each axis
    node_x = cmds.createNode("multiplyDivide", name="X_MD")
    node_y = cmds.createNode("multiplyDivide", name="Y_MD")
    node_z = cmds.createNode("multiplyDivide", name="Z_MD")

    # Set the signs for each axis (invert if negative, keep positive if not)
    cmds.setAttr(node_x + ".input2X", -1 if x_sign == '-' else 1)
    cmds.setAttr(node_y + ".input2X", -1 if y_sign == '-' else 1)
    cmds.setAttr(node_z + ".input2X", -1 if z_sign == '-' else 1)

    # Connect the appropriate rotation axis from the source to the multiplyDivide node
    cmds.connectAttr(f"{source}.rotateX", f"{node_x}.input1X", force=True)
    cmds.connectAttr(f"{source}.rotateY", f"{node_y}.input1X", force=True)
    cmds.connectAttr(f"{source}.rotateZ", f"{node_z}.input1X", force=True)

    # Connect the output of the multiplyDivide node to the target's rotation, based on the selected target axis
    cmds.connectAttr(f"{node_x}.outputX", f"{target}.rotate{x_target}", force=True)
    cmds.connectAttr(f"{node_y}.outputX", f"{target}.rotate{y_target}", force=True)
    cmds.connectAttr(f"{node_z}.outputX", f"{target}.rotate{z_target}", force=True)

    print(f"Connected {source} rotations to {target} with specified signs and target axes.")

def create_ui():
    def on_apply_button_click(*args):
        selection = cmds.ls(selection=True, type='transform')
        if len(selection) < 2:
            cmds.warning("Please select two objects: first the source and then the target.")
            return

        source = selection[0]
        target = selection[1]

        # Get the sign for each axis
        x_sign = cmds.optionMenu("xSignMenu", query=True, value=True)
        y_sign = cmds.optionMenu("ySignMenu", query=True, value=True)
        z_sign = cmds.optionMenu("zSignMenu", query=True, value=True)

        # Get the target axis for each rotation axis
        x_target = cmds.optionMenu("xTargetMenu", query=True, value=True)
        y_target = cmds.optionMenu("yTargetMenu", query=True, value=True)
        z_target = cmds.optionMenu("zTargetMenu", query=True, value=True)

        # Call dynamic connection function with individual signs for each axis and target axes
        inverse_rotate_dynamic(source, target, x_sign, y_sign, z_sign, x_target, y_target, z_target)

    if cmds.window("customUI", exists=True):
        cmds.deleteUI("customUI")
    
    window = cmds.window("customUI", title="Dynamic Rotation Connection", widthHeight=(300, 250))
    cmds.columnLayout(adjustableColumn=True)
    
    # Instructions
    cmds.text("1. Select the source object first, then the target object.")

    # Sign selection dropdown for X, Y, Z axes
    cmds.text("X Axis Sign:")
    cmds.optionMenu("xSignMenu", label="Choose X Sign")
    cmds.menuItem(label="+")
    cmds.menuItem(label="-")

    cmds.text("Y Axis Sign:")
    cmds.optionMenu("ySignMenu", label="Choose Y Sign")
    cmds.menuItem(label="+")
    cmds.menuItem(label="-")

    cmds.text("Z Axis Sign:")
    cmds.optionMenu("zSignMenu", label="Choose Z Sign")
    cmds.menuItem(label="+")
    cmds.menuItem(label="-")

    # Target axis selection dropdowns for X, Y, Z axes
    cmds.text("X Target Axis:")
    cmds.optionMenu("xTargetMenu", label="Target X Axis")
    cmds.menuItem(label="X")
    cmds.menuItem(label="Y")
    cmds.menuItem(label="Z")

    cmds.text("Y Target Axis:")
    cmds.optionMenu("yTargetMenu", label="Target Y Axis")
    cmds.menuItem(label="X")
    cmds.menuItem(label="Y")
    cmds.menuItem(label="Z")

    cmds.text("Z Target Axis:")
    cmds.optionMenu("zTargetMenu", label="Target Z Axis")
    cmds.menuItem(label="X")
    cmds.menuItem(label="Y")
    cmds.menuItem(label="Z")
    
    # Apply button
    cmds.button(label="Apply", command=on_apply_button_click)
    
    cmds.showWindow(window)

create_ui()
#Z-Y
#Y - Z
#X-X