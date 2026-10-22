import maya.cmds as cmds
import controlJoint_creation
import foot_joint_creation
import joint_chain_calc

def create_ui():
    # Tab 1: Leg Chain Tool
    def create_leg_chain_tool():
        # Check if the workspaceControl already exists and delete it
        if cmds.workspaceControl("legChainWorkspace", exists=True):
            cmds.deleteUI("legChainWorkspace", workspaceControl=True)
        
        # Create a new workspaceControl to dock the UI panel
        cmds.workspaceControl("legChainWorkspace", label="Leg Chain Tool", uiScript="print('Leg Chain Tool Loaded')", retain=False)
        cmds.columnLayout(adjustableColumn=True)
        
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
        
        cmds.button(label="Create Foot Joint Chain", command=on_create_button_click)
        cmds.setParent('..')
    
    # Tab 2: NURBS Circle Tool
    def create_nurbs_circle_tool():
        # Check if the workspaceControl already exists and delete it
        if cmds.workspaceControl("nurbsCircleWorkspace", exists=True):
            cmds.deleteUI("nurbsCircleWorkspace", workspaceControl=True)
        
        # Create a new workspaceControl to dock the UI panel
        cmds.workspaceControl("nurbsCircleWorkspace", label="NURBS Circle Tool", uiScript="print('NURBS Circle Tool Loaded')", retain=False)
        cmds.columnLayout(adjustableColumn=True)
        
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
        
        # checkbox control connection
        ctrl_connect_checkbox = cmds.checkBox(label="\nCreate Orient Constraint\n", value=True)
        
        # Create button to call the function
        def on_create_button_click(*args):
            selected_axis = cmds.optionMenu(axis_menu, query=True, value=True)
            size = float(cmds.textField(size_input, query=True, text=True))
            create_nurbs_circle_around_joint(selected_axis, size, ctrl_connect_checkbox)
        
        cmds.button(label="Create NURBS Circle", command=on_create_button_click)
        cmds.setParent('..')
    
    # Tab 3: Joint Chain Tool
    def create_joint_chain_tool():
        # Check if the workspaceControl already exists and delete it
        if cmds.workspaceControl("jointChainWorkspace", exists=True):
            cmds.deleteUI("jointChainWorkspace", workspaceControl=True)
        
        # Create a new workspaceControl to dock the UI panel
        cmds.workspaceControl("jointChainWorkspace", label="Joint Chain Tool", uiScript="print('Joint Chain Tool Loaded')", retain=False)
        cmds.columnLayout(adjustableColumn=True)
        
        cmds.text(label="Create a joint chain based on selected locators \n Shift select the start then end locator")
        
        cmds.text(label="Spread Factor (0.5, 1, 2):")
        spread_factor_field = cmds.floatField(value=1.0)

        cmds.text(label="Number of Points:")
        num_points_field = cmds.intField(value=8)
        
        cmds.text(label="Joint Radius:")
        jointChain_radius_field = cmds.floatField(minValue=0.1, value=20)
        
        # Button for creating the joint chain
        cmds.button(label="Create Joint Chain", command=lambda x: joint_chain_calc.create_joint_chain(
            spread_factor_field, num_points_field, jointChain_radius_field))
        cmds.setParent('..')
    
    # Create all three separate workspace windows
    create_leg_chain_tool()
    create_nurbs_circle_tool()
    create_joint_chain_tool()

# Run the UI
create_ui()
