import maya.cmds as cmds

def create_nurbs_circle_around_joint(selected_axis, size):
    # Check if there is a joint selected
    selected = cmds.ls(selection=True, type="joint")
    if not selected:
        cmds.confirmDialog(title="Error", message="Please select a joint.", button=["OK"])
        return
    
    joint = selected[0]
    
    # which axis does it direct to
    if selected_axis == "X Axis":
        normal = [1, 0, 0]
    elif selected_axis == "Y Axis":
        normal = [0, 1, 0]
    elif selected_axis == "Z Axis":
        normal = [0, 0, 1]
    else:
        cmds.confirmDialog(title="Error", message="Invalid axis selected.", button=["OK"])
        return

    # Create a NURBS circle at the joint's position via 
    # Move the circle to the joint's position, scale, freeze transforms
    circle = cmds.circle(name=joint + "_circle", normal=normal)[0]
    joint_position = cmds.xform(joint, query=True, worldSpace=True, translation=True)
    cmds.xform(circle, worldSpace=True, translation=joint_position)
    cmds.scale(size, size, size, circle)
    cmds.makeIdentity(circle, apply=True, rotate=True, scale=True, translate=True)
    
    # Success message
    cmds.confirmDialog(title="Success", message="NURBS circle created around joint.", button=["OK"])

def create_ui():
    if cmds.window("nurbsCircleWindow", exists=True):
        cmds.deleteUI("nurbsCircleWindow", window=True)
    window = cmds.window("nurbsCircleWindow", title="Create NURBS Circle Around Joint", widthHeight=(300, 200))
    cmds.columnLayout(adjustableColumn=True)
    
    # Instructions prior
    cmds.text(label="Select a joint in the scene.")
    
    # Create a dropdown menu for axis selection
    axis_menu = cmds.optionMenu(label='Select Axis:')
    cmds.menuItem(label='X - O Left or Right')
    cmds.menuItem(label='Y - O Top or Bottom')
    cmds.menuItem(label='Z - O Front or Back')
    
    # Create a slider for size input
    cmds.text(label='Select Circle Size:')
    size_slider = cmds.intSlider(min=1, max=10, value=5, step=1)
    
    # Create a text field for size input
    size_input = cmds.textField(text="5.0")
    
    # update the text field based on the slider value
    def update_text_field(value):
        cmds.textField(size_input, edit=True, text=str(value))
    
    # Connect slider to update text field
    cmds.intSlider(size_slider, edit=True, changeCommand=update_text_field)
    
    # Create a button to run the function
    cmds.button(label="Create NURBS Circle", command=lambda x: create_nurbs_circle_around_joint(
        cmds.optionMenu(axis_menu, query=True, value=True),
        float(cmds.textField(size_input, query=True, text=True))  # Get size from text field
    ))
    
    # Show the window
    cmds.showWindow(window)

# Run the UI
create_ui()