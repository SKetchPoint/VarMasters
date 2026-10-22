import maya.cmds as cmds
import foot_joint_creation

def create_leg_chain_ui(tabs):
    # Create a new tab layout if it doesn't exist
    if not cmds.tabLayout(tabs, exists=True):
        tabs = cmds.tabLayout()

    # Tab 1: Leg Chain Tool
    tab1_layout = cmds.columnLayout(adjustableColumn=True)

    # Title for the Leg Chain Tool
    cmds.text(label="Leg Chain Tool", font="boldLabelFont", align="center")
    
    # Description
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
    hip_locator_field = cmds.textField(editable=False)
    knee_locator_field = cmds.textField(editable=False)
    ankle_locator_field = cmds.textField(editable=False)
    

    def on_select_locator(field):
        locator = cmds.ls(selection=True)
        if locator:
            cmds.textField(field, edit=True, text=locator[0])
    
    cmds.button(label="Select Hip Locator", command=lambda x: on_select_locator(hip_locator_field))
    cmds.button(label="Select Knee Locator", command=lambda x: on_select_locator(knee_locator_field))
    cmds.button(label="Select Ankle Locator", command=lambda x: on_select_locator(ankle_locator_field))
    
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
    
    # Set the parent back to the main layout
    cmds.setParent('..')
    
    cmds.tabLayout(tabs, edit=True, tabLabel=((tab_layout, "Leg Chain Tool"),))

    return tab_layout  # Return the layout name