import maya.cmds as cmds
import controlJoint_creation

def create_nurbs_circle_ui(tabs):
    # Tab 2: NURBS Circle Tool
    tab2_layout = cmds.columnLayout(adjustableColumn=True)
    
    # Instructions prior
    cmds.text(label="Select a joint in the scene.")
    
    # Create a dropdown menu for axis selection
    axis_menu = cmds.optionMenu(label='Select Axis:')
    cmds.menuItem(label='X Axis')
    cmds.menuItem(label='Y Axis')
    cmds.menuItem(label='Z Axis')
    
    # Create a slider for size input
    cmds.text(label='Select Circle Size:')
    size_slider = cmds.intSlider(min=1, max=10, value=5, step=1)
    size_input = cmds.textField(text="5.0")

    # Update the text field based on the slider value
    def update_text_field(value):
        cmds.textField(size_input, edit=True, text=str(value))
    
    # Connect slider to update text field
    cmds.intSlider(size_slider, edit=True, changeCommand=update_text_field)

    # Create a button to run the function
    cmds.button(label="Create NURBS Circle", command=lambda x: create_nurbs_circle_around_joint(
        cmds.optionMenu(axis_menu, query=True, value=True),
        float(cmds.textField(size_input, query=True, text=True))  # Get size from text field
    ))

    # Recolor/Group NURBS Circle
    def on_group_nurbs_circle_click(*args):
        """Button to create the two groups for each control."""
        selected = cmds.ls(selection=True)
        if not selected:
            cmds.confirmDialog(title="Error", message="Please select a NURBS circle.", button=["OK"])
            return
        
        # Check if the selected object is a NURBS circle
        shape = cmds.listRelatives(selected[0], shapes=True, type="nurbsCurve")
        if not shape:
            cmds.confirmDialog(title="Error", message="Selected object is not a NURBS circle.", button=["OK"])
            return
        
        circle_name = selected[0]
        # Create offset + auto group
        offset_group = cmds.group(empty=True, name=circle_name + "_OFFSET")
        auto_group = cmds.group(empty=True, name=circle_name + "_AUTO")
        
        # Parent auto group under offset group and circle under that
        cmds.parent(auto_group, offset_group)
        cmds.parent(circle_name, auto_group)
        position = cmds.xform(circle_name, query=True, worldSpace=True, translation=True)
        cmds.xform(offset_group, worldSpace=True, translation=position)

    # Color slider
    cmds.text(label="Select NURBS Circle Color:")
    color_slider = cmds.intSlider(min=1, max=31, value=6, step=1)
    color_label = cmds.text(label="Color: Yellow (Index 6)")

    # Color names mapping
    color_names = {
        1: "Grey", 2: "Black", 3: "Dark Gray", 4: "Red",
        5: "Dark Blue", 6: "Blue", 7: "Dark Green", 8: "Navy",
        9: "Purple", 10: "Dark Red", 11: "Brown", 12: "Blood Red",
        13: "Bright Red", 14: "Bright Green", 15: "Dull Blue",
        16: "White", 17: "Light Yellow", 18: "Bright Blue",
        19: "Light Cyan", 20: "Pink-Orange", 21: "Peach", 22: "Yellow",
        23: "Green", 24: "Red-Yellow", 25: "Gold", 26: "Yellow-Green",
        27: "Green-Blue", 28: "Blue-Green", 29: "Blue", 30: "Light Purple",
        31: "Pink"
    }

    def update_color_label(value):
        """Update the color label to reflect the selected color."""
        color_name = color_names.get(value, "Unknown")
        cmds.text(color_label, edit=True, label=f"Color: {color_name} (Index {value})")
    
    # Connect the slider to update color label
    cmds.intSlider(color_slider, edit=True, dragCommand=update_color_label)

    def on_recolor_button_click(*args):
        """Recoloring an existing NURBS shape with index color."""
        selected = cmds.ls(selection=True)
        if not selected:
            cmds.confirmDialog(title="Error", message="Please select a NURBS circle.", button=["OK"])
            return
        
        shape = cmds.listRelatives(selected[0], shapes=True, type="nurbsCurve")
        if not shape:
            cmds.confirmDialog(title="Error", message="Selected object is not a NURBS circle.", button=["OK"])
            return
        
        # Get the color index from the slider
        color_index = cmds.intSlider(color_slider, query=True, value=True)
        
        # Apply the color to the NURBS curve
        shape_node = shape[0]
        cmds.setAttr(f"{shape_node}.overrideEnabled", 1)
        cmds.setAttr(f"{shape_node}.overrideColor", color_index)

    # Button to recolor the NURBS circle
    cmds.button(label="Recolor NURBS Circle", command=on_recolor_button_click)

    # Button to group the NURBS circle
    cmds.button(label="Group NURBS Circle", command=on_group_nurbs_circle_click)

    # Hex color input section
    cmds.text(label="Enter Hex Color Code (e.g., #FF5733):")
    hex_color_field = cmds.textField(placeholderText="#FF5733", width=280)

    def on_recolor_hex_button_click(*args):
        """Recoloring an existing NURBS shape with hex color."""
        hex_color = cmds.textField(hex_color_field, query=True, text=True)
        if not hex_color or not hex_color.startswith('#') or len(hex_color) != 7:
            cmds.warning("Please enter a valid hex color code (e.g., #FF5733).")
            return
        
        selected = cmds.ls(selection=True)
        if not selected:
            cmds.confirmDialog(title="Error", message="Please select a NURBS circle.", button=["OK"])
            return
        
        shape = cmds.listRelatives(selected[0], shapes=True, type="nurbsCurve")
        if not shape:
            cmds.confirmDialog(title="Error", message="Selected object is not a NURBS circle.", button=["OK"])
            return
        
        # Convert hex to RGB
        rgb = [int(hex_color[i:i+2], 16) / 255.0 for i in (1, 3, 5)]
        
        # Create a shading group and material if necessary
        shading_group = cmds.sets(shape[0], edit=True, force=True, noSurfaceShader=True, empty=True)
        shader = cmds.shadingNode('lambert', asShader=True, name=f"{shape[0]}_shader")
        
        cmds.setAttr(f"{shader}.color", rgb[0], rgb[1], rgb[2], type="double3")
        cmds.select(shape[0])
        cmds.hyperShade(assign=shader)

    # Button for recoloring any NURBS shape using hex color
    cmds.button(label="Recolor Selected NURBS Shapes", command=on_recolor_hex_button_click)

    # Set the parent back to the main layout
    cmds.setParent('..')
    
    cmds.tabLayout(tabs, edit=True, tabLabel=((tab_layout, "NURBS Circle Tool"),))

    return tab_layout

# Function to create a NURBS circle around a joint
def create_nurbs_circle_around_joint(axis, size):
    """Creates a NURBS circle around the currently selected joint."""
    selected_joints = cmds.ls(selection=True, type='joint')
    if not selected_joints:
        cmds.confirmDialog(title="Error", message="Please select a joint.", button=["OK"])
        return
    
    joint_position = cmds.xform(selected_joints[0], query=True, worldSpace=True, translation=True)
    
    # Create the NURBS circle
    circle = cmds.circle(normal=(1, 0, 0) if axis == 'X Axis' else (0, 1, 0) if axis == 'Y Axis' else (0, 0, 1),
                         radius=size, name=f"{selected_joints[0]}_NURBS_Circle")[0]
    
    # Move the circle to the joint position
    cmds.xform(circle, worldSpace=True, translation=joint_position)

