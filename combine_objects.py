"""
combine_selected.py

Combines all selected objects in Autodesk Maya into one shape.

Usage (paste into Maya Script Editor -> Python tab, then run):

    import combine_selected
    combine_selected.combine_selected_objects()

Requires: Maya with Python and maya.cmds
"""

import maya.cmds as cmds

def combine_selected_objects(name="combinedShape"):
    # Get selected objects
    selection = cmds.ls(selection=True, long=True, type='transform')
    if not selection:
        cmds.warning("No objects selected to combine.")
        return None

    # Combine all selected meshes
    combined = cmds.polyUnite(selection, name=name, ch=False, mergeUVSets=True)[0]

    # Delete history and center the pivot
    try:
        cmds.delete(combined, ch=True)
    except Exception:
        pass
    cmds.xform(combined, centerPivots=True)

    print(f"Combined {len(selection)} objects into one: {combined}")
    return combined

if __name__ == '__main__':
    combine_selected_objects()