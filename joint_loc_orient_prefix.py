import maya.cmds as cmds
from functools import partial

#-------------------------------------------------------------------------------------------------------------------------------------
# Core Logic Functions
#-------------------------------------------------------------------------------------------------------------------------------------

def add_prefix_to_joints(prefix="", apply_to_hierarchy=False, *args):
    """Adds a prefix string to selected joints, avoiding duplicate formatting."""
    if prefix and not prefix.endswith("_"):
        prefix += "_"
        
    selected_joints = cmds.ls(sl=True, type="joint")
    if not selected_joints:
        cmds.warning("No joints selected. Please select at least one joint.")
        return
        
    joints_to_rename = []
    if apply_to_hierarchy:
        all_descendants = cmds.listRelatives(selected_joints, ad=True, f=True, type="joint") or []
        long_selected = cmds.ls(selected_joints, l=True)
        joints_to_rename = long_selected + all_descendants
        joints_to_rename.sort(key=len, reverse=True)
    else:
        joints_to_rename = selected_joints

    renamed_count = 0
    for joint in joints_to_rename:
        short_name = joint.split("|")[-1]
        if short_name.startswith(prefix):
            continue
            
        new_name = prefix + short_name
        try:
            cmds.rename(joint, new_name)
            renamed_count += 1
        except RuntimeError as e:
            cmds.warning("Could not rename {}. System Error: {}".format(short_name, e))

    print("Success! Added prefix '{}' to {} joints.".format(prefix, renamed_count))


def convert_locator_hierarchy_to_joints(root_locator=None, *args):
    """Replicates an existing locator chain ending in _LOC into matching bone elements."""
    if not root_locator:
        selection = cmds.ls(sl=True)
        if not selection:
            cmds.warning("Please select the root locator of your hierarchy.")
            return
        root_locator = selection[0]
        
    hierarchy = cmds.listRelatives(root_locator, ad=True, f=True, type="transform") or []
    hierarchy.append(cmds.ls(root_locator, l=True)[0])
    hierarchy.sort(key=len)
    
    loc_to_jnt_map = {}
    cmds.select(cl=True)
    
    for loc_path in hierarchy:
        short_name = loc_path.split("|")[-1]
        if short_name.endswith("_LOC"):
            new_name = short_name.replace("_LOC", "_JNT")
        else:
            new_name = short_name + "_JNT"
            
        new_joint = cmds.joint(n=new_name)
        cmds.matchTransform(new_joint, loc_path, pos=True, rot=True, scl=True)
        cmds.makeIdentity(new_joint, apply=True, t=False, r=True, s=False)
        loc_to_jnt_map[loc_path] = new_joint
        
        parent_loc = cmds.listRelatives(loc_path, p=True, f=True)
        if parent_loc and parent_loc[0] in loc_to_jnt_map:
            target_parent_joint = loc_to_jnt_map[parent_loc[0]]
            cmds.parent(new_joint, target_parent_joint)
        else:
            cmds.parent(new_joint, w=True)
            
        cmds.select(cl=True)
        
    print("Success! Hierarchy converted from Locators to Joints.")


def set_joint_hierarchy_radius(target_radius=0.2, *args):
    """Changes the display radius across selected joints and descendants."""
    selected = cmds.ls(sl=True, type="joint")
    if not selected:
        cmds.warning("Please select the root joint of the hierarchy.")
        return
        
    hierarchy = cmds.listRelatives(selected, ad=True, f=True, type="joint") or []
    all_joints = selected + hierarchy
    
    for jnt in all_joints:
        cmds.setAttr("{}.radius".format(jnt), target_radius)
        
    print("Set radius to {} on {} joints.".format(target_radius, len(all_joints)))


def fix_hierarchy_orient_and_transforms(aim_axis="xyz", up_axis="yup", *args):
    """Cleans transformation variables and matches local coordinate orientations down a chain."""
    selected = cmds.ls(sl=True, type="joint")
    if not selected:
        cmds.warning("Please select the root joint of the hierarchy.")
        return
        
    children = cmds.listRelatives(selected, ad=True, f=True, type="joint") or []
    hierarchy = cmds.ls(selected, l=True) + children
    hierarchy.sort(key=len, reverse=True)
    
    print("Processing {} joints...".format(len(hierarchy)))
    
    for jnt in hierarchy:
        cmds.makeIdentity(jnt, apply=True, t=False, r=True, s=False, n=False, pn=True)
        
    hierarchy.reverse()
    
    for jnt in hierarchy:
        jnt_children = cmds.listRelatives(jnt, children=True, type="joint")
        if jnt_children:
            cmds.joint(jnt, edit=True, oj=aim_axis, secondaryAxisOrient=up_axis, ch=False, zso=True)
        else:
            cmds.joint(jnt, edit=True, oj="none", ch=False, zso=True)
            
    for jnt in hierarchy:
        parent = cmds.listRelatives(jnt, parent=True)
        if parent:
            for axis in ['y', 'z']: 
                attr = "{}.t{}".format(jnt, axis)
                if abs(cmds.getAttr(attr)) < 0.001:
                    cmds.setAttr(attr, 0)

    print("Hierarchy successfully optimized for pipeline export without positional shifts.")

#-------------------------------------------------------------------------------------------------------------------------------------
# UI Assembly Callbacks and Window
#-------------------------------------------------------------------------------------------------------------------------------------

def ui_callback_prefix(*args):
    prefix_val = cmds.textFieldGrp("ui_prefix_field", q=True, text=True)
    hierarchy_val = cmds.checkBoxGrp("ui_prefix_hier", q=True, v1=True)
    add_prefix_to_joints(prefix=prefix_val, apply_to_hierarchy=hierarchy_val)

def ui_callback_radius(*args):
    radius_val = cmds.floatFieldGrp("ui_radius_field", q=True, v1=True)
    set_joint_hierarchy_radius(target_radius=radius_val)

def ui_callback_orient(*args):
    aim_val = cmds.optionMenuGrp("ui_aim_menu", q=True, v=True)
    up_val = cmds.optionMenuGrp("ui_up_menu", q=True, v=True)
    fix_hierarchy_orient_and_transforms(aim_axis=aim_val, up_axis=up_val)

def create_joint_utility_ui():
    win_id = "animTechJointUtilsWindow"
    if cmds.window(win_id, exists=True):
        cmds.deleteUI(win_id)
        
    win = cmds.window(win_id, title="Joint Pipeline Utilities", w=320, h=280, mnb=False, mxb=False, s=True)
    main_layout = cmds.columnLayout(adj=True, rowSpacing=2)
    
    # --- BLOCK 1: PREFIX MANAGER ---
    cmds.frameLayout(l="Joint Naming Management", cll=False, marginWidth=4, marginHeight=4)
    cmds.columnLayout(adj=True, rowSpacing=4)
    cmds.textFieldGrp("ui_prefix_field", l="Prefix String", tx="L_", ad2=2)
    cmds.checkBoxGrp("ui_prefix_hier", l="Include Hierarchy", v1=True)
    cmds.button(l="Apply Prefix to Selected", h=26, c=ui_callback_prefix)
    cmds.setParent("..")
    cmds.setParent("..")
    
    # --- BLOCK 2: CONVERSIONS & VISUAL SCALE ---
    cmds.frameLayout(l="Structure & Display Adjustments", cll=False, marginWidth=4, marginHeight=4)
    cmds.columnLayout(adj=True, rowSpacing=4)
    cmds.button(l="Convert Locator Chain (_LOC -> _JNT)", h=28, c=convert_locator_hierarchy_to_joints)
    cmds.separator(h=6, st="in")
    cmds.floatFieldGrp("ui_radius_field", l="New Visual Radius", v1=0.21, pre=2, ad2=2)
    cmds.button(l="Set Scale on Selected Chain", h=26, c=ui_callback_radius)
    cmds.setParent("..")
    cmds.setParent("..")
    
    # --- BLOCK 3: ORIENT ENGINE ---
    cmds.frameLayout(l="Pipeline Orientation Alignment", cll=False, marginWidth=4, marginHeight=4)
    cmds.columnLayout(adj=True, rowSpacing=4)
    cmds.optionMenuGrp("ui_aim_menu", l="Primary Aim Axis", ad2=2)
    for axis_opt in ["xyz", "yzx", "zxy", "xzy", "yxz", "zyx"]: cmds.menuItem(l=axis_opt)
    
    cmds.optionMenuGrp("ui_up_menu", l="Secondary Up Rule", ad2=2)
    for up_opt in ["yup", "ydown", "zup", "zdown", "xup", "xdown"]: cmds.menuItem(l=up_opt)
    
    cmds.button(l="Clean and Orient Hierarchy", h=30, c=ui_callback_orient)
    cmds.setParent("..")
    cmds.setParent("..")
    
    cmds.showWindow(win)

if __name__ == "__main__":
    create_joint_utility_ui()