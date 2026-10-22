import maya.cmds as cmds
import math

def chain_on_curve(spread_factor_field, num_points_field, joint_radius_field):
    """
    Creates a joint chain along a selected curve based on user input for spread factor,
    number of joints, and joint radius.
    """
    # Query values from the UI fields
    spread_factor = cmds.floatField(spread_factor_field, query=True, value=True)
    num_points = cmds.intField(num_points_field, query=True, value=True)
    joint_radius = cmds.floatField(joint_radius_field, query=True, value=True)
    
    # Get the selected curve
    selected = cmds.ls(selection=True, transforms=True)
    
    if len(selected) != 1:
        cmds.warning("Please select exactly one curve.")
        return
    
    curve_name = selected[0]
    
    # Check if the selected object is a NURBS curve
    if cmds.objectType(cmds.listRelatives(curve_name, shapes=True)[0]) != "nurbsCurve":
        cmds.error("Selected object is not a NURBS curve.")
        return
    
    # Get the start and end parameter range of the curve
    start_param = cmds.getAttr("{}.minValue".format(curve_name))
    end_param = cmds.getAttr("{}.maxValue".format(curve_name))
    
    # Compute spread-adjusted parameter range
    param_range = (end_param - start_param) * spread_factor
    param_step = param_range / (num_points - 1)
    
    # Create joints along the curve
    cmds.select(clear=True)
    joint_chain = []
    for i in range(num_points):
        # Calculate parameter value for each joint
        param = start_param + i * param_step
        
        # Get position on the curve at the parameter
        pos = cmds.pointOnCurve(curve_name, pr=param, p=True)
        
        # Create joint at the position with specified radius
        joint_name = f"joint_{i + 1:02d}"
        joint = cmds.joint(name=joint_name, position=pos, radius=joint_radius)
        joint_chain.append(joint)
    
    print("Created {} joints along the curve '{}'.".format(num_points, curve_name))
    
def create_controls(positions, normal, size):
    controls = []
    control_names = ["start_CTRL", "mid_CTRL", "end_CTRL"]

    for i, name in enumerate(control_names):
        ctrl = cmds.circle(name=name, normal=normal, radius=size)[0]
        grp = cmds.group(ctrl, name=f"{name}_GRP")
        cmds.xform(grp, worldSpace=True, translation=positions[i])
        controls.append(ctrl)
    return controls

def create_curve_from_joints():
    """
    Creates a curve from the selected joints and returns the curve.
    """
    # Step 1: Get the selected joints
    selected_joints = cmds.ls(selection=True, type="joint")
    
    if len(selected_joints) < 2:
        cmds.warning("Please select at least two joints.")
        return

    # Step 2: Get the world positions of the selected joints
    joint_positions = [cmds.xform(joint, query=True, worldSpace=True, translation=True) for joint in selected_joints]

    # Step 3: Create a curve through the joint positions
    curve = cmds.curve(d=3, p=joint_positions)  # Degree 3 curve through the joint positions
    cmds.rename(curve, "generatedCurve")

    return curve
def cluster_cv_on_selected_curve():
    """
    Clusters each control vertex (CV) on the selected curve and parents the clusters to the curve.
    Assumes one curve is selected in the scene.
    """
    # Step 1: Get the selected object
    selected = cmds.ls(selection=True)
    
    if len(selected) != 1:
        cmds.warning("Please select exactly one curve.")
        return
    
    curve_name = selected[0]
    
    # Step 2: Get the CVs of the curve
    cvs = cmds.ls(f"{curve_name}.cv[*]", flatten=True)
    
    # Step 3: Create clusters for each CV
    clusters = []

    # Create a cluster for each CV
    for cv in cvs:
        cluster = cmds.cluster(cv)[1]
        cmds.parent(cluster, curve_name)
        clusters.append(cluster)

    # Optional: Hide the clusters (cleanup)
    for cluster in clusters:
        cmds.setAttr(f"{cluster}.visibility", 0)

    print(f"Created clusters for {len(cvs)} CVs successfully!")

ROTATE_ORDERS = ['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx']

def select_all_joint_descendants():
    """
    Select all descendants (children and their children) of the currently selected joint(s)
    and include the originally selected joints, then return the list of joints.
    """
    # Get the currently selected joints
    selected_joints = cmds.ls(selection=True, type='joint')

    if not selected_joints:
        cmds.warning("No joint selected. Please select a joint to select its descendants.")
        return []

    # Initialize a list to hold all joints to be selected
    joint_selection = selected_joints[:] 

    # Add all children
    def add_children(joint):
        children = cmds.listRelatives(joint, children=True, type='joint') or []
        for child in children:
            joint_selection.append(child)
            add_children(child)

    # Loop through each selected joint and add its descendants
    for joint in selected_joints:
        add_children(joint)

    return joint_selection

def joint_children_rotation_order(new_order, change_children_joints):
    """
    Changes the rotation order of selected objects to the specified rotation order.
    Supports joints, NURBS circles, curves, and custom controls.

    Args:
    - new_order (str): The rotation order to set. Must be one of the following:
      'xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx'.
    - change_children_joints (bool): If True, changes the rotation order for children
      of selected joints as well.
    """
    if new_order not in ROTATE_ORDERS:
        cmds.warning(f"'{new_order}' is not a valid rotation order. Please choose from {ROTATE_ORDERS}.")
        return

    # Get the currently selected joints, NURBS circles, curves, and custom controls
    selected_objects = cmds.ls(selection=True, type=['joint', 'nurbsCurve', 'transform'])

    if not selected_objects:
        cmds.warning("No valid objects selected. Please select joints, NURBS circles, curves, or custom controls to change their rotation order.")
        return

    # Get all descendants if change_children_joints is True
    if change_children_joints:
        descendants = []
        for obj in selected_objects:
            descendants += cmds.listRelatives(obj, allDescendents=True, type='transform') or []
        selected_objects = list(set(selected_objects + descendants))

    def change_rotation_order(obj):
        """Change the rotation order of a given object."""
        if cmds.objExists(obj):
            print(f"Setting rotation order of {obj} to {new_order} (index {ROTATE_ORDERS.index(new_order)})")
            cmds.setAttr(f"{obj}.rotateOrder", ROTATE_ORDERS.index(new_order))
            print(f"Changed rotation order of {obj} to {new_order}.")
        else:
            cmds.warning(f"Object '{obj}' does not exist in the scene.")

    for obj in selected_objects:
        change_rotation_order(obj)

    return
def change_curve_rotation_order(new_order):
    """
    Changes the rotation order of selected curves or transform objects in Maya.
    
    Args:
    - new_order (str): The rotation order to set. Must be one of the following:
      'xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx'.
    """
    if new_order not in ROTATE_ORDERS:
        cmds.warning(f"'{new_order}' is not a valid rotation order. Please choose from {ROTATE_ORDERS}.")
        return
    
    # Get the currently selected curves or transform objects for controls
    selected_curves = cmds.ls(selection=True, type='transform')
    
    if not selected_curves:
        cmds.warning("No curves or transform objects selected. Please select curves to change their rotation order.")
        return
    
    for curve in selected_curves:
        if cmds.objExists(curve):
            print(f"Setting rotation order of {curve} to {new_order} (index {ROTATE_ORDERS.index(new_order)})")
            cmds.setAttr(f"{curve}.rotateOrder", ROTATE_ORDERS.index(new_order))
            print(f"Changed rotation order of {curve} to {new_order}.")
        else:
            cmds.warning(f"Object '{curve}' does not exist in the scene.")
    return