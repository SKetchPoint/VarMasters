# Golden 3-Point Rig for Maya
# Paste this into Maya's Script Editor (Python tab) and run.
# Creates three locators (A, B, C) that preserve A->B : B->C = 1 : phi
# Moving any locator updates the others:
# - move A -> C fixed, B recalculated
# - move C -> A fixed, B recalculated
# - move B -> keep AC length, move A and C symmetrically on the same direction


import math
import maya.cmds as cmds

# Names (change if you want)
GRP = "golden3p_grp"
LOC_A = "gold_A_loc"
LOC_B = "gold_B_loc"
LOC_C = "gold_C_loc"
UI_WIN = "golden3p_win"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
SUM_1_PHI = 1.0 + PHI  # ~2.6180339887

# state flags
_golden_updating = False
_jobs = []

def _vec_sub(a, b):
    return [a[i] - b[i] for i in range(3)]

def _vec_add(a, b):
    return [a[i] + b[i] for i in range(3)]

def _vec_scale(v, s):
    return [v[i] * s for i in range(3)]

def _vec_len(v):
    return math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])

def _vec_norm(v):
    l = _vec_len(v)
    if l == 0.0:
        return [1.0, 0.0, 0.0]  # default axis
    return [v[i] / l for i in range(3)]

def _get_world_pos(node):
    return cmds.xform(node, q=True, ws=True, t=True)

def _set_world_pos(node, pos):
    cmds.xform(node, ws=True, t=pos)

def _ensure_nodes_exist():
    return cmds.objExists(LOC_A) and cmds.objExists(LOC_B) and cmds.objExists(LOC_C)

def golden_update(mover):
    """
    mover: 'A', 'B', or 'C' -- which locator triggered the change
    This function avoids recursion using _golden_updating flag.
    """
    global _golden_updating
    if _golden_updating:
        return
    _golden_updating = True
    try:
        if not _ensure_nodes_exist():
            return

        a_pos = _get_world_pos(LOC_A)
        b_pos = _get_world_pos(LOC_B)
        c_pos = _get_world_pos(LOC_C)

        # If A moved -> keep C fixed, recalc B on line A->C
        if mover == 'A':
            vec_ac = _vec_sub(c_pos, a_pos)
            L = _vec_len(vec_ac)
            if L < 1e-6:
                # if near zero length, nudge C to +X and recalc
                c_pos = _vec_add(a_pos, [1.0, 0.0, 0.0])
                _set_world_pos(LOC_C, c_pos)
                vec_ac = _vec_sub(c_pos, a_pos)
                L = _vec_len(vec_ac)
            frac_ab = 1.0 / SUM_1_PHI   # AB = L / (1+phi)
            b_new = _vec_add(a_pos, _vec_scale(vec_ac, frac_ab))
            _set_world_pos(LOC_B, b_new)

        # If C moved -> keep A fixed, recalc B on line A->C
        elif mover == 'C':
            vec_ac = _vec_sub(c_pos, a_pos)
            L = _vec_len(vec_ac)
            if L < 1e-6:
                # nudge A if degenerate
                a_pos = _vec_add(c_pos, [-1.0, 0.0, 0.0])
                _set_world_pos(LOC_A, a_pos)
                vec_ac = _vec_sub(c_pos, a_pos)
                L = _vec_len(vec_ac)
            frac_ab = 1.0 / SUM_1_PHI
            b_new = _vec_add(a_pos, _vec_scale(vec_ac, frac_ab))
            _set_world_pos(LOC_B, b_new)

        # If B moved -> keep total length L (prev A->C) and re-center A and C
        elif mover == 'B':
            prev_vec = _vec_sub(c_pos, a_pos)
            prev_L = _vec_len(prev_vec)
            # If previous length is degenerate, pick a default length (1.0)
            if prev_L < 1e-6:
                prev_L = 1.0
                dir_norm = [1.0, 0.0, 0.0]
            else:
                dir_norm = _vec_norm(prev_vec)

            # s = AB (base length) = L / (1 + phi)
            s = prev_L / SUM_1_PHI
            # place A at B - dir*s
            a_new = _vec_add(b_pos, _vec_scale(dir_norm, -s))
            # place C at B + dir*(s*phi)
            c_new = _vec_add(b_pos, _vec_scale(dir_norm, s * PHI))
            _set_world_pos(LOC_A, a_new)
            _set_world_pos(LOC_C, c_new)
        else:
            # unknown mover - do nothing
            pass

    finally:
        _golden_updating = False

def _on_attr_change_A():
    golden_update('A')

def _on_attr_change_B():
    golden_update('B')

def _on_attr_change_C():
    golden_update('C')

def create_golden_rig():
    """Create locators and scriptJobs to drive the rig."""
    global _jobs

    # cleanup if exists
    delete_golden_rig()

    # create group and locators
    grp = cmds.group(em=True, name=GRP)
    a = cmds.spaceLocator(name=LOC_A)[0]
    b = cmds.spaceLocator(name=LOC_B)[0]
    c = cmds.spaceLocator(name=LOC_C)[0]
    # default positions along X axis
    cmds.xform(a, ws=True, t=[0.0, 0.0, 0.0])
    cmds.xform(b, ws=True, t=[0.38, 0.0, 0.0])  # roughly 1/(1+phi)
    cmds.xform(c, ws=True, t=[1.0, 0.0, 0.0])

    # parent under group
    cmds.parent(a, grp)
    cmds.parent(b, grp)
    cmds.parent(c, grp)

    # create two small visual helpers: a line curve between A-C and text nodes (optional)
    pts = [ _get_world_pos(LOC_A), _get_world_pos(LOC_C) ]
    curve = cmds.curve(p=pts, degree=1, name="golden3p_line_crv")
    cmds.parent(curve, grp)

    # Set up attribute-change scriptJobs to watch translate attr changes
    # We create three jobs and keep the ids for cleanup.
    # Each scriptJob calls a small python wrapper that triggers our main update (golden_update).
    jobA = cmds.scriptJob(attributeChange=[LOC_A + ".translate", "import sys\nif 'maya' in sys.modules: from maya import cmds\nimport __main__\n__main__.golden_update('A')"], protected=True, kws=True)
    jobB = cmds.scriptJob(attributeChange=[LOC_B + ".translate", "import sys\nif 'maya' in sys.modules: from maya import cmds\nimport __main__\n__main__.golden_update('B')"], protected=True, kws=True)
    jobC = cmds.scriptJob(attributeChange=[LOC_C + ".translate", "import sys\nif 'maya' in sys.modules: from maya import cmds\nimport __main__\n__main__.golden_update('C')"], protected=True, kws=True)

    _jobs = [jobA, jobB, jobC]

    # initial update to ensure B is precisely on the golden split
    golden_update('A')

    print("Golden 3-point rig created. Move any locator (A, B, or C). To remove use delete_golden_rig().")

def delete_golden_rig():
    """Deletes locators, curve and scriptJobs created by this tool."""
    global _jobs
    # remove scriptJobs if they exist
    for j in list(_jobs):
        try:
            if cmds.scriptJob(exists=j):
                cmds.scriptJob(kill=j, force=True)
        except Exception:
            pass
    _jobs = []

    # delete UI if present
    if cmds.window(UI_WIN, exists=True):
        cmds.deleteUI(UI_WIN)

    # delete created nodes (group will parent children)
    for n in [LOC_A, LOC_B, LOC_C, "golden3p_line_crv", GRP]:
        try:
            if cmds.objExists(n):
                cmds.delete(n)
        except Exception:
            pass
    print("Golden 3-point rig deleted (if present).")

def build_ui():
    if cmds.window(UI_WIN, exists=True):
        cmds.deleteUI(UI_WIN)
    win = cmds.window(UI_WIN, title="Golden 3-Point Rig", widthHeight=(300, 100))
    cl = cmds.columnLayout(adj=True, rowSpacing=6)
    cmds.button(label="Create Golden 3-Point Rig", command=lambda *_: create_golden_rig())
    cmds.button(label="Delete Golden Rig", command=lambda *_: delete_golden_rig())
    cmds.text(label="Golden ratio φ = %.9f" % PHI)
    cmds.setParent('..')
    cmds.showWindow(win)

# Auto build small UI when running the script
if __name__ == '__main__':
    build_ui()
