import maya.cmds as cmds
import maya.api.OpenMaya as om

def average_face_normal():
    sel = cmds.ls(sl=True, fl=True)

    if not sel:
        cmds.error("Please select polygon faces.")

    # Convert to selection list
    sel_list = om.MSelectionList()
    for s in sel:
        sel_list.add(s)

    dag, comp = sel_list.getComponent(0)
    mesh_fn = om.MFnMesh(dag)

    face_iter = om.MItMeshPolygon(dag, comp)

    normals = []
    centers = []

    while not face_iter.isDone():
        normals.append(face_iter.getNormal())
        centers.append(face_iter.center())
        face_iter.next()

    # Average normal
    avg_normal = om.MVector()
    for n in normals:
        avg_normal += n
    avg_normal.normalize()

    # Average position
    avg_pos = om.MVector()
    for c in centers:
        avg_pos += om.MVector(c)
    avg_pos /= len(centers)

    # Create locator
    loc = cmds.spaceLocator(name="avgNormal_LOC")[0]
    cmds.xform(loc, ws=True, t=(avg_pos.x, avg_pos.y, avg_pos.z))

    # Build orientation matrix
    up = om.MVector(0,1,0)
    if abs(avg_normal * up) > 0.99:
        up = om.MVector(1,0,0)

    x = up ^ avg_normal
    x.normalize()
    y = avg_normal ^ x
    y.normalize()
    z = avg_normal

    matrix = [
        x.x,x.y,x.z,0,
        y.x,y.y,y.z,0,
        z.x,z.y,z.z,0,
        avg_pos.x,avg_pos.y,avg_pos.z,1
    ]

    cmds.xform(loc, ws=True, matrix=matrix)

average_face_normal()
