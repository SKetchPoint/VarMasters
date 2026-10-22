import maya.cmds as cmds

WINDOW_NAME = "suffixToolUI"

def apply_suffix():
    geo_suffix = cmds.textField("geoField", q=True, text=True)
    grp_suffix = cmds.textField("grpField", q=True, text=True)
    ctrl_suffix = cmds.textField("ctrlField", q=True, text=True)
    loc_suffix = cmds.textField("locField", q=True, text=True)

    selection = cmds.ls(selection=True, long=True)

    if not selection:
        cmds.warning("No objects selected.")
        return

    for obj in selection:
        short_name = obj.split('|')[-1]
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []

        suffix = None

        if shapes and cmds.nodeType(shapes[0]) == "locator":
            suffix = loc_suffix

        elif shapes and cmds.nodeType(shapes[0]) == "nurbsCurve":
            suffix = ctrl_suffix

        elif shapes and cmds.nodeType(shapes[0]) == "mesh":
            suffix = geo_suffix

        elif not shapes:
            suffix = grp_suffix

        if not suffix:
            continue

        if not short_name.endswith(suffix):
            new_name = short_name + suffix
            try:
                cmds.rename(obj, new_name)
                print(f"Renamed: {short_name} -> {new_name}")
            except:
                cmds.warning(f"Could not rename {short_name}")
        else:
            print(f"{short_name} already has suffix.")


def create_ui():
    if cmds.window(WINDOW_NAME, exists=True):
        cmds.deleteUI(WINDOW_NAME)

    cmds.window(WINDOW_NAME, title="Suffix Checker", widthHeight=(300, 200))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=8)

    cmds.text(label="Enter Desired Suffixes")

    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.text(label="Geometry:")
    cmds.textField("geoField", text="_GEO")
    cmds.setParent("..")

    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.text(label="Groups:")
    cmds.textField("grpField", text="_GRP")
    cmds.setParent("..")

    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.text(label="Controls:")
    cmds.textField("ctrlField", text="_CTRL")
    cmds.setParent("..")

    cmds.rowLayout(numberOfColumns=2, adjustableColumn=2)
    cmds.text(label="Locators:")
    cmds.textField("locField", text="_LOC")
    cmds.setParent("..")

    cmds.separator(height=10)

    cmds.button(label="Check Selected Objects", height=35, command=lambda x: apply_suffix())

    cmds.showWindow(WINDOW_NAME)


create_ui()