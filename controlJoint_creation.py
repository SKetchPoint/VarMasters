import maya.cmds as cmds
import maya.api.OpenMaya as om
def create_nurbs_circle_around_joint(selected_axis, size, ctrl_connect):
    """
    Creates trial nurbs circle for quick testing
    
    :param selected_axsis: orientation of the circle if its laying down or standing up
    :param size: scale of the control to change to
    :param ctrl_connect: true or false for also adding orient constraint
    """
    # Check if there is a joint selected
    selected = cmds.ls(selection=True, type="joint")
    if not selected:
        cmds.confirmDialog(title="Error", message="Please select a joint.", button=["OK"])
        return
    
    joint = selected[0]
    
    # Determine the normal vector based on the selected axis
    if selected_axis == "X Axis":
        normal = [1, 0, 0]
    elif selected_axis == "Y Axis":
        normal = [0, 1, 0]
    elif selected_axis == "Z Axis":
        normal = [0, 0, 1]
    else:
        cmds.confirmDialog(title="Error", message="Invalid axis selected.", button=["OK"])
        return

    # Create a NURBS circle at the joint's position
    circle_name = joint + '_CTRL'
    circle = cmds.circle(name=circle_name, normal=normal)[0]
    joint_position = cmds.xform(joint, query=True, worldSpace=True, translation=True)
    cmds.xform(circle, worldSpace=True, translation=joint_position)
    cmds.scale(size, size, size, circle)
    cmds.makeIdentity(circle, apply=True, rotate=True, scale=True, translate=True)
    
    #if ctrlConnect is true, creates orient constrain to joint, else just creates the circle ctrl
    if ctrl_connect:
        cmds.orientConstraint(circle, joint, maintainOffset=True)
    
    # Success message
    cmds.confirmDialog(title="Success", message="NURBS circle created around joint.", button=["OK"])

def group_nurbs_curve(curve_name, group_name):
    """
    Create Offset and auto groups for the control
    
    :param curve_name: The name of the NURBS curve.
    :param group_name: Name of the group that is created.
    """
    # Check if the specified curve exists
    if not cmds.objExists(curve_name):
        cmds.confirmDialog(title="Error", message=f"'{curve_name}' does not exist.", button=["OK"])
        return
    
    # Ensure the object is a NURBS curve transform + if repeated
    shape = cmds.listRelatives(curve_name, shapes=True, type="nurbsCurve")
    if not shape:
        cmds.confirmDialog(title="Error", message=f"'{curve_name}' is not a valid NURBS curve transform.", button=["OK"])
        return
    
    if cmds.objExists(group_name):
        cmds.confirmDialog(title="Error", message=f"'{group_name}' already exists.", button=["OK"])
        return
    
    # Create the group with the specified name, parented
    group = cmds.group(empty=True, name=group_name)
    cmds.parent(curve_name, group)
    curve_position = cmds.xform(curve_name, query=True, worldSpace=True, translation=True)
    cmds.xform(group, worldSpace=True, translation=curve_position)
    
    return group

def recolor_nurbs_curve(curve_name, color_index):
    """
    Recolors a specified NURBS curve in Maya.
    
    :param curve_name: The name of the NURBS curve.
    :param color_index: The color index for Maya's color settings (1-31).
    """
    if not cmds.objExists(curve_name):
        cmds.confirmDialog(title="Error", message=f"'{curve_name}' does not exist.", button=["OK"])
        return
    
    # Ensure it's a NURBS curve
    shape = cmds.listRelatives(curve_name, shapes=True, type="nurbsCurve")
    if not shape:
        cmds.confirmDialog(title="Error", message=f"'{curve_name}' is not a NURBS curve.", button=["OK"])
        return

    # Set the color override
    shape_node = shape[0]
    cmds.setAttr(f"{shape_node}.overrideEnabled", 1)  # Enable override
    cmds.setAttr(f"{shape_node}.overrideColor", color_index)  # Set color
    
def hex_to_rgb(hex_color):
    """
    Convert a hexadecimal color string to RGB values (0.0 to 1.0).
    
    :param hex_color: Hexadecimal color string, e.g., "#FF5733".
    :return: A tuple of RGB values.
    """
    hex_color = hex_color.lstrip('#')
    
    # Convert the hex string to RGB components + checks error if invalid input
    if len(hex_color) == 6:
        r = int(hex_color[0:2], 16) / 255.0
        g = int(hex_color[2:4], 16) / 255.0
        b = int(hex_color[4:6], 16) / 255.0
        return r, g, b
    else:
        cmds.error(f"Invalid hex color: {hex_color}. Must be a 6-digit hexadecimal code.")
        return

def recolor_nurbs_shapes(hex_color):
    """
    Recolor selected NURBS using a hex color code.
    :Param hex_color: Hexadecimal color string, e.g., "#FF5733".
    """
    # Convert hex color to RGB tuple
    color = hex_to_rgb(hex_color)
    if color is None:
        return
    
    r, g, b = color

    selection = cmds.ls(selection=True, type='transform')
    if not selection:
        cmds.warning("No objects selected. Please select NURBS shapes to recolor.")
        return

    for obj in selection:
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        for shape in shapes:
            if cmds.nodeType(shape) in ['nurbsCurve', 'nurbsSurface']:
                # Enable override color+ set
                cmds.setAttr(f"{shape}.overrideEnabled", 1)
                cmds.setAttr(f"{shape}.overrideRGBColors", 1)
                cmds.setAttr(f"{shape}.overrideColorRGB", r, g, b)
                print(f"Recolored: {shape}")

def create_locator_at_pivot():
    selection = cmds.ls(selection=True, long=True)
    if not selection:
        cmds.warning("Please select a curve or circle.")
        return
    for obj in selection:
        pivot = cmds.xform(obj, query=True, worldSpace=True, rotatePivot=True)
        locator = cmds.spaceLocator()[0]
        cmds.xform(locator, worldSpace=True, translation=pivot)
        print(f"Locator created at pivot point of {obj}: {pivot}")
        
def color_joints_with_hex(hex_color):
    """
    Colors the selected joints in Maya using a specified hex color.
    
    Args:
        hex_color (str): Hex color string (e.g., "#FF5733"). Default is orange.
    """
    selected_joints = cmds.ls(selection=True, type="joint")
    
    if not selected_joints:
        cmds.warning("No joints selected.")
        return
    
    r, g, b = hex_to_rgb(hex_color)
    
    for joint in selected_joints:
        # Enable override color and set RGB values
        cmds.setAttr(f"{joint}.overrideEnabled", 1)
        cmds.setAttr(f"{joint}.overrideRGBColors", 1)  # Enable RGB override
        cmds.setAttr(f"{joint}.overrideColorRGB", r, g, b)
    
    print(f"Colored {len(selected_joints)} joint(s) with hex color {hex_color}.")


def create_nurbs_control_with_joint(nurbs_surface, joint):
    """
    Takes an existing NURBS surface and a joint to create a control with proper grouping, 
    positions the group at the joint's world position, orients it, and assigns the joint's 
    rotation order to the control.
    
    :param nurbs_surface: The name of the NURBS surface to use as a control.
    :param joint: The name of the joint to create the control for.
    :param ctrlConnect: Whether to connect the control to the joint with an orient constraint (default is True).
    """
    # Ensure the specified NURBS surface and joint exist
    if not cmds.objExists(nurbs_surface) or not cmds.objExists(joint):
        cmds.confirmDialog(title="Error", message="Please provide valid NURBS surface and joint names.", button=["OK"])
        return
    
    # Create a group for offset
    group_name = nurbs_surface + '_OFFSET'
    group = cmds.group(empty=True, name=group_name)
    
    # Position the group at the joint's world position
    joint_position = cmds.xform(joint, query=True, worldSpace=True, translation=True)
    cmds.xform(group, worldSpace=True, translation=joint_position)
    cmds.parent(nurbs_surface, group)
    cmds.makeIdentity(nurbs_surface, apply=True, scale=True)
    
    # Reset any translations +match
    cmds.xform(nurbs_surface, translation=(0, 0, 0))
    cmds.matchTransform(group, joint, pos=True, rot=True)
    
    # Set the NURBS surface's rotation order to match the joint's rotation order
    joint_rotation_order = cmds.getAttr(joint + ".rotateOrder")
    cmds.setAttr(nurbs_surface + ".rotateOrder", joint_rotation_order)
    print("Grouping control created")
    return


def create_fk_control_with_group(selected_axis="X Axis", size=20, ctrlConnect=True):
    """
    Creates an FK control for the selected joint with proper grouping and constraints, 
    scales the control, and then freezes the transforms.
    
    :param selected_axis: The axis to align the control circle (default is "X Axis").
    :param size: The size of the control (default is 20).
    :param ctrlConnect: Whether to connect the control to the joint (default is True).
    """
    # Ensure a joint is selected
    selected = cmds.ls(selection=True, type="joint")
    if not selected:
        cmds.confirmDialog(title="Error", message="Please select a joint.", button=["OK"])
        return
    
    joint = selected[0]
    
    # Determine the normal vector based on the selected axis
    if selected_axis == "X Axis":
        normal = [1, 0, 0]
    elif selected_axis == "Y Axis":
        normal = [0, 1, 0]
    elif selected_axis == "Z Axis":
        normal = [0, 0, 1]
    else:
        cmds.confirmDialog(title="Error", message="Invalid axis selected.", button=["OK"])
        return
    
    # Create the control circle
    circle_name = joint + '_CTRL'
    circle = cmds.circle(name=circle_name, normal=normal)[0]
    
   
    cmds.scale(size, size, size, circle)
   
    create_nurbs_control_with_joint(circle, joint)
    # Create an orient constraint if specified
    if ctrlConnect:
        cmds.orientConstraint(circle, joint, maintainOffset=True)
    
    cmds.confirmDialog(title="Success", message="FK control created and scaled with proper grouping.", button=["OK"])
    
def apply_group_transform_to_curve_and_delete_group(group_name, curve_name):
    """
    Transfers the transform of a group to the offsetParentMatrix of a NURBS curve,
    unparents the curve, and deletes the group.
    
    Args:
        group_name (str): Name of the group.
        curve_name (str): Name of the NURBS curve.
    """
    if not cmds.objExists(group_name) or not cmds.objExists(curve_name):
        cmds.error("Either the group or the curve does not exist.")
        return
    
    # Get the world matrix of the group
    group_matrix = cmds.xform(group_name, query=True, matrix=True, worldSpace=True)
    group_m_matrix = om.MMatrix(group_matrix)
    
    # Get the current parent offset matrix of the curve
    offset_matrix_plug = cmds.getAttr(f"{curve_name}.offsetParentMatrix")
    offset_m_matrix = om.MMatrix(offset_matrix_plug)
    
    # Combine the group transform matrix with the existing offset matrix of the curve
    new_offset_matrix = group_m_matrix * offset_m_matrix
    
    # Apply the combined matrix as the new offsetParentMatrix of the curve
    cmds.setAttr(f"{curve_name}.offsetParentMatrix", list(new_offset_matrix), type="matrix")
    
    # Reset translate, rotate, and scale of the curve to zero
    cmds.setAttr(f"{curve_name}.translate", 0, 0, 0)
    cmds.setAttr(f"{curve_name}.rotate", 0, 0, 0)
    cmds.setAttr(f"{curve_name}.scale", 1, 1, 1)
    
    # Unparent the curve from the group
    cmds.parent(curve_name, world=True)
    
    # Delete the group
    cmds.delete(group_name)
    
    print(f"Group '{group_name}' deleted, and its transform applied to '{curve_name}'.")
def apply_group_transform_to_children_and_delete_selected_group():
    """
    Transfers the transform of a selected group to the offsetParentMatrix of all its children,
    unparents the children, and deletes the group.
    
    Raises an error if no group is selected or if the selection is invalid.
    """
    # Get the currently selected object
    selection = cmds.ls(selection=True, long=True)
    
    if not selection:
        cmds.error("No group selected. Please select a group.")
        return
    
    if len(selection) > 1:
        cmds.error("Multiple objects selected. Please select only one group.")
        return
    
    group_name = selection[0]
    
    # Check if the selected object is a group (must have children)
    children = cmds.listRelatives(group_name, children=True, fullPath=True) or []
    if not children:
        cmds.warning(f"'{group_name}' has no children.")
        return
    
    # Get the world matrix of the group
    group_matrix = cmds.xform(group_name, query=True, matrix=True, worldSpace=True)
    group_m_matrix = om.MMatrix(group_matrix)
    
    for child in children:
        # Get the current parent offset matrix of the child
        offset_matrix_plug = cmds.getAttr(f"{child}.offsetParentMatrix")
        offset_m_matrix = om.MMatrix(offset_matrix_plug)
        
        # Combine the group transform matrix with the child's offset matrix
        new_offset_matrix = group_m_matrix * offset_m_matrix
        
        # Apply the combined matrix as the new offsetParentMatrix of the child
        cmds.setAttr(f"{child}.offsetParentMatrix", list(new_offset_matrix), type="matrix")
        
        # Reset translate, rotate, and scale of the child to zero
        cmds.setAttr(f"{child}.translate", 0, 0, 0)
        cmds.setAttr(f"{child}.rotate", 0, 0, 0)
        cmds.setAttr(f"{child}.scale", 1, 1, 1)
        
        # Unparent the child from the group
        cmds.parent(child, world=True)
    
    # Delete the group after processing its children
    cmds.delete(group_name)
    
    print(f"Group '{group_name}' deleted, and transforms applied to its children.")