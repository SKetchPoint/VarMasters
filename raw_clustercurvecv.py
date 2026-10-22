import maya.cmds as cmds

def cluster_cv_on_selected_curve():
    """
    Clusters each control vertex (CV) on the selected curve and parents the clusters to the curve.
    Assumes one curve is selected in the scene.
    """
    # Step 1: Get the selected object
    selected = cmds.ls(selection=True)
    
    if len(selected) != 1:
        cmds.warning("Please select exactly one curve.")
        return
    
    curve_name = selected[0]
    
    # Step 2: Get the CVs of the curve
    cvs = cmds.ls(f"{curve_name}.cv[*]", flatten=True)
    
    # Step 3: Create clusters for each CV
    clusters = []

    # Create a cluster for each CV
    for cv in cvs:
        # Create a cluster for the CV
        cluster = cmds.cluster(cv)[1]

        # Parent the cluster to the curve (if needed)
        cmds.parent(cluster, curve_name)

        # Append cluster to list
        clusters.append(cluster)

    # Optional: Hide the clusters (optional cleanup)
    for cluster in clusters:
        cmds.setAttr(f"{cluster}.visibility", 0)

    print(f"Created clusters for {len(cvs)} CVs successfully!")
cluster_cv_on_selected_curve()
