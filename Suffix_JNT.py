import maya.cmds as cmds

def add_joint_suffix(root=None, suffix="_JNT"):
    # If no root is given, use the selected object
    if not root:
        sel = cmds.ls(sl=True)
        if not sel:
            cmds.error("Please select the root of the hierarchy.")
        root = sel[0]
    
    # Get all descendants including the root
    all_nodes = cmds.listRelatives(root, allDescendents=True, fullPath=True) or []
    all_nodes.append(root)

    for node in all_nodes:
        # Check if it's a joint
        if cmds.nodeType(node) == "joint":
            short_name = node.split("|")[-1]  # strip path
            if not short_name.endswith(suffix):
                new_name = cmds.rename(node, short_name + suffix)
                print("Renamed:", short_name, "→", new_name)

# Run it
add_joint_suffix()
