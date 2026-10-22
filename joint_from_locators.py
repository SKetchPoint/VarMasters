import maya.cmds as cmds
import re

class JointFromLocatorsUI:
    WINDOW_NAME = "locatorJointCreatorWin"

    def __init__(self):
        self.build_ui()

    def build_ui(self):
        if cmds.window(self.WINDOW_NAME, exists=True):
            cmds.deleteUI(self.WINDOW_NAME, window=True)

        self.window = cmds.window(
            self.WINDOW_NAME,
            title="Joint Chain Generator",
            widthHeight=(360, 420),
            sizeable=False
        )

        main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

        # Hierarchy Section
        cmds.frameLayout(label="Hierarchy & Structure", collapsable=False, parent=main_layout)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=6)
        self.match_hierarchy_chk = cmds.checkBox(
            label="Mirror Locator Hierarchy",
            value=True,
            annotation="Build joints preserving parent-child relations from locators."
        )
        self.unreal_root_chk = cmds.checkBox(
            label="Enforce Single Root (Unreal Rules)",
            value=True,
            annotation="Ensures only one root joint exists; creates a designated root if multiple top-level locators are selected."
        )
        cmds.setParent(main_layout)

        # Orientation Section
        cmds.frameLayout(label="Joint Orientation", collapsable=False, parent=main_layout)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=6)
        
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(130, 200), adjustableColumn=2)
        cmds.text(label="Primary / Aim Axis:")
        self.aim_axis_grp = cmds.optionMenu()
        for axis in ["xyz", "xzy", "yxz", "yzx", "zxy", "zyx"]:
            cmds.menuItem(label=axis)
        cmds.setParent("..")

        cmds.rowLayout(numberOfColumns=2, columnWidth2=(130, 200), adjustableColumn=2)
        cmds.text(label="Secondary / Up Axis:")
        self.up_axis_grp = cmds.optionMenu()
        for up in ["yup", "ydown", "zup", "zdown", "xup", "xdown"]:
            cmds.menuItem(label=up)
        cmds.setParent("..")

        cmds.rowLayout(numberOfColumns=2, columnWidth2=(130, 200), adjustableColumn=2)
        cmds.text(label="Rotation Order:")
        self.rot_order_menu = cmds.optionMenu()
        for ro in ["xyz", "yzx", "zxy", "xzy", "yxz", "zyx"]:
            cmds.menuItem(label=ro)
        cmds.setParent("..")

        self.end_joint_zero_chk = cmds.checkBox(
            label="Zero-out End Joints (World/Parent Align)",
            value=True,
            annotation="Aligns leaf joints / tips to world (0 orientation) or parent rotation rather than aiming nowhere."
        )
        cmds.setParent(main_layout)

        # Execution
        cmds.separator(height=10, style="in", parent=main_layout)
        cmds.button(
            label="Generate Joints",
            height=35,
            backgroundColor=(0.25, 0.45, 0.35),
            command=self.execute,
            parent=main_layout
        )

        cmds.showWindow(self.window)

    def _format_joint_name(self, node_name):
        """Strips '_LOC' / '_loc' suffix and appends '_JNT'."""
        short_name = node_name.split("|")[-1]
        base_name = re.sub(r'(?i)_loc$', '', short_name)
        return f"{base_name}_JNT"

    def execute(self, *args):
        selection = cmds.ls(selection=True, type="transform")
        if not selection:
            cmds.warning("Select at least one locator or transform node.")
            return

        match_hierarchy = cmds.checkBox(self.match_hierarchy_chk, query=True, value=True)
        enforce_unreal = cmds.checkBox(self.unreal_root_chk, query=True, value=True)
        aim_axis = cmds.optionMenu(self.aim_axis_grp, query=True, value=True)
        up_axis = cmds.optionMenu(self.up_axis_grp, query=True, value=True)
        rot_order_str = cmds.optionMenu(self.rot_order_menu, query=True, value=True)
        zero_end_joints = cmds.checkBox(self.end_joint_zero_chk, query=True, value=True)

        rot_order_map = {"xyz": 0, "yzx": 1, "zxy": 2, "xzy": 3, "yxz": 4, "zyx": 5}
        rot_order_val = rot_order_map.get(rot_order_str, 0)

        cmds.undoInfo(openChunk=True)
        try:
            created_joints = {}
            top_level_joints = []

            sorted_nodes = self._sort_by_hierarchy_depth(selection)

            # 1. Create Joints at World Positions
            cmds.select(clear=True)
            for node in sorted_nodes:
                pos = cmds.xform(node, query=True, worldSpace=True, translation=True)
                joint_name = self._format_joint_name(node)
                jnt = cmds.joint(name=joint_name, position=pos)
                cmds.setAttr(f"{jnt}.rotateOrder", rot_order_val)
                created_joints[node] = jnt
                cmds.select(clear=True)

            # 2. Re-parenting pass
            if match_hierarchy:
                for node in sorted_nodes:
                    parent_node = cmds.listRelatives(node, parent=True, type="transform")
                    if parent_node and parent_node[0] in created_joints:
                        cmds.parent(created_joints[node], created_joints[parent_node[0]])
                    else:
                        top_level_joints.append(created_joints[node])
            else:
                top_level_joints = list(created_joints.values())

            # 3. Orient Joints
            if match_hierarchy:
                for root_jnt in top_level_joints:
                    cmds.joint(
                        root_jnt,
                        edit=True,
                        orientJoint=aim_axis,
                        secondaryAxisOrient=up_axis,
                        children=True,
                        zeroScaleOrient=True
                    )

                if zero_end_joints:
                    for jnt in created_joints.values():
                        children = cmds.listRelatives(jnt, children=True, type="joint")
                        if not children:
                            cmds.setAttr(f"{jnt}.jointOrientX", 0)
                            cmds.setAttr(f"{jnt}.jointOrientY", 0)
                            cmds.setAttr(f"{jnt}.jointOrientZ", 0)

            # 4. Unreal Root Validation
            if enforce_unreal and len(top_level_joints) > 1:
                unreal_root = cmds.joint(name="root_JNT", position=(0, 0, 0))
                cmds.setAttr(f"{unreal_root}.rotateOrder", rot_order_val)
                for jnt in top_level_joints:
                    cmds.parent(jnt, unreal_root)
                top_level_joints = [unreal_root]

            cmds.select(top_level_joints)
            print(f"Generated {len(created_joints)} joints successfully.")

        finally:
            cmds.undoInfo(closeChunk=True)

    def _sort_by_hierarchy_depth(self, nodes):
        """Sort nodes so parents are always evaluated before their children."""
        def get_depth(node):
            full_path = cmds.ls(node, long=True)[0]
            return full_path.count("|")
        return sorted(nodes, key=get_depth)


# Launch UI
JointFromLocatorsUI()