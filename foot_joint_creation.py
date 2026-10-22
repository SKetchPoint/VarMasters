import maya.cmds as cmds

def create_joint_chain(jntRadi, hipLoc, kneeLoc, ankleLoc):
    # Get the position of the locators
    hipPos = cmds.xform(hipLoc, query=True, worldSpace=True, translation=True)
    kneePos = cmds.xform(kneeLoc, query=True, worldSpace=True, translation=True)
    anklePos = cmds.xform(ankleLoc, query=True, worldSpace=True, translation=True)

    # Creation of the joints for hip, knee, and ankle
    hip = cmds.joint(p=hipPos, name="hip_JNT", radius=jntRadi)
    knee = cmds.joint(p=kneePos, name="knee_JNT", radius=jntRadi)
    ankle = cmds.joint(p=anklePos, name="ankle_JNT", radius=jntRadi)
    
    # Branch to the fake back toe
    cmds.select(ankle)  # Selection of the ankle joint for proper branching
    fake_back_toe1 = cmds.joint(p=(43, 86, -73), name="fakeBackToe1_JNT", radius=jntRadi)
    fake_back_toe2 = cmds.joint(p=(39, 71, -62), name="fakeBackToe2_JNT", radius=jntRadi)
    fake_back_toe3 = cmds.joint(p=(37, 56, -57), name="fakeBackToe3_JNT", radius=jntRadi)
    fake_back_toe4 = cmds.joint(p=(35, 37.5, -51), name="fakeBackToe4_JNT", radius=jntRadi)
    
    # Foot for the support of the main toes
    cmds.select(ankle)
    foot = cmds.joint(p=(70, 21, -42), name="foot_JNT", radius=jntRadi)
    
    # All 3 toe branches
    cmds.select(foot)  # Selection for branching
    inner_toe1 = cmds.joint(p=(49, 15, -19.5), name="innerToe1_JNT", radius=jntRadi)
    inner_toe2 = cmds.joint(p=(38, 12, -.5), name="innerToe2_JNT", radius=jntRadi)
    inner_toe3 = cmds.joint(p=(30, 5.5, 23), name="innerToe3_JNT", radius=jntRadi)
    
    cmds.select(foot)  # Select for branch
    mid_toe1 = cmds.joint(p=(74, 17.5, -13), name="midToe1_JNT", radius=jntRadi)
    mid_toe2 = cmds.joint(p=(76, 15, 11), name="midToe2_JNT", radius=jntRadi)
    mid_toe3 = cmds.joint(p=(80, 11, 42), name="midToe3_JNT", radius=jntRadi)

    cmds.select(foot)  # Select for branch
    outter_toe1 = cmds.joint(p=(98, 15, -25), name="outterToe1_JNT", radius=jntRadi)
    outter_toe2 = cmds.joint(p=(110, 11.5, -7), name="outterToe2_JNT", radius=jntRadi)
    outter_toe3 = cmds.joint(p=(121.5, 8, 15.5), name="outterToe3_JNT", radius=jntRadi)

    # Return the root joint
    return hip
def change_bone_radius(radius):
    # Get the selected joints
    selected_joints = cmds.ls(selection=True, type='joint')
    
    if not selected_joints:
        cmds.warning("No joints selected. Please select some joints.")
        return
    
    # Change the radius of each selected joint
    for joint in selected_joints:
        cmds.setAttr(f"{joint}.radius", radius)
    
    print(f"Changed radius of {len(selected_joints)} joint(s) to {radius}")