import maya.cmds as cmds

def generate_lip_locators_from_loop(
    head_locator="head_LOC", 
    jaw_locator="jaw_LOC", 
    group_under_locator_hierarchy=True
):
    """
    Converts a selected mouth edge loop into an 8-point facial locator ring.
    Parents the upper lip locators to head_LOC and lower lip locators to jaw_LOC.
    """
    sel_edges = cmds.filterExpand(selectionMask=32)
    if not sel_edges:
        cmds.error("Please select a continuous closed polygon edge loop around the mouth.")
        return

    cmds.undoInfo(openChunk=True)
    try:
        # polyToCurve operates on active selection
        cmds.select(sel_edges, replace=True)
        temp_curve = cmds.polyToCurve(
            name="temp_lip_loop_CRV",
            form=2,  # Closed/Periodic
            degree=3
        )[0]

        # Rebuild curve uniformly across 8 spans
        rebuilt_curve = cmds.rebuildCurve(
            temp_curve,
            name="lip_uniform_CRV",
            replaceOriginal=True,
            rebuildType=0,
            spans=8,
            degree=3,
            keepRange=0
        )[0]

        # 2. Sample 8 points along the perimeter
        poc_node = cmds.createNode("pointOnCurveInfo")
        cmds.connectAttr(f"{rebuilt_curve}.worldSpace[0]", f"{poc_node}.inputCurve")
        cmds.setAttr(f"{poc_node}.turnOnPercentage", 1)

        raw_points = []
        for i in range(8):
            param = float(i) / 8.0
            cmds.setAttr(f"{poc_node}.parameter", param)
            pos = cmds.getAttr(f"{poc_node}.position")[0]
            raw_points.append(pos)

        cmds.delete([poc_node, rebuilt_curve])

        # 3. Categorize positions anatomically
        # Sort by X: Left (X > 0) and Right (X < 0)
        sorted_by_x = sorted(raw_points, key=lambda p: p[0])
        right_corner_pos = sorted_by_x[0]   # Min X
        left_corner_pos = sorted_by_x[-1]   # Max X

        remaining_pts = [p for p in raw_points if p != right_corner_pos and p != left_corner_pos]

        # Split remaining into lower (lower Y) and upper (higher Y)
        sorted_by_y = sorted(remaining_pts, key=lambda p: p[1])
        lower_points = sorted_by_y[:3]
        upper_points = sorted_by_y[3:]

        # Sort Upper: [Right, Mid, Left]
        upper_points = sorted(upper_points, key=lambda p: p[0])
        upper_R = upper_points[0]
        upper_mid = upper_points[1]
        upper_L = upper_points[2]

        # Sort Lower: [Right, Mid, Left]
        lower_points = sorted(lower_points, key=lambda p: p[0])
        lower_R = lower_points[0]
        lower_mid = lower_points[1]
        lower_L = lower_points[2]

        # Define parent target mappings
        lip_mapping = [
            ("lip_upper_mid", upper_mid, head_locator),
            ("lip_upper_L", upper_L, head_locator),
            ("lip_upper_R", upper_R, head_locator),
            ("lip_lower_mid", lower_mid, jaw_locator),
            ("lip_lower_L", lower_L, jaw_locator),
            ("lip_lower_R", lower_R, jaw_locator),
            ("lip_corner_L", left_corner_pos, head_locator),
            ("lip_corner_R", right_corner_pos, head_locator)
        ]

        created_locators = []

        # 4. Create Locators and Parent into Hierarchy
        for base_name, pos, parent_node in lip_mapping:
            loc_name = f"{base_name}_LOC"
            
            if cmds.objExists(loc_name):
                cmds.delete(loc_name)

            loc = cmds.spaceLocator(name=loc_name)[0]
            cmds.xform(loc, worldSpace=True, translation=pos)
            
            # Set Rotation Order to ZYX
            cmds.setAttr(f"{loc}.rotateOrder", 5)

            # Parent to head_LOC or jaw_LOC if specified and existing
            if group_under_locator_hierarchy and cmds.objExists(parent_node):
                cmds.parent(loc, parent_node)

            created_locators.append(loc)

        cmds.select(created_locators)
        print(f"Generated {len(created_locators)} mouth locators successfully.")

    finally:
        cmds.undoInfo(closeChunk=True)


# --- USAGE ---
# Select the mouth edge loop on your bat mesh and run:
generate_lip_locators_from_loop(
    head_locator="head_LOC", 
    jaw_locator="jaw_LOC", 
    group_under_locator_hierarchy=True
)