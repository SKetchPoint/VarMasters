import maya.cmds as cmds
import controlJoint_creation
import foot_joint_creation
import joint_chain_calc
import joint_spline_chain

def create_ui():
    # Check if the window exists
    if cmds.window("toolWindow", exists=True):
        cmds.deleteUI("toolWindow", window=True)
    window = cmds.window("toolWindow", title="General Rig Tools", widthHeight=(200, 300))
    
    # Tab layout
    tabs = cmds.tabLayout(innerMarginWidth=10, innerMarginHeight=10)
    
    # ------------------------------------------
    # Tab 1: Leg Chain Tool
    # ------------------------------------------
    tab1_layout = cmds.columnLayout(adjustableColumn=True)
    cmds.text(label="Create a foot joint chain using selected locators.")
    
    # Input for joint radius
    cmds.text(label="Joint Radius:")
    joint_radius_field = cmds.floatField(minValue=0.1, value=1.0)
    
    # Instructions for user
    cmds.text(label="1. Select the Hip Locator, then click the button.")
    cmds.text(label="2. Select the Knee Locator, then click the button.")
    cmds.text(label="3. Select the Ankle Locator, then click the button.")
    cmds.text(label="4. Once ALL the locators have been assigned, create the chain.")
    
    # Locator selection buttons and fields
    def on_select_locator(field):
        locator = cmds.ls(selection=True)
        if locator:
            cmds.textField(field, edit=True, text=locator[0])
    # select the locators to allow adjustments  in joint placement (expecially hip) and show which locator name it is
    cmds.button(label="Select Hip Locator", command=lambda x: on_select_locator(hip_locator_field))
    hip_locator_field = cmds.textField(editable=False)
    
    cmds.button(label="Select Knee Locator", command=lambda x: on_select_locator(knee_locator_field))
    knee_locator_field = cmds.textField(editable=False)
    
    cmds.button(label="Select Ankle Locator", command=lambda x: on_select_locator(ankle_locator_field))
    ankle_locator_field = cmds.textField(editable=False)
    
    # Button to create the foot joint chain
    def on_create_button_click(*args):
        jntRadi = cmds.floatField(joint_radius_field, query=True, value=True)
        hip_locator = cmds.textField(hip_locator_field, query=True, text=True)
        knee_locator = cmds.textField(knee_locator_field, query=True, text=True)
        ankle_locator = cmds.textField(ankle_locator_field, query=True, text=True)
        
        if hip_locator and knee_locator and ankle_locator:
            foot_joint_creation.create_joint_chain(jntRadi, hip_locator, knee_locator, ankle_locator)
        else:
            cmds.confirmDialog(title="Error", message="Please select all locators before creating joints.", button=["OK"])
    def apply_radius(radius_field):
        """Gets the radius value from the text box and applies it."""
        try:
            # value from the stored text field reference
            radius_value = float(cmds.textFieldGrp(radius_field, query=True, text=True))
            foot_joint_creation.change_bone_radius(radius=radius_value)
        except ValueError:
            cmds.warning("Please enter a valid numeric value for the radius.")
    cmds.button(label="Create Foot Joint Chain", command=on_create_button_click)
    radius_field = cmds.textFieldGrp(label="New Selected Joint Radius", text="1.0")
    cmds.button(label="Apply Radius", command=lambda x: apply_radius(radius_field))
    cmds.setParent('..')
    

    # ----------------------------------- 
    # Tab 2: NURBS Circle Tool
    # -----------------------------------
    #-----------------------------------------------------------------------Create NURBS Circle
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
    size_slider = cmds.intSlider(min=1, max=200, value=10, step=1)
    
    # Create a text field for size input
    size_input = cmds.textField(text="10")
    
    # update the text field based on the slider value
    def update_text_field(value):
        cmds.textField(size_input, edit=True, text=str(value))
    
    # Connect slider to update text field
    cmds.intSlider(size_slider, edit=True, changeCommand=update_text_field)
    
    #checkbox
    ctrl_connect_checkbox = cmds.checkBox(label="\nCreate Orient Constraint\n", value=True)
    
    # Create button to call the function
    def on_create_button_click(*args):
        selected_axis = cmds.optionMenu(axis_menu, query=True, value=True)
        size = float(cmds.textField(size_input, query=True, text=True))
        ctrl_connect = cmds.checkBox(ctrl_connect_checkbox, query=True, value=True)
        
        # Call the function with UI inputs
        controlJoint_creation.create_fk_control_with_group(selected_axis, size, ctrl_connect)
    
    cmds.button(label="Create NURBS Circle", command=on_create_button_click)
    #----------------------------------------------------------------------------------------------------------------Recolor/Group NURBS Circle (W slider)
    def on_group_controls_click(*args):
        """Button to group selected controls into grp (OFFSET)."""
        selected = cmds.ls(selection=True)
        if not selected:
            cmds.confirmDialog(title="Error", message="Please select one or more controls.", button=["OK"])
            return
        group_nurbs_curve(curve, curve)
        cmds.confirmDialog(title="Success", message="Controls have been grouped successfully.", button=["OK"])
        
    # color slider
    cmds.text(label="Select NURBS Circle Color:")
    color_slider = cmds.intSlider(min=1, max=31, value=6, step=1)
    
    # name of the color + index #
    color_label = cmds.text(label="Color: Yellow (Index 6)")
    
    # library of indexes of color # to name, could also use HEX
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
    
    def on_group_nurbs_circle_click(*args):
        """Button to create the two groups for each control."""
        # Get the selected object
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
    
        # Create auto grp
        auto_group = cmds.group(empty=True, name=circle_name + "_AUTO")
        #offset_group = cmds.group(empty=True, name=circle_name + "_OFFSET")
        # Parent auto group under offset group and circle under that
        #cmds.parent(auto_group, offset_group)
        cmds.parent(circle_name, auto_group)
        position = cmds.xform(circle_name, query=True, worldSpace=True, translation=True)
        cmds.xform(auto_group, worldSpace=True, translation=position)
    
    def update_color_label(value):
        """Update the color label to reflect the selected color."""
        color_name = color_names.get(value, "Unknown")
        cmds.text(color_label, edit=True, label=f"Color: {color_name} (Index {value})")
    # lable to slider
    cmds.intSlider(color_slider, edit=True, dragCommand=update_color_label)
    
    def on_recolor_button_click(*args):
        """Recoloring an existing CTRL nurbs circle"""
        # checking to see if the selected is a NURBS CIRCLE
        # if it's a custom control/ anything but a NURBS circle, use hex color code (87-93 gives examples in comments)
        selected = cmds.ls(selection=True)
        if not selected:
            cmds.confirmDialog(title="Error", message="Please select a NURBS circle. Check comments on line 60", button=["OK"])
            return
        
        # Check if the selected object is a NURBS circle
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
    
    cmds.button(label="Recolor NURBS Circle", command=on_recolor_button_click)
    #Recolor NURBS Circle func ONLY meant for Curcle NURBS, use HEX for anything else
    cmds.button(label="Group NURBS Circle", command=on_group_nurbs_circle_click)
    #--------------------------------------------------------------------------------------------select joint and control correction
    def on_position_nurbs_click(*args):
        """ Call the create_nurbs_control_with_joint function with selected inputs. """
        nurbs_surface = cmds.textField(nurbs_field, query=True, text=True)
        joint = cmds.textField(joint_field, query=True, text=True)
        
        if nurbs_surface and joint:
            controlJoint_creation.create_nurbs_control_with_joint(nurbs_surface, joint)
        else:
            cmds.warning("Please enter valid NURBS surface and joint names.")
    
    def on_select_nurbs_click(*args):
        """ Populate the NURBS surface field with the selected object. """
        selected = cmds.ls(selection=True)
        if selected:
            cmds.textField(nurbs_field, edit=True, text=selected[0])
        else:
            cmds.warning("Please select a NURBS surface.")
    
    def on_select_joint_click(*args):
        """ Populate the joint field with the selected joint. """
        selected = cmds.ls(selection=True, type="joint")
        if selected:
            cmds.textField(joint_field, edit=True, text=selected[0])
        else:
            cmds.warning("Please select a joint.")
    
    # NURBS surface input field with button to select
    cmds.text(label="\n\nNURBS Surface:")
    nurbs_field = cmds.textField()
    cmds.button(label="Select NURBS Surface", command=on_select_nurbs_click)
    
    # Joint input field with button to select
    cmds.text(label="Joint:")
    joint_field = cmds.textField()
    cmds.button(label="Select Joint", command=on_select_joint_click)
    
    # Button to position the NURBS surface
    cmds.button(label="Position NURBS Surface", command=on_position_nurbs_click)

    cmds.text(label="\n")
    #--------------------------------------------------------------------------------------------Hex color any control
    cmds.text(label="Enter Hex Color Code (e.g., #FF5733):")
    #text field for user unput w example peach color
    #other hex codes 
    
    #Colors below are chosen to accomodate color blindness based upon
    #https://www.nceas.ucsb.edu/sites/default/files/2022-06/Colorblind%20Safe%20Color%20Schemes.pdf
    
    #Paul Tol's Bright
    #aa3377 - pink
    #ee6677 - light pink
    #ccbb44 - yellow
    #ff5f00 - orange
    #66ccee - light blue
    #228833 - green
    #4477aa - medium blue
    #bbbbbb - grey
    hex_color_field = cmds.textField(placeholderText="#FF5733", width=280)

    def on_recolorCurve_button_click(*args):
        """Recoloring an existing NURBS shape with hex color."""
        hex_color = cmds.textField(hex_color_field, query=True, text=True)
        #checkig its a hexadecimle color and once it is can recolor any nurbs shape, even custom controls
        if not hex_color:
            cmds.warning("Please enter a hex color code. Line 188-193 give other examples")
            return
        controlJoint_creation.recolor_nurbs_shapes(hex_color)
    #button for recoloring any nurbs shape, no longer limited to circle (useful for customs)
    cmds.button(label="Recolor Selected NURBS Shapes", command=on_recolorCurve_button_click)
    
    def on_recolorJoints_button_click(*args):
        """Recoloring an existing joint with hex color."""
        hex_color = cmds.textField(hex_color_field, query=True, text=True)
        #checkig its a hexadecimle color and once it is can recolor any nurbs shape, even custom controls
        if not hex_color:
            cmds.warning("Please enter a hex color code. Line 188-193 give other examples")
            return
        controlJoint_creation.color_joints_with_hex(hex_color)
    #button for recoloring any nurbs shape, no longer limited to circle (useful for customs)
    cmds.button(label="Recolor Selected Joints", command=on_recolorJoints_button_click)
    
    #-----------------------------------------------------------------------------------------------Locator at control
    #create button that makes a locator at the piviot point as a building aid
    def on_createLocator_button_click(*args):
        controlJoint_creation.create_locator_at_pivot()
    cmds.text(label="\nPlace locator at piviot point ")
    cmds.button(label="Create Control Locator", command=on_createLocator_button_click)
        
    cmds.setParent('..')
    
    # -----------------------------------
    # Tab 3: Joint Chain Tool
    # -----------------------------------
    tab3_layout = cmds.columnLayout(adjustableColumn=True)
    cmds.columnLayout(adjustableColumn=True)
    
    cmds.text(label="Create a joint chain based on selected locators OR curve-shift select joint creation\n")
    
    cmds.text(label="Spread Factor (0.5, 1, 2):")
    spread_factor_field = cmds.floatField(value=1.0)

    cmds.text(label="Number of Points:")
    num_points_field = cmds.intField(value=8)
    
    cmds.text(label="Joint Radius:")
    jointChain_radius_field = cmds.floatField(minValue=0.1, value=20)
    

    # Button for creating the joint chain
    cmds.text(label="\n Linear Path Joint Chain (2 locators):")  
    cmds.button(label="Create Joint Chain", command=lambda x: joint_chain_calc.create_joint_chain(
        spread_factor_field, num_points_field, jointChain_radius_field))
    cmds.text(label="\n Non Linear Path Joint Chain(Select a curve):")    
    cmds.button(label="Create Joint Chain Along Curve", command=lambda x:joint_spline_chain.chain_on_curve(spread_factor_field, num_points_field, jointChain_radius_field))
    
    cmds.text(label="\n---[SPLINE IK CONTROL HELPER]--\n")
    cmds.button(label="Create Curve (select joints)", command=lambda x: joint_spline_chain.create_curve_from_joints())
    cmds.button(label="Cluster Curve (select curve)", command=lambda x: joint_spline_chain.cluster_cv_on_selected_curve())
    cmds.text(label="\n---[JOINT+CHILDREN ROTATE ORDER]--\n")
    def apply_rotation_order(*args):
        """
        Applies the selected rotation order to either joints or curves, depending on the selection.
        """
        selected_order = cmds.optionMenu(rotation_order_menu, query=True, value=True)
        rotationOrder_jointChildren = cmds.checkBox(rotationOrder_jointChildren_checkbox, query=True, value=True)
        
        selected_joints = cmds.ls(selection=True, type='joint')
        
        if selected_joints:
            joint_spline_chain.joint_children_rotation_order(selected_order, rotationOrder_jointChildren)
        else:
            joint_spline_chain.change_curve_rotation_order(selected_order)
    cmds.text(label="Choose Rotation Order:")
    
    rotation_order_menu = cmds.optionMenu(label="Rotation Order")
    cmds.menuItem(label="yzx")
    cmds.menuItem(label="yxz")
    cmds.menuItem(label="zxy")
    cmds.menuItem(label="zyx")
    cmds.menuItem(label="xzy")
    cmds.menuItem(label="xyz")
    
    rotationOrder_jointChildren_checkbox = cmds.checkBox(label="\nChildren Rotation Order Changed (joint ony)\n", value=True)
    
    cmds.button(label="Set Rotation Order (joints or controls)", command=apply_rotation_order)
    cmds.setParent('..')
    
    # Tab labels/layout for user to pan through
    cmds.tabLayout(tabs, edit=True, tabLabel=(
        (tab1_layout, "Leg Chain"), 
        (tab2_layout, "NURBS Circle Control"),
        (tab3_layout, "Joint Chain Curve")
    ))
    # Show the window
    cmds.showWindow(window)
# Run the UI
create_ui()
