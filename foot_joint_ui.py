import maya.cmds as cmds
import foot_joint_creation  # Import the joint creation function from the other file

def create_ui():
    # Check if the window already exists
    if cmds.window("footUI", exists=True):
        cmds.deleteUI("footUI", window=True)
    
    # Create the window
    cmds.window("footUI", title="Foot Joint Chain Creator", widthHeight=(300, 250))
    
    # Layout for the UI
    cmds.columnLayout(adjustableColumn=True)
    
    # Input for joint radius
    cmds.text(label="Joint Radius:")
    joint_radius_field = cmds.floatField(minValue=0.1, value=1.0)
    
    # Text instructions for selecting locators
    cmds.text(label="Select Locators for Joint Positions:")
    cmds.text(label="1. Select the Hip Locator, then click the button.")
    cmds.text(label="2. Select the Knee Locator, then click the button.")
    cmds.text(label="3. Select the Ankle Locator, then click the button.")
    
    # Button to set locator for hip
    def on_select_hip_locator(*args):
        hip_locator = cmds.ls(selection=True)
        if hip_locator:
            cmds.textField(hip_locator_field, edit=True, text=hip_locator[0])
    
    cmds.button(label="Select Hip Locator", command=on_select_hip_locator)
    hip_locator_field = cmds.textField(editable=False)
    
    # Button to set locator for knee
    def on_select_knee_locator(*args):
        knee_locator = cmds.ls(selection=True)
        if knee_locator:
            cmds.textField(knee_locator_field, edit=True, text=knee_locator[0])
    
    cmds.button(label="Select Knee Locator", command=on_select_knee_locator)
    knee_locator_field = cmds.textField(editable=False)
    
    # Button to set locator for ankle
    def on_select_ankle_locator(*args):
        ankle_locator = cmds.ls(selection=True)
        if ankle_locator:
            cmds.textField(ankle_locator_field, edit=True, text=ankle_locator[0])
    
    cmds.button(label="Select Ankle Locator", command=on_select_ankle_locator)
    ankle_locator_field = cmds.textField(editable=False)
    
    # Button to create joints
    def on_create_button_click(*args):
        jntRadi = cmds.floatField(joint_radius_field, query=True, value=True)
        hip_locator = cmds.textField(hip_locator_field, query=True, text=True)
        knee_locator = cmds.textField(knee_locator_field, query=True, text=True)
        ankle_locator = cmds.textField(ankle_locator_field, query=True, text=True)
        
        if hip_locator and knee_locator and ankle_locator:
            # Call the create_joint_chain function from foot_joint_creation.py
            foot_joint_creation.create_joint_chain(jntRadi, hip_locator, knee_locator, ankle_locator)
        else:
            cmds.confirmDialog(title="Error", message="Please select all locators before creating joints.", button=["OK"])
    
    cmds.button(label="Create Foot Joint Chain", command=on_create_button_click)
    
    # Show the window
    cmds.showWindow("footUI")

# Run the UI
create_ui()
