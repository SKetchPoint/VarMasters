import maya.cmds as cmds
from leg_chain_ui import create_leg_chain_ui
from nurbs_circle_ui import create_nurbs_circle_ui

def create_ui():
    # Check if the window exists
    if cmds.window("toolWindow", exists=True):
        cmds.deleteUI("toolWindow", window=True)
    
    window = cmds.window("toolWindow", title="Animation Tools", widthHeight=(400, 300))
    
    # Tab layout + creation
    tabs = cmds.tabLayout(innerMarginWidth=10, innerMarginHeight=10)
   
    # Create tabs and store the layout names
    leg_chain_layout = create_leg_chain_ui(tabs)
    nurbs_circle_layout = create_nurbs_circle_ui(tabs)
    
    # Rename the tabs if needed
    cmds.tabLayout(tabs, edit=True, tabLabel=[
        (leg_chain_layout, "Leg Chain Tool"),  # Rename if needed
        (nurbs_circle_layout, "NURBS Circle Tool")  # Rename if needed
    ])
    
    # Show window
    cmds.showWindow(window)

create_ui()