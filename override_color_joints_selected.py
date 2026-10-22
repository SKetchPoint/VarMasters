import maya.cmds as cmds

def set_override_color_index(color_index=None, enable_override=True, include_shapes=True):
    """
    Overrides the display color of all selected joints/transforms using Maya's color index table (0-31).
    """
    selection = cmds.ls(selection=True, long=True)
    if not selection:
        cmds.warning("Select at least one joint or transform node.")
        return

    # Collect nodes (and their shapes if specified)
    nodes_to_color = list(selection)
    if include_shapes:
        shapes = cmds.listRelatives(selection, shapes=True, fullPath=True) or []
        nodes_to_color.extend(shapes)

    cmds.undoInfo(openChunk=True)
    try:
        for node in nodes_to_color:
            # Enable/Disable drawing overrides
            if cmds.attributeQuery("overrideEnabled", node=node, exists=True):
                cmds.setAttr(f"{node}.overrideEnabled", enable_override)

            # Assign color index
            if enable_override and color_index is not None:
                if cmds.attributeQuery("overrideColor", node=node, exists=True):
                    cmds.setAttr(f"{node}.overrideColor", color_index)

        status_msg = f"Set override color index to {color_index}" if enable_override else "Disabled display overrides"
        print(f"{status_msg} on {len(nodes_to_color)} object(s).")
    finally:
        cmds.undoInfo(closeChunk=True)


class JointColorOverrideUI:
    WINDOW_NAME = "jointColorOverrideWin"

    # Common rigging palette: (Label, Index, RGB preview)
    QUICK_PALETTE = [
        ("Left (Blue)", 6, (0.0, 0.0, 1.0)),
        ("Right (Red)", 13, (1.0, 0.0, 0.0)),
        ("Center (Yellow)", 17, (1.0, 1.0, 0.0)),
        ("Root / Main (Green)", 14, (0.0, 1.0, 0.0)),
        ("Secondary (Cyan)", 18, (0.0, 1.0, 1.0)),
        ("Tertiary (Magenta)", 9, (0.8, 0.1, 0.8)),
        ("Neutral (White)", 16, (1.0, 1.0, 1.0)),
        ("Dark Gray", 2, (0.25, 0.25, 0.25))
    ]

    def __init__(self):
        self.build_ui()

    def build_ui(self):
        if cmds.window(self.WINDOW_NAME, exists=True):
            cmds.deleteUI(self.WINDOW_NAME, window=True)

        self.window = cmds.window(
            self.WINDOW_NAME,
            title="Joint Color Override",
            widthHeight=(320, 370),
            sizeable=False
        )

        main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnOffset=["both", 10])

        # -------------------------------------------------------------
        # Quick Rigging Presets
        # -------------------------------------------------------------
        cmds.frameLayout(label="Standard Rigging Presets", collapsable=False, parent=main_layout)
        grid = cmds.gridLayout(numberOfColumns=2, cellWidthHeight=(145, 30), parent=main_layout)

        for label, idx, rgb in self.QUICK_PALETTE:
            cmds.button(
                label=label,
                backgroundColor=rgb,
                command=lambda *args, i=idx: self.apply_color(i),
                parent=grid
            )

        # -------------------------------------------------------------
        # Manual Index Slider (0-31)
        # -------------------------------------------------------------
        cmds.frameLayout(label="Manual Color Index (0 - 31)", collapsable=False, parent=main_layout)
        slider_col = cmds.columnLayout(adjustableColumn=True, rowSpacing=6)

        self.index_slider = cmds.intSliderGrp(
            field=True,
            minValue=0,
            maxValue=31,
            value=6,
            columnWidth3=(40, 50, 180),
            parent=slider_col
        )

        cmds.button(
            label="Apply Slider Index",
            height=30,
            backgroundColor=(0.3, 0.4, 0.5),
            command=self.apply_slider_index,
            parent=slider_col
        )

        # -------------------------------------------------------------
        # Reset / Disable Overrides
        # -------------------------------------------------------------
        cmds.separator(height=10, style="in", parent=main_layout)
        cmds.button(
            label="Clear Overrides (Reset to Default)",
            height=30,
            backgroundColor=(0.35, 0.35, 0.35),
            command=lambda *args: set_override_color_index(enable_override=False),
            parent=main_layout
        )

        cmds.showWindow(self.window)

    def apply_color(self, index):
        set_override_color_index(color_index=index, enable_override=True)

    def apply_slider_index(self, *args):
        idx = cmds.intSliderGrp(self.index_slider, query=True, value=True)
        self.apply_color(idx)


# Launch UI
JointColorOverrideUI()