import maya.cmds as cmds

def create_nurbs_circle_around_joint(axis, size):
    """Creates a NURBS circle around a selected joint."""
    selected = cmds.ls(selection=True, type="joint")
    if not selected:
        cmds.warning("Please select a joint.")
        return
    
    joint = selected[0]
    circle = cmds.circle(normal=(1, 0, 0) if axis == "X - O Left or Right" else
                         (0, 1, 0) if axis == "Y - O Top or Bottom" else
                         (0, 0, 1), radius=size)[0]
    cmds.matchTransform(circle, joint, position=True, rotation=True)
    print(f"NURBS circle created around {joint} on {axis} axis with size {size}.")
    return circle

def add_controls_to_layout(parent_layout):
    """Adds the NURBS Circle Tool controls to a specified layout."""
    cmds.setParent(parent_layout)
    cmds.text(label="Select a joint in the scene.")
    
    # Dropdown menu for axis selection
    axis_menu = cmds.optionMenu(label='Select Axis:')
    cmds.menuItem(label='X - O Left or Right')
    cmds.menuItem(label='Y - O Top or Bottom')
    cmds.menuItem(label='Z - O Front or Back')
    
    # Slider for circle size
    cmds.text(label='Select Circle Size:')
    size_slider = cmds.intSlider(min=1, max=10, value=5, step=1)
    size_input = cmds.textField(text="5.0")
    
    def update_text_field(value):
        cmds.textField(size_input, edit=True, text=str(value))
    
    cmds.intSlider(size_slider, edit=True, changeCommand=update_text_field)
    
    # Button to create NURBS circle
    cmds.button(label="Create NURBS Circle", command=lambda x: create_nurbs_circle_around_joint(
        cmds.optionMenu(axis_menu, query=True, value=True),
        float(cmds.textField(size_input, query=True, text=True))
    ))
