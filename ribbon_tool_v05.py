import maya.cmds as cmds
import maya.mel as mel
from functools import partial

#-------------------------------------------------------------------------------------------------------------------------------------     
# Add Temporary Distance Node
def getTempDistance(startPos, endPos):
    cmds.shadingNode ("distanceBetween", au=1, n=(startPos + "_distnode"))
    cmds.connectAttr ((startPos + ".worldMatrix"), (startPos + "_distnode.inMatrix1"))
    cmds.connectAttr ((endPos + ".worldMatrix"), (startPos + "_distnode.inMatrix2"))
    cmds.connectAttr ((startPos + ".rotatePivotTranslate"), (startPos + "_distnode.point1"))
    cmds.connectAttr ((endPos + ".rotatePivotTranslate"), (startPos + "_distnode.point2"))
    dist = cmds.getAttr((startPos + "_distnode.distance"))
    cmds.delete((startPos + "_distnode"))
    return dist
     
#-------------------------------------------------------------------------------------------------------------------------------------
# Build Icon
def buildIcon(iconName, scale, *args):
    jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1) 
    pointsList = ([0.49949352081828996, -0.49965646741954789, 0.00011386882060004933],
            [-0.50050383972379531, -0.49965777484916379, 0.00025944578385106443],
            [-0.50050388864963413, 0.50034323886898902, -0.00011386824481751656],
            [0.49950191468729815, 0.50034278368308582, -0.0002594457838509534],
            [0.49949352081828996, -0.49965646741954789, 0.00011386882060004933])
            
    cmds.curve (d=1, p=pointsList[0], n=iconName)
    for i in range(len(pointsList)):
        if i < (len(pointsList)-1):
            cmds.curve (iconName, a=1, p=pointsList[i+1])   
    cmds.setAttr ((iconName + ".scale"), scale, scale, scale)
   
    if jointOrient == "X": cmds.setAttr ((iconName + ".ry"), 90)
    elif jointOrient == "Y": cmds.setAttr ((iconName + ".rx"), 90)
        
    cmds.makeIdentity (iconName, a=1, t=1, r=1, s=1)
    
#-------------------------------------------------------------------------------------------------------------------------------------
# Cleanup
def cleanRibbon(ribbonNme, matrixRibbon):
    if not cmds.objExists(ribbonNme + "_grp"):
        cmds.group(em=1, n=ribbonNme + "_grp")
        cmds.parent(ribbonNme, ribbonNme + "_grp")

    if cmds.ls(ribbonNme + "_follicle_*"):
        if cmds.objExists(ribbonNme + "_follicles"): cmds.parent(cmds.ls(ribbonNme + "_follicle_*"), ribbonNme + "_follicles")
        else: cmds.group(cmds.ls(ribbonNme + "_follicle_*"), n=ribbonNme + "_follicles")
        cmds.parent(ribbonNme + "_follicles", ribbonNme + "_grp")
        
    if cmds.ls(ribbonNme + "_ctrljnt_*", type="joint"):
        if cmds.objExists(ribbonNme + "_ctrljnts"): cmds.parent(cmds.ls((ribbonNme + "_ctrljnt_*"), type="joint"), ribbonNme + "_ctrljnts")
        else: cmds.group(cmds.ls((ribbonNme + "_ctrljnt_*"), type="joint"), n=ribbonNme + "_ctrljnts")
        cmds.parent(ribbonNme + "_ctrljnts", ribbonNme + "_grp")

    if cmds.ls(ribbonNme + "_control_*_offset"):
        if cmds.objExists(ribbonNme + "_controls"): cmds.parent(cmds.ls(ribbonNme + "_control_*_offset"), ribbonNme + "_controls")
        else: cmds.group(cmds.ls(ribbonNme + "_control_*_offset"), n=ribbonNme + "_controls")
        cmds.parent(ribbonNme + "_controls", ribbonNme + "_grp")

    extraNodeList = (cmds.ls(ribbonNme + "_ikHandle_*") + cmds.ls(ribbonNme + "_tweak_*offset") + cmds.ls(ribbonNme + "_sine_*", tr=1) + cmds.ls(ribbonNme + "_twist_*", tr=1))
    for extraNode in extraNodeList:
        if not "Constraint" in extraNode: cmds.parent(extraNode, ribbonNme + "_grp")
    cmds.select(cl=1)
    
#-------------------------------------------------------------------------------------------------------------------------------------
# Store the ribbon data
def storeRibData(surface, spans, direction, orientation, endorient):
    globalScale = cmds.floatField("globalScaleInput", q=1, v=1)
    jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1) 
    jointFlip = cmds.checkBox("jointOrientFlip", q=1, v=1)
    resetJnt = cmds.checkBox("resetJntInput", q=1, v=1)
    # New checkbox data
    worldEndPos = cmds.checkBox("worldEndPosInput", q=1, v=1)

    cmds.addAttr (surface, ln="spans", at="long", dv=spans); cmds.setAttr ((surface + ".spans"), l=1)
    cmds.addAttr (surface, ln="RibbonName", dt="string"); cmds.setAttr ((surface + ".RibbonName"), surface, type="string", l=1)
    cmds.addAttr (surface, ln="jointOrientMenu", dt="string"); cmds.setAttr ((surface + ".jointOrientMenu"), jointOrient, type="string", l=1)
    cmds.addAttr (surface, ln="direction", dt="string"); cmds.setAttr ((surface + ".direction"), direction, type="string", l=1)

    cmds.addAttr (surface, ln="orientation", at="double3")
    cmds.addAttr (surface, ln="orientationX", at="double", p="orientation")    
    cmds.addAttr (surface, ln="orientationY", at="double", p="orientation")        
    cmds.addAttr (surface, ln="orientationZ", at="double", p="orientation")        
    cmds.setAttr ((surface + ".orientation"), orientation[0], orientation[1], orientation[2], type="double3", l=1)

    cmds.addAttr (surface, ln="endorient", at="double3")
    cmds.addAttr (surface, ln="endorientX", at="double", p="endorient")    
    cmds.addAttr (surface, ln="endorientY", at="double", p="endorient")        
    cmds.addAttr (surface, ln="endorientZ", at="double", p="endorient")  
    cmds.setAttr ((surface + ".endorient"), endorient[0], endorient[1], endorient[2], type="double3", l=1)
                        
    cmds.addAttr (surface, ln="globalScaleInput", at="double", dv=globalScale); cmds.setAttr ((surface + ".globalScaleInput"), l=1)
    cmds.addAttr (surface, ln="jointOrientFlip", at="long", dv=jointFlip); cmds.setAttr ((surface + ".jointOrientFlip"), l=1)
    cmds.addAttr (surface, ln="resetJntInput", at="long", dv=resetJnt); cmds.setAttr ((surface + ".resetJntInput"), l=1)
    cmds.addAttr (surface, ln="worldEndPosInput", at="long", dv=worldEndPos); cmds.setAttr ((surface + ".worldEndPosInput"), l=1)

#-------------------------------------------------------------------------------------------------------------------------------------
# Convert to Matrix
def convertToMatrix(*args):
    ribbonNme = cmds.textField("nameInput", q=1, tx=1)
    if not cmds.objExists(ribbonNme + "_follicle_01"): cmds.error("Follicles not found, make sure the name of the ribbon is correct.")
    ribbonJointList = cmds.ls(ribbonNme + "_joint_*", type="joint")

    spans = cmds.getAttr ((ribbonNme + ".spans"))
    direction = cmds.getAttr ((ribbonNme + ".direction"))
    orientation = (cmds.getAttr(ribbonNme + ".orientationX"), cmds.getAttr(ribbonNme + ".orientationY"), cmds.getAttr(ribbonNme + ".orientationZ"))
    endorient = (cmds.getAttr(ribbonNme + ".endorientX"), cmds.getAttr(ribbonNme + ".endorientY"), cmds.getAttr(ribbonNme + ".endorientZ"))

    for ribbonJoint in ribbonJointList: cmds.delete(ribbonJoint.replace("_joint_", "_follicle_"))
    cmds.select(cl=1)
    matrixConnect(ribbonNme, spans, direction, orientation, endorient, 1)  

#-------------------------------------------------------------------------------------------------------------------------------------
# Add Ribbon Jiggle
def addRibbonJiggle(surface, *args):
    doJiggle = cmds.checkBox("addJiggleInput", q=1, v=1)
    if doJiggle:
        cmds.deformer(surface, type="jiggle", n=surface + "_jiggle")
        cmds.connectAttr (("time1.outTime"), (surface + "_jiggle.currentTime"), f=1) 
        cmds.addAttr (surface, ln="muscleOptions", nn="--------", at="enum", en="MUSCLE", k=1)
        cmds.addAttr (surface, ln="Enable", at="enum", en="On:Off", k=1)
        cmds.addAttr (surface, ln="Amount", s=1, at="double", k=1, dv=0.9)
        cmds.addAttr (surface, ln="Flexability", s=1, at="double", k=1, dv=0.5)
        cmds.addAttr (surface, ln="Float", s=1, at="double", k=1, dv=0.5)   
        cmds.connectAttr ((surface + ".Enable"), (surface + "_jiggle.enable"), f=1)  
        cmds.connectAttr ((surface + ".Amount"), (surface + "_jiggle.jiggleWeight"), f=1)  
        cmds.connectAttr ((surface + ".Flexability"), (surface + "_jiggle.stiffness"), f=1)  
        cmds.connectAttr ((surface + ".Float"), (surface + "_jiggle.damping"), f=1)  
        cmds.select(cl=1)        
            
#-------------------------------------------------------------------------------------------------------------------------------------
# Add Ribbon Deformers
def addRibbonDeformers(surface, ribbonDir, *args):
    cmds.duplicate (surface, n=(surface + "_sine_bsh"))   
    cmds.duplicate (surface, n=(surface + "_twist_bsh"))  

    sineDef = cmds.nonLinear((surface + "_sine_bsh"), typ="sine")    
    sineTwi = cmds.nonLinear((surface + "_twist_bsh"), typ="twist")

    if ribbonDir == "Horizontal": cmds.rotate (0, 0, 90, sineDef[1], sineTwi[1], r=1, os=1)

    cmds.rename (sineDef[0], (surface + "_sine_def"))
    cmds.rename (sineTwi[0], (surface + "_twist_def"))        
    cmds.rename (sineDef[1], (surface + "_sine_def_handle"))
    cmds.rename (sineTwi[1], (surface + "_twist_def_handle"))
    
    cmds.blendShape ((surface + "_sine_bsh"), (surface + "_twist_bsh"), surface, n=(surface + "_def_bsh"), foc=1)

    cmds.addAttr (surface, ln="deformOptions", nn="--------", at="enum", en="DEFORM", k=1)
    cmds.addAttr(surface, ln="Sine_Blend", s=1, at="double", min=0, max=1, k=1)
    cmds.addAttr(surface, ln="Twist_Blend", s=1, at="double", min=0, max=1, k=1)
    cmds.addAttr (surface, ln="sineOptions", nn="--------", at="enum", en="SINE", k=1)
    cmds.addAttr(surface, ln="Amplitude", s=1, at="double", k=1)
    cmds.addAttr(surface, ln="Wavelength", s=1, at="double", k=1)
    cmds.addAttr(surface, ln="Orientation", s=1, at="double", k=1)
    cmds.addAttr(surface, ln="Animate", s=1, at="double", k=1)
    cmds.addAttr (surface, ln="twistOptions", nn="--------", at="enum", en="TWIST", k=1)
    cmds.addAttr(surface, ln="Root", s=1, at="double", k=1)
    cmds.addAttr(surface, ln="Tip", s=1, at="double", k=1)   
                        
    cmds.connectAttr ((surface + ".Sine_Blend"), (surface + "_def_bsh." + surface + "_sine_bsh"), f=1)        
    cmds.connectAttr ((surface + ".Twist_Blend"), (surface + "_def_bsh." + surface + "_twist_bsh"), f=1) 
    cmds.connectAttr ((surface + ".Amplitude"), (surface + "_sine_def_handleShape.amplitude"), f=1) 
    cmds.connectAttr ((surface + ".Wavelength"), (surface + "_sine_def_handleShape.wavelength"), f=1) 
    cmds.connectAttr ((surface + ".Orientation"), (surface + "_sine_def_handle.rotateY"), f=1) 
    cmds.connectAttr ((surface + ".Animate"), (surface + "_sine_def_handleShape.offset"), f=1) 
    cmds.connectAttr ((surface + ".Root"), (surface + "_twist_def_handleShape.startAngle"), f=1)         
    cmds.connectAttr ((surface + ".Tip"), (surface + "_twist_def_handleShape.endAngle"), f=1)  

    cmds.setAttr (surface + "_sine_def.dropoff", 1)
    cmds.setAttr ((surface + ".Wavelength"), 2)
    cmds.select(cl=1)
                               
#-------------------------------------------------------------------------------------------------------------------------------------
# Use UV Pin Instead of Follicles
def matrixConnect(surface, spans, direction, orientation, endorient, regenJoints):
    if regenJoints:
        globalScale = cmds.getAttr ((surface + ".globalScaleInput"))
        jointFlip = cmds.getAttr ((surface + ".jointOrientFlip"))
        resetJnt = cmds.getAttr ((surface + ".resetJntInput"))
        jointOrient = cmds.getAttr ((surface + ".jointOrientMenu"))
        worldEndPos = cmds.getAttr ((surface + ".worldEndPosInput"))
    else:
        globalScale = cmds.floatField("globalScaleInput", q=1, v=1)
        jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1) 
        jointFlip = cmds.checkBox("jointOrientFlip", q=1, v=1)
        resetJnt = cmds.checkBox("resetJntInput", q=1, v=1)
        worldEndPos = cmds.checkBox("worldEndPosInput", q=1, v=1)

    flipJnt = 3 if jointFlip else 0
    
    for i in range(0, spans):
        jointName = '_'.join((surface,'joint', str(i+1).zfill(2)))
        newJoint = cmds.joint (rad=0.15*globalScale, n=jointName)

        # UV PIN SETUP
        uvPin = cmds.shadingNode ("uvPin", au=1, n=(jointName + "_uvpin"))
        cmds.connectAttr (uvPin + ".outputMatrix[0]", jointName + ".offsetParentMatrix")
        cmds.connectAttr (surface + "Shape.worldSpace", uvPin + ".deformedGeometry")
        cmds.setAttr (uvPin + ".coordinate[0].coordinateV", 0.5)
        cmds.setAttr (uvPin + ".coordinate[0].coordinateU", (i/(spans - 1.0)))
        
        # LOGIC FOR AXIS ALIGNMENT
        if worldEndPos and i == (spans - 1):
            # Force the UV pin to use a "straight" world-aligned coordinate (Y-Up, X-Forward)
            cmds.setAttr(uvPin + ".normalAxis", 1) 
            cmds.setAttr(uvPin + ".tangentAxis", 0) 
            
            # TEMP FIX-------------------------------------------------------------------------------------------------------------------------////////////////////////////////////////--------------------------------------------------------------
            cmds.setAttr(newJoint + ".rotateX", 0)
            cmds.setAttr(newJoint + ".rotateY", -90)
            cmds.setAttr(newJoint + ".rotateZ", 90)
        elif resetJnt and i == 0:
            cmds.setAttr(uvPin + ".normalAxis", 2); cmds.setAttr(uvPin + ".tangentAxis", 1)          
        else:
            if jointOrient == "X": n, t = 1+flipJnt, 3-flipJnt
            elif jointOrient == "Y": n, t = 2+flipJnt, 4-flipJnt        
            else: n, t = 0+flipJnt, 5-flipJnt    
            cmds.setAttr(uvPin + ".normalAxis", n)
            cmds.setAttr(uvPin + ".tangentAxis", t)
                        
        if cmds.objExists("ribbon_joints"): cmds.parent(jointName, "ribbon_joints")
        else: cmds.group(jointName, n="ribbon_joints")
        cmds.select(cl=1)

#-------------------------------------------------------------------------------------------------------------------------------------
# Use Selected Ribbon
def useRibbon(*args):
    closedLoop = cmds.checkBox("ribbonLoop", q=1, v=1)
    matrixRibbon = cmds.checkBox("mtrxRibbonInput", q=1, v=1)
    selRibbonList = cmds.ls(sl=1)
    
    if selRibbonList:
        for selRibbon in selRibbonList:
            if not cmds.attributeQuery("jointOrientMenu", ex=1, n=selRibbon): cmds.error("Invalid ribbon.")
            
            spans = cmds.getAttr ((selRibbon + ".spans"))
            surface = cmds.getAttr ((selRibbon + ".RibbonName"))
            orientation = cmds.getAttr ((selRibbon + ".jointOrientMenu"))
            direction = cmds.getAttr ((selRibbon + ".direction"))
            orientation = (cmds.getAttr (selRibbon + ".orientationX"), cmds.getAttr (selRibbon + ".orientationY"), cmds.getAttr (selRibbon + ".orientationZ"))
            endorient = (cmds.getAttr (selRibbon + ".endorientX"), cmds.getAttr (selRibbon + ".endorientY"), cmds.getAttr (selRibbon + ".endorientZ"))
            
            if cmds.objExists(surface + "_skinCluster"):cmds.skinCluster(surface + "Shape", e=1, ub=1)
            if cmds.objExists(surface + "_follicles"): cmds.delete(surface + "_follicles")
            if cmds.objExists(surface + "_ctrljnts"): cmds.delete(surface + "_ctrljnts")
            if cmds.objExists(surface + "_controls"): cmds.delete(surface + "_controls")
                        
            if cmds.objExists(surface + "_jiggle"):
                cmds.delete(surface + "_jiggle")
                cmds.deleteAttr(surface, at="muscleOptions")
                cmds.deleteAttr(surface, at="Enable")
                cmds.deleteAttr(surface, at="Amount")
                cmds.deleteAttr(surface, at="Flexability")
                cmds.deleteAttr(surface, at="Float")   

            if matrixRibbon: matrixConnect(surface, spans, direction, orientation, endorient, 0)
            else: addFollicles(surface, spans, direction, orientation, endorient)            

            if closedLoop: buildGenRibControls(surface, spans)
            else: buildCustomControls(surface, "", 1, matrixRibbon, spans, 0)
        cleanRibbon(surface, matrixRibbon)
        addRibbonJiggle(surface)
    else: cmds.error("Please select a ribbon to add follicles to.")
    
#-------------------------------------------------------------------------------------------------------------------------------------
# Create Follicle Function
def addFollicles(surface, spans, direction, orientation, endorient):
    globalScale = cmds.floatField("globalScaleInput", q=1, v=1)
    worldEndPos = cmds.checkBox("worldEndPosInput", q=1, v=1)
    
    for i in range(0, spans):        
        follicleName = '_'.join((surface,'follicle', str(i+1).zfill(2)))
        jointName = '_'.join((surface,'joint', str(i+1).zfill(2)))
              
        follicle = cmds.createNode('transform', n=follicleName, ss=1)
        follicleShape = cmds.createNode('follicle', n=follicle+'Shape', p=follicle, ss=1)

        cmds.connectAttr(surface + ".local", follicleShape + ".inputSurface")
        cmds.connectAttr(surface + ".worldMatrix[0]", follicleShape + ".inputWorldMatrix")
        cmds.connectAttr(follicleShape + ".outRotate", follicle + ".rotate")
        cmds.connectAttr(follicleShape + ".outTranslate", follicle + ".translate")
        cmds.setAttr(follicle + ".inheritsTransform", False)

        cmds.setAttr(follicleShape + ".parameterU", i/(spans - 1.0))
        cmds.setAttr(follicleShape + ".parameterV", 0.5)
                   
        jntPos = cmds.xform (follicle, q=True, ws=True, piv=True)
        newJoint = cmds.joint (rad=.05*globalScale, p=(jntPos[0], jntPos[1], jntPos[2]), n=jointName)
        cmds.parent (newJoint, follicle)

        if worldEndPos and i == (spans - 1):
            cmds.rotate(0, 0, 0, newJoint, ws=True, pcp=True)
            # Apply the 90 degree fix on Y relative to the world ----------------------------------------------------------------///////////////////////////////---------------------------------------------------------
            cmds.rotate(0, -90, 90, newJoint, a=True, ws=True)
        
        elif i == 0: 
            cmds.matchTransform(newJoint, follicle, rot=1)
            cmds.rotate (endorient[0], endorient[1], endorient[2], newJoint, r=1, os=1, fo=1)
        
        else: 
            cmds.matchTransform(newJoint, follicle, rot=1)
            cmds.rotate (orientation[0], orientation[1], orientation[2], newJoint, r=1, os=1, fo=1)             
            
    cmds.select(cl=1)
#-------------------------------------------------------------------------------------------------------------------------------------
# Build Ribbon Controls - Generated From Polys
def buildGenRibControls(ribbonNme, ribbonSpans):
    globalScale = cmds.floatField("globalScaleInput", q=1, v=1)
    matrixRibbon = cmds.checkBox("mtrxRibbonInput", q=1, v=1)
    offsetControl = cmds.floatField("controlOffsetInput", q=1, v=1)
    ribbonRatio = cmds.optionMenu("controlRatioMenu", q=1, v=1)
    controlGroup = cmds.checkBox("contGroupInput", q=1, v=1)
    jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1)

    if "Alt" in ribbonRatio: spanNumber = 2; ribbonRatio = ribbonRatio[0]
    else: spanNumber = 1
        
    colour = [0, 1, 0]

    if matrixRibbon:
        controlNormal = (0, 1, 0)
        moveAmount = (0, offsetControl*globalScale, 0)
    else:
        controlNormal = (0, 0, 1) if jointOrient == "Z" else ((0, 1, 0) if jointOrient == "Y" else (1, 0, 0))
        moveAmount = (controlNormal[0]*offsetControl*globalScale, controlNormal[1]*offsetControl*globalScale, controlNormal[2]*offsetControl*globalScale)
        
    for i in range(1, ribbonSpans):
        if i == spanNumber:
            if i < 10: spanNumberStr = "0" + str(i)
            if i >= 10: spanNumberStr = str(i)

            jointName =  (ribbonNme + "_joint_" + spanNumberStr)
            cmds.duplicate(jointName, n=jointName.replace("joint", "ctrljnt"))
            if not matrixRibbon: cmds.parent(jointName.replace("joint", "ctrljnt"), w=1)

            cmds.circle (nr=controlNormal, n=jointName.replace("joint", "control"), r=0.25*globalScale, s=12, ch=0)
            cmds.setAttr ((jointName.replace("joint", "control") + ".ove"), 1)
            cmds.setAttr((jointName.replace("joint", "control") + ".overrideRGBColors"), 1)
            cmds.setAttr ((jointName.replace("joint", "control") + ".overrideColorRGB"), colour[0], colour[1], colour[2])

            if controlGroup:
                cmds.group(jointName.replace("joint", "control"), n=jointName.replace("joint", "control") + "_offset")
                cmds.group(jointName.replace("joint", "control") + "_offset", n=jointName.replace("joint", "control") + "_driver")
                cmds.matchTransform(jointName.replace("joint", "control") + "_driver", jointName, pos=1, rot=1)
            else:
                cmds.group(jointName.replace("joint", "control"), n=jointName.replace("joint", "control") + "_offset")
                cmds.matchTransform(jointName.replace("joint", "control") + "_offset", jointName, pos=1, rot=1)

            cmds.parentConstraint(jointName.replace("joint", "control"), jointName.replace("joint", "ctrljnt"), mo=0)
            cmds.move(moveAmount[0], moveAmount[1], moveAmount[2], jointName.replace("joint", "control") + ".cv[0:11]", r=1, os=1)
            spanNumber = spanNumber + int(ribbonRatio)

    ctrljntList = cmds.ls((ribbonNme + "_ctrljnt_*"), type="joint")
    cmds.skinCluster(ribbonNme, ctrljntList, dr=3, mi=2, n=(ribbonNme + "_skinCluster"))

#-------------------------------------------------------------------------------------------------------------------------------------
# Duplicate and reset joints position
def dupeJoint(source, target, newName, radius):
    cmds.duplicate(source, n=newName)
    cmds.matchTransform(newName, target, pos=1, rot=1)  
    cmds.makeIdentity (newName, a=1, t=0, r=1, s=1)
    cmds.joint(newName, e=1, rad=radius)
    childList = cmds.listRelatives(newName, f=1)
    if childList: cmds.delete(childList)
         
#-------------------------------------------------------------------------------------------------------------------------------------
# Build Custom Ribbon Controls
def buildCustomControls(ribbonNme, jntList, genRibbon, matrixRibbon, ribbonDiv, quadLimbInput):
    globalScale = cmds.floatField("globalScaleInput", q=1, v=1)
    jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1)
    controlGroup = cmds.checkBox("contGroupInput", q=1, v=1)
    controlRatio = cmds.optionMenu("controlRatioMenu", q=1, v=1)
    snapToInput = cmds.checkBox("snapToInput", q=1, v=1)                
    ribbonLen = cmds.intField("lengthCount", q=1, v=1)
    ribbonLoop = cmds.checkBox("ribbonLoop", q=1, v=1)
    tweakCtrl = cmds.checkBox("twkControlsInput", q=1, v=1)
    angleCtrl = cmds.checkBox("angleControlsInput", q=1, v=1)
    resetJnt = cmds.checkBox("resetJntInput", q=1, v=1)
    offsetControl = cmds.floatField("controlOffsetInput", q=1, v=1)
    
    if jntList:
        if "l_" in jntList[0].lower(): colour = [1, 0, 0]
        elif "r_" in jntList[0].lower(): colour = [0, 0, 1]
        else: colour = [0, 1, 0]
    else: colour = [0, 1, 0]
         
    if genRibbon: limbDivisions = int(controlRatio)
    else:
        if quadLimbInput: limbDivisions = int(ribbonDiv/3)
        else: limbDivisions = int(ribbonDiv/2)
                
    jointNumber = 1
    cntrlJointList = []

    for i in range(1, ribbonDiv+1):
        if i == jointNumber or i == ribbonDiv:            
            if i < 10: buffer = "_0" + str(i)
            else: buffer = "_" + str(i)
                            
            dupeJoint((ribbonNme + "_joint" + buffer), (ribbonNme + "_joint" + buffer), (ribbonNme + "_ctrljnt" + buffer), 0.1*globalScale)
            if not matrixRibbon: cmds.parent((ribbonNme + "_ctrljnt" + buffer), w=1)

            moveAmount = (0, 0, offsetControl*globalScale)
                
            if genRibbon: controlOri = (0, 0, 1)
            elif jointOrient == "Z": controlOri = (0, 0, 1)
            elif jointOrient == "Y": controlOri = (0, 1, 0)
            else: controlOri = (1, 0, 0)   

            if matrixRibbon:
                controlOri = (0, 1, 0)
                moveAmount = (0, offsetControl*globalScale, 0)

            if resetJnt:
                if i == 1: controlNormal = (0, 1, 0)
        
            cmds.circle (nr=controlOri, n=(ribbonNme + "_control" + buffer), r=0.25*globalScale, s=12, ch=0)
            cmds.setAttr ((ribbonNme + "_control" + buffer + ".ove"), 1)
            cmds.setAttr((ribbonNme + "_control" + buffer + ".overrideRGBColors"), 1)
            cmds.setAttr ((ribbonNme + "_control" + buffer + ".overrideColorRGB"), colour[0], colour[1], colour[2])

            if controlGroup:
                cmds.group((ribbonNme + "_control" + buffer), n=(ribbonNme + "_control" + buffer + "_driver"))
                cmds.group((ribbonNme + "_control" + buffer + "_driver"), n=(ribbonNme + "_control" + buffer + "_offset"))
            else:
                cmds.group((ribbonNme + "_control" + buffer), n=(ribbonNme + "_control" + buffer + "_offset"))
                
            cmds.matchTransform((ribbonNme + "_control" + buffer + "_offset"), (ribbonNme + "_ctrljnt" + buffer), pos=1, rot=1)
            cmds.parentConstraint((ribbonNme + "_control" + buffer), (ribbonNme + "_ctrljnt" + buffer), mo=0)
            jointNumber = jointNumber + limbDivisions

            if genRibbon: cmds.move(moveAmount[0], moveAmount[1], moveAmount[2], (ribbonNme + "_control" + buffer + ".cv[0:11]"), r=1, os=1)
            cntrlJointList.append((ribbonNme + "_ctrljnt" + buffer))

    if not genRibbon:
        if tweakCtrl: addTweakControls(ribbonNme, cntrlJointList, quadLimbInput, controlOri)
        if angleCtrl: addAngleControls(ribbonNme, cntrlJointList, quadLimbInput, controlOri)
    
    cmds.skinCluster(ribbonNme, (cmds.ls(((ribbonNme + "_ctrljnt_*"), (ribbonNme + "_angle_*")), type="joint")), tsb=1, dr=10, n=(ribbonNme + "_skinCluster"))        

    if jntList:
        if snapToInput:
            if quadLimbInput: limbJntCount = 4
            else: limbJntCount = 3     

            limbJointList = cmds.listRelatives(jntList[0], ad=1, type="joint")
            limbJointList.append(jntList[0])
            controlGrpList = cmds.ls((ribbonNme + "_control_*_offset"))
            controlGrpList.reverse()
            for i in range(limbJntCount):            
                cmds.matchTransform(controlGrpList[i], limbJointList[i], pos=1, rot=1)

#-------------------------------------------------------------------------------------------------------------------------------------
# Add Angle Controls
def addAngleControls(ribbonNme, cntrlJointList, quadLimbInput, controlOri, *args):
    globalScale = cmds.floatField("globalScaleInput", q=1, v=1)
       
    for i in range(len(cntrlJointList)-1):
        dupeJoint(cntrlJointList[i], cntrlJointList[i], (cntrlJointList[i].replace("_ctrljnt_", "_angle_")), 0.25*globalScale)
        dupeJoint(cntrlJointList[i], cntrlJointList[i+1], (cntrlJointList[i].replace("_ctrljnt_", "_angletip_")), 0.25*globalScale)
        cmds.parent((cntrlJointList[i].replace("_ctrljnt_", "_angletip_")), (cntrlJointList[i].replace("_ctrljnt_", "_angle_")))
        cmds.parent((cntrlJointList[i].replace("_ctrljnt_", "_angle_")), cntrlJointList[i])
        cmds.ikHandle( n=(cntrlJointList[i].replace("_ctrljnt_", "_ikHandle_")), sol="ikRPsolver", sj=(cntrlJointList[i].replace("_ctrljnt_", "_angle_")), ee=(cntrlJointList[i].replace("_ctrljnt_", "_angletip_")) )
        cmds.setAttr(cntrlJointList[i].replace("_ctrljnt_", "_ikHandle_") + ".poleVector", 0, 0, 0, type="double3")
        cmds.setAttr(cntrlJointList[i].replace("_ctrljnt_", "_ikHandle_") + ".rotate", 0, 0, 0, type="double3")
        cmds.pointConstraint(cntrlJointList[i+1], cntrlJointList[i].replace("_ctrljnt_", "_ikHandle_"), mo=1)
                        
#-------------------------------------------------------------------------------------------------------------------------------------
# Add Tweak Controls
def addTweakControls(ribbonNme, cntrlJointList, quadLimbInput, controlOri, *args):
    jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1)  
    globalScale = cmds.floatField("globalScaleInput", q=1, v=1)

    if jointOrient == "X": controlUp = (0, 1, 0)
    elif jointOrient == "Y": controlUp = (0, 0, 1)
    else: controlUp = (1, 0, 0)

    if cmds.checkBox("jointOrientFlip", q=1, v=1): controlOri = (controlOri[0]*-1, controlOri[1]*-1, controlOri[2]*-1)        
    if quadLimbInput: tweakCount = 3
    else: tweakCount = 2
        
    for i in range(tweakCount):
        buildIcon((ribbonNme + "_tweak_" + str(i)), 0.5*globalScale)
        dupeJoint(cntrlJointList[i], cntrlJointList[i], (cntrlJointList[i] + "_tweak"), 0.1*globalScale)
        
        cmds.setAttr ((ribbonNme + "_tweak_" + str(i) + ".ove"), 1)
        cmds.setAttr((ribbonNme + "_tweak_" + str(i) + ".overrideRGBColors"), 1)
        cmds.setAttr ((ribbonNme + "_tweak_" + str(i) + ".overrideColorRGB"), 0, 1, 1)

        cmds.group((ribbonNme + "_tweak_" + str(i)), n=(ribbonNme + "_tweak_" + str(i) + "_aim"))
        cmds.group((ribbonNme + "_tweak_" + str(i) + "_aim"), n=(ribbonNme + "_tweak_" + str(i) + "_offset"))
        cmds.matchTransform((ribbonNme + "_tweak_" + str(i) + "_offset"), cntrlJointList[i+1], rot=1)
        cmds.pointConstraint(cntrlJointList[i], cntrlJointList[i+1], (ribbonNme + "_tweak_" + str(i) + "_offset"), mo=0)
        cmds.aimConstraint( cntrlJointList[i], (ribbonNme + "_tweak_" + str(i) + "_aim"), w=1, aim=controlOri, u=controlUp, wu=controlUp, wut="objectrotation", wuo=(cntrlJointList[i]), mo=0 ) 
        cmds.parentConstraint((ribbonNme + "_tweak_" + str(i)), (cntrlJointList[i] + "_tweak"), mo=0)
            
#-------------------------------------------------------------------------------------------------------------------------------------
# Build Custom Ribbon
def custRibbon(*args):
    globalScale = cmds.floatField("globalScaleInput", q=1, v=1)
    ribbonDir = cmds.optionMenu("ribbonDirMenu", q=1, v=1)
    ribbonOri = cmds.optionMenu("ribbonOrientMenu", q=1, v=1)
    ribbonDiv = cmds.intField("divisCount", q=1, v=1)   
    ribbonLen = cmds.intField("lengthCount", q=1, v=1) 
    ribbonNme = cmds.textField("nameInput", q=1, tx=1) 
    jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1) 
    jointFlip = cmds.checkBox("jointOrientFlip", q=1, v=1)
    addCrease = cmds.checkBox("addCreaseInput", q=1, v=1)
    addControls = cmds.checkBox("controlsInput", q=1, v=1)
    snapToInput = cmds.checkBox("snapToInput", q=1, v=1)
    matrixRibbon = cmds.checkBox("mtrxRibbonInput", q=1, v=1)
    quadLimbInput = cmds.checkBox("quadLimbInput", q=1, v=1)
    addDeformers = cmds.checkBox("addDeformInput", q=1, v=1)
    resetJnt = cmds.checkBox("resetJntInput", q=1, v=1)
    # New check
    worldEndPos = cmds.checkBox("worldEndPosInput", q=1, v=1)

    if quadLimbInput: limbJntCount = 4
    else: limbJntCount = 3
        
    jntRoot = cmds.ls(sl=1, ap=1, type="joint")
    if snapToInput:
        if not jntRoot: cmds.error("Please select the root joint of the limb if you want to snap the controls to it.")

    if cmds.objExists(ribbonNme): cmds.error("A ribbon with that name already exists, choose another name.")

    if jntRoot:                
        limbJointList = cmds.listRelatives(jntRoot[0], ad=1, type="joint")
        limbJointList.append(jntRoot[0])
        ribbonLen = 0.0
        for i in range(limbJntCount-1):            
            ribbonLen = ribbonLen + getTempDistance(limbJointList[i], limbJointList[i+1])
   
    lengthRatio = 0.15

    if ribbonOri == "X": planeAxis = [1, 0, 0]
    if ribbonOri == "Y": planeAxis = [0, 1, 0]
    if ribbonOri == "Z": planeAxis = [0, 0, 1]

    if jointFlip:   
        if jointOrient == "X": ribbonJointOrient = [-90, 0, 0]; endJointOrient = [0, 0, -90]   
        elif jointOrient == "Y": ribbonJointOrient = [0, 180, -90]; endJointOrient = [0, 0, -90]   
        else: ribbonJointOrient = [0, 90, 0]; endJointOrient = [0, 0, -90] 
    else:
        if jointOrient == "X": ribbonJointOrient = [-90, -180, 0]; endJointOrient = [0, 0, -90]   
        elif jointOrient == "Y": ribbonJointOrient = [0, 0, 90]; endJointOrient = [0, 0, -90]               
        else: ribbonJointOrient = [0, -90, 0]; endJointOrient = [0, 0, -90]  

    if not resetJnt: endJointOrient = ribbonJointOrient      
            
    if not quadLimbInput: multi = 2; baseDivisions = 5
    else: multi = 3; baseDivisions = 7
        
    for i in range(1, ribbonDiv): baseDivisions = baseDivisions + multi
                  
    cmds.nurbsPlane(w=ribbonLen, d=3, u=baseDivisions-1, v=1, lr=lengthRatio, ax=planeAxis, ch=0, n=ribbonNme)

    if ribbonDir == "Vertical":
        cmds.setAttr ((ribbonNme + ".rotate" + ribbonOri), 90)
        cmds.makeIdentity (ribbonNme, a=1, t=0, r=1, s=1)

    if addCrease:
        if quadLimbInput:
            cmds.insertKnotSurface((ribbonNme + ".u[0.325]"), ch=0, nk=7, add=1, ib=0, rpo=1)
            cmds.insertKnotSurface((ribbonNme + ".u[0.340]"), ch=0, nk=7, add=1, ib=0, rpo=1)
            cmds.insertKnotSurface((ribbonNme + ".u[0.660]"), ch=0, nk=7, add=1, ib=0, rpo=1)
            cmds.insertKnotSurface((ribbonNme + ".u[0.675]"), ch=0, nk=7, add=1, ib=0, rpo=1)
        else:
            cmds.insertKnotSurface((ribbonNme + ".u[0.495]"), ch=0, nk=7, add=1, ib=0, rpo=1)
            cmds.insertKnotSurface((ribbonNme + ".u[0.505]"), ch=0, nk=7, add=1, ib=0, rpo=1)
            
    cmds.select(cl=1)

    if addDeformers:
        addRibbonDeformers(ribbonNme, ribbonDir)    
        addRibbonJiggle(ribbonNme)

    if matrixRibbon: matrixConnect(ribbonNme, baseDivisions, ribbonDir.lower(), ribbonJointOrient, endJointOrient, 0)
    else:
        storeRibData(ribbonNme, baseDivisions, ribbonDir.lower(), ribbonJointOrient, endJointOrient)
        addFollicles(ribbonNme, baseDivisions, ribbonDir.lower(), ribbonJointOrient, endJointOrient)   

    if addControls: buildCustomControls(ribbonNme, jntRoot, 0, matrixRibbon, baseDivisions, quadLimbInput)
    cleanRibbon(ribbonNme, matrixRibbon)

#-------------------------------------------------------------------------------------------------------------------------------------
# Build Polygon Selection Ribbon
def storeEdges(whichSide, *args):
    cmds.polyToCurve(f=2, dg=3, usm=0, n=("temp" + whichSide + "curve"))
    cmds.button((whichSide + "Button"), e=1, en=0)
    if cmds.objExists("tempinnercurve") and cmds.objExists("tempoutercurve"): cmds.button("polyRibbonButton", e=1, en=1)  
    cmds.select(cl=1)
              
def polyRibbon(*args):
    jntList = []
    jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1) 
    jointFlip = cmds.checkBox("jointOrientFlip", q=1, v=1)
    normalFlip = cmds.checkBox("flipRibbonNormals", q=1, v=1)
    ribbonNme = cmds.textField("nameInput", q=1, tx=1)
    addControls = cmds.checkBox("controlsInput", q=1, v=1)
    closedLoop = cmds.checkBox("ribbonLoop", q=1, v=1)
    matrixRibbon = cmds.checkBox("mtrxRibbonInput", q=1, v=1)
    reduceCurve = cmds.checkBox("reduceRibbonSpans", q=1, v=1)

    if cmds.objExists(ribbonNme): cmds.error("A ribbon with that name already exists, choose another name.")
    
    if jointFlip: invert = -1
    else: invert = 1

    if reduceCurve:
        spanCount = cmds.getAttr("tempinnercurve.spans")
        cmds.rebuildCurve("tempinnercurve", rpo=1, rt=0, s=spanCount/2, ch=1)
        cmds.rebuildCurve("tempoutercurve", rpo=1, rt=0, s=spanCount/2, ch=1)

    if normalFlip: cmds.loft("tempinnercurve", "tempoutercurve", r=0, ch=0, u=1, c=0, ar=1, d=1, ss=1, rn=0, po=0, rsn=1, n=ribbonNme) 
    else: cmds.loft("tempinnercurve", "tempoutercurve", r=0, ch=0, u=1, c=0, ar=1, d=1, ss=1, rn=0, po=0, rsn=1, n=ribbonNme)         
        
    ribbonDiv = cmds.getAttr(ribbonNme + ".spansU")
    ribbonJointOrient = [0, 0, 0]    
    endJointOrient = [0, 0, 0]    
    cmds.select(cl=1)

    if matrixRibbon: matrixConnect(ribbonNme, ribbonDiv+1, "horizontal", ribbonJointOrient, endJointOrient, 0)
    else:
        storeRibData(ribbonNme, ribbonDiv+1, "horizontal", ribbonJointOrient, endJointOrient)
        addFollicles(ribbonNme, ribbonDiv+1, "horizontal", ribbonJointOrient, endJointOrient)  

    cmds.delete("tempoutercurve", "tempinnercurve")
    
    cmds.button("polyRibbonButton", e=1, en=0)   
    cmds.button("outerButton", e=1, en=1)
    cmds.button("innerButton", e=1, en=1)       

    if addControls:
        if closedLoop: buildGenRibControls(ribbonNme, ribbonDiv+1)
        else: buildCustomControls(ribbonNme, jntList, 1, matrixRibbon, ribbonDiv+1, 0)

    cleanRibbon(ribbonNme, matrixRibbon)
    addRibbonJiggle(ribbonNme)

#-------------------------------------------------------------------------------------------------------------------------------------    
# USER 3-TAB UI
#-------------------------------------------------------------------------------------------------------------------------------------
def snapTo(*args):
    state = cmds.checkBox("controlsInput", q=1, v=1)
    for ctrl in ["snapToInput", "twkControlsInput", "angleControlsInput", "addDeformInput"]:
        cmds.checkBox(ctrl, e=1, en=state)

def RibbonUI():
    if cmds.window("RibbonTool", ex=1): cmds.deleteUI("RibbonTool")
    
    window = cmds.window("RibbonTool", t="Ribbon Tool v03", w=300, h=450, s=1)
    main_layout = cmds.columnLayout(adj=True)
    
    # --- Tab Layout ---
    tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
    
    # --- TAB 1: SETTINGS ---
    tab1 = cmds.columnLayout(adj=True, rowSpacing=10)
    cmds.separator(h=5, style='none')
    cmds.text("GLOBAL CONFIGURATION", fn="boldLabelFont")
    
    cmds.rowLayout(nc=2, ad2=2, cl2=("left", "left"))
    cmds.text(l="Ribbon Name: ")
    cmds.textField("nameInput", tx="Ribbon_ASSET", h=25)
    cmds.setParent('..')
    
    cmds.rowLayout(nc=2, ad2=2)
    cmds.text(l="Overall Scale: ")
    defVal = 20 if cmds.currentUnit(q=1, f=1) == "centimeter" else 1
    cmds.floatField("globalScaleInput", v=defVal, pre=2)
    cmds.setParent('..')

    cmds.separator(h=10)
    cmds.text("JOINT ORIENTATION", fn="boldLabelFont")
    cmds.rowLayout(nc=3, ad3=2)
    cmds.text(l="Primary Axis: ")
    cmds.optionMenu("jointOrientMenu")
    cmds.menuItem(l="Z"); cmds.menuItem(l="X"); cmds.menuItem(l="Y")
    cmds.checkBox("jointOrientFlip", l="Invert Axis")
    cmds.setParent('..')
    
    cmds.separator(h=10)
    cmds.text("CAPABILITIES", fn="boldLabelFont")
    cmds.rowColumnLayout(nc=2, cw=[(1, 140), (2, 140)])
    cmds.checkBox("mtrxRibbonInput", l="Use Matrix (2020+)", v=1)
    cmds.checkBox("addJiggleInput", l="Add Jiggle/Wobble")
    cmds.checkBox("controlsInput", l="Build Controls", v=1, cc=snapTo)
    cmds.checkBox("contGroupInput", l="Extra Driver Group")
    cmds.checkBox("twkControlsInput", l="Tweak Controls", en=1)
    cmds.checkBox("angleControlsInput", l="Angle Controls", en=1)
    cmds.checkBox("addDeformInput", l="Add Deformers", en=1)
    cmds.checkBox("resetJntInput", l="World End Orient")
    cmds.checkBox("worldEndPosInput", l="End Point World Pos", v=0)
    cmds.setParent('..')
    cmds.setParent(tabs)

    # --- TAB 2: BUILD RIBBON ---
    tab2 = cmds.columnLayout(adj=True, rowSpacing=10)
    
    cmds.frameLayout(l="1. Create Custom Ribbon (Parametric)", cll=False, mw=5, mh=5)
    cmds.columnLayout(adj=True, rs=5)
    cmds.rowLayout(nc=4, ad4=4)
    cmds.text(l="Divisions: "); cmds.intField("divisCount", v=1)
    cmds.text(l="Length: "); cmds.intField("lengthCount", v=10)
    cmds.setParent('..')
    
    cmds.rowLayout(nc=2, ad2=2)
    cmds.optionMenu("ribbonDirMenu", l="Direction: ")
    cmds.menuItem(l="Vertical"); cmds.menuItem(l="Horizontal")
    cmds.optionMenu("ribbonOrientMenu", l="Plane Axis: ")
    cmds.menuItem(l="X"); cmds.menuItem(l="Y"); cmds.menuItem(l="Z")
    cmds.setParent('..')
    
    cmds.checkBox("quadLimbInput", l="Dog Leg (3-Joint Limb)")
    cmds.checkBox("addCreaseInput", l="Add Creases (Elbow/Knee)")
    cmds.checkBox("snapToInput", l="Snap to Selected Joints")
    cmds.button(l="BUILD CUSTOM RIBBON", h=40, bgc=(0.3, 0.4, 0.5), c=custRibbon)
    cmds.setParent('..')
    cmds.setParent('..')
    
    cmds.frameLayout(l="2. Generate From Mesh Edges", cll=False, mw=5, mh=5)
    cmds.columnLayout(adj=True, rs=5)
    cmds.rowLayout(nc=2, adj=1)
    cmds.button("outerButton", l="Set Outer Edges", c=partial(storeEdges, "outer"))
    cmds.button("innerButton", l="Set Inner Edges", c=partial(storeEdges, "inner"))
    cmds.setParent('..')
    
    cmds.rowLayout(nc=2, adj=1)
    cmds.checkBox("flipRibbonNormals", l="Flip Normals")
    cmds.checkBox("reduceRibbonSpans", l="Simplify Spans")
    cmds.setParent('..')
    
    cmds.rowLayout(nc=2, adj=1)
    cmds.text(l="Ctrl Ratio: ")
    cmds.optionMenu("controlRatioMenu")
    for i in ["1","2","2 Alt","3","4","5"]: cmds.menuItem(l=i)
    cmds.setParent('..')
    
    cmds.button("polyRibbonButton", l="GENERATE FROM EDGES", h=40, en=0, bgc=(0.3, 0.5, 0.4), c=polyRibbon)
    cmds.setParent('..')
    cmds.setParent('..')
    cmds.setParent(tabs)

    # --- TAB 3: MANAGEMENT ---
    tab3 = cmds.columnLayout(adj=True, rowSpacing=10)
    cmds.text("MODIFICATION TOOLS", fn="boldLabelFont")
    cmds.button(l="Update Selected Ribbon", h=35, c=useRibbon, ann="Rebuild follicles/controls on selected ribbon.")
    cmds.button(l="Convert Follicles to Matrix", h=35, c=convertToMatrix)
    cmds.separator(h=10)
    cmds.text("Control Offset Settings")
    cmds.floatField("controlOffsetInput", v=0, pre=2)
    cmds.checkBox("ribbonLoop", l="Closed Loop Ribbon")
    
    cmds.setParent(tabs)
    cmds.tabLayout(tabs, edit=True, tabLabel=((tab1, '1. Setup'), (tab2, '2. Build'), (tab3, '3. Manage')))
    cmds.showWindow(window)

    if int(cmds.about(v=1)) < 2020:
        cmds.checkBox("mtrxRibbonInput", e=1, v=0, en=0)

RibbonUI()