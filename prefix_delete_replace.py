import maya.cmds as cmds

def modify_prefix(prefix_to_find, replace_with="", action="delete"):
    """
    Modifies or removes a specific prefix from selected objects.
    action: "delete" or "replace"
    """
    # Get current selection
    selection = cmds.ls(sl=True, long=True)
    
    if not selection:
        cmds.warning("No objects selected. Please select objects to rename.")
        return

    # Sort selection by string length descending to rename children before parents
    # This prevents Maya's long paths from breaking mid-loop
    selection.sort(key=len, reverse=True)
    
    count = 0
    
    for obj in selection:
        # Get the short name (the actual node name, ignoring path '|' characters)
        short_name = obj.split("|")[-1]
        
        # Check if the object starts with the specified prefix
        if short_name.startswith(prefix_to_find):
            if action == "delete":
                # Slice off the prefix
                new_short_name = short_name[len(prefix_to_find):]
            elif action == "replace":
                # Replace the prefix with the new string
                new_short_name = short_name.replace(prefix_to_find, replace_with, 1)
            else:
                continue
                
            # Rename the object
            try:
                new_name = cmds.rename(obj, new_short_name)
                count += 1
            except Exception as e:
                cmds.warning("Failed to rename {}: {}".format(short_name, e))
                
    print("Successfully updated {} objects.".format(count))

# --- UI Setup ---
def create_prefix_ui():
    window_id = "prefixManagerWindow"
    
    if cmds.window(window_id, exists=True):
        cmds.deleteUI(window_id)
        
    window = cmds.window(window_id, title="Prefix Manager", widthHeight=(300, 150), sizeable=False)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnOffset=["both", 10])
    
    cmds.separator(h=5, style="none")
    
    # Input fields
    prefix_field = cmds.textFieldGrp(label="Target Prefix:", text="Insert_", columnWidth=[1, 80])
    replace_field = cmds.textFieldGrp(label="Replace With:", text="", columnWidth=[1, 80])
    
    # Mode selector
    action_radio = cmds.radioButtonGrp(label="Action:", labelArray2=["Delete", "Replace"], numberOfRadioButtons=2, select=1, columnWidth=[1, 80])
    
    # Execution function wrapped for UI button
    def on_run_clicked(*args):
        prefix = cmds.textFieldGrp(prefix_field, q=True, text=True)
        replace_text = cmds.textFieldGrp(replace_field, q=True, text=True)
        mode_idx = cmds.radioButtonGrp(action_radio, q=True, select=True)
        
        mode = "delete" if mode_idx == 1 else "replace"
        
        if not prefix:
            cmds.error("Target Prefix cannot be empty.")
            return
            
        modify_prefix(prefix, replace_with=replace_text, action=mode)

    cmds.button(label="Process Selected", command=on_run_clicked, bgc=[0.2, 0.4, 0.3])
    cmds.separator(h=5, style="none")
    
    cmds.showWindow(window)

# Run the UI
create_prefix_ui()