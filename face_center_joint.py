import maya.cmds as cmds
import maya.api.OpenMaya as om

def joint_on_closest_vertex():

    faces = cmds.ls(sl=True, fl=True)

    if not faces:
        cmds.error("Please select polygon faces.")

    # Convert selection
    sel = om.MSelectionList()
    for f in faces:
        sel.add(f)

    dag, comp = sel.getComponent(0)

    face_iter = om.MItMeshPolygon(dag, comp)

    centers = []

    while not face_iter.isDone():
        centers.append(face_iter.center())
        face_iter.next()

    # Average center
    avg = om.MVector()
    for c in centers:
        avg += om.MVector(c)

    avg /= len(centers)

    # Convert faces to vertices
    verts = cmds.polyListComponentConversion(faces, tv=True)
    verts = cmds.ls(verts, fl=True)

    closest_vert = None
    closest_dist = 1e10
    closest_pos = None

    for v in verts:
        pos = cmds.pointPosition(v, world=True)

        dist = (avg.x-pos[0])**2 + (avg.y-pos[1])**2 + (avg.z-pos[2])**2

        if dist < closest_dist:
            closest_dist = dist
            closest_vert = v
            closest_pos = pos

    # Create joint
    cmds.select(clear=True)
    jnt = cmds.joint(p=closest_pos, name="faceCenter_JNT")

    print("Joint created at:", closest_vert)

joint_on_closest_vertex()
