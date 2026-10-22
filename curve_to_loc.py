import maya.cmds as cmds

def create_locators_along_curve(
    curve_node=None,
    locator_count=5,
    mode="parametric",  # "parametric" (recommended) or "cv"
    aim_axis=(1, 0, 0),     # Primary aim down chain (+X)
    up_axis=(0, 0, 1),      # Secondary up vector (+Z dorsal for bat wings)
    rot_order="xzy",
    base_name="batWing_strutA",
    build_hierarchy=True
):
    """
    Spawns and orients a chain of locators along a selected NURBS curve.
    
    Args:
        curve_node (str): Name of the NURBS curve. If None, uses active selection.
        locator_count (int): Number of locators to generate (used in parametric mode).
        mode (str): 'parametric' distributes evenly on curve; 'cv' places at control vertices.
        aim_axis (tuple): Vector direction to aim at child locator.
        up_axis (tuple): Vector direction for secondary up alignment.
        rot_order (str): Locator rotate order string ('xyz', 'xzy', 'yzx', etc.).
        base_name (str): Base name prefix for the generated locators.
        build_hierarchy (bool): Whether to parent the locators sequentially.
    """
    if not curve_node:
        sel = cmds.ls(selection=True)
        if not sel:
            cmds.error("Please select a NURBS curve.")
            return
        curve_node = sel[0]

    # Verify curve shape
    shapes = cmds.listRelatives(curve_node, shapes=True, type="nurbsCurve")
    if not shapes:
        if cmds.nodeType(curve_node) == "nurbsCurve":
            curve_shape = curve_node
        else:
            cmds.error(f"'{curve_node}' is not a valid NURBS curve.")
            return
    else:
        curve_shape = shapes[0]

    rot_order_map = {"xyz": 0, "yzx": 1, "zxy": 2, "xzy": 3, "yxz": 4, "zyx": 5}
    rot_val = rot_order_map.get(rot_order.lower(), 0)

    cmds.undoInfo(openChunk=True)
    try:
        positions = []

        if mode.lower() == "cv":
            cv_count = cmds.getAttr(f"{curve_shape}.controlPoints", size=True)
            for i in range(cv_count):
                pos = cmds.pointPosition(f"{curve_shape}.cv[{i}]", world=True)
                positions.append(pos)
        else:
            if locator_count < 2:
                locator_count = 2

            poc_node = cmds.createNode("pointOnCurveInfo")
            cmds.connectAttr(f"{curve_shape}.worldSpace[0]", f"{poc_node}.inputCurve")
            cmds.setAttr(f"{poc_node}.turnOnPercentage", 1)

            step = 1.0 / float(locator_count - 1)
            for i in range(locator_count):
                param = i * step
                cmds.setAttr(f"{poc_node}.parameter", param)
                pos = cmds.getAttr(f"{poc_node}.position")[0]
                positions.append(pos)

            cmds.delete(poc_node)

        # 1. Create Locators
        created_locators = []
        for i, pos in enumerate(positions):
            loc_name = f"{base_name}_{i+1:02d}_LOC"
            loc = cmds.spaceLocator(name=loc_name)[0]
            cmds.xform(loc, worldSpace=True, translation=pos)
            cmds.setAttr(f"{loc}.rotateOrder", rot_val)
            created_locators.append(loc)

        # 2. Orient Locators down the chain using Aim Constraints
        for i in range(len(created_locators) - 1):
            current_loc = created_locators[i]
            target_loc = created_locators[i + 1]

            temp_constraint = cmds.aimConstraint(
                target_loc,
                current_loc,
                aimVector=aim_axis,
                upVector=up_axis,
                worldUpType="scene"
            )
            cmds.delete(temp_constraint)

        # Match the last locator's orientation to its predecessor
        if len(created_locators) > 1:
            prev_rot = cmds.xform(created_locators[-2], query=True, rotation=True, worldSpace=True)
            cmds.xform(created_locators[-1], rotation=prev_rot, worldSpace=True)

        # 3. Build Hierarchy (Child -> Parent)
        if build_hierarchy and len(created_locators) > 1:
            for i in reversed(range(1, len(created_locators))):
                cmds.parent(created_locators[i], created_locators[i - 1])

        cmds.select(created_locators[0])
        print(f"Generated {len(created_locators)} locators along curve successfully.")

    finally:
        cmds.undoInfo(closeChunk=True)


# Usage:
# Select a curve in Maya and execute:
create_locators_along_curve(
    locator_count=5,
    mode="parametric",     # "parametric" (even arc-length) or "cv"
    aim_axis=(1, 0, 0),    # +X Aim
    up_axis=(0, 0, 1),     # +Z Up
    rot_order="xzy",
    base_name="tng",
    build_hierarchy=True
)