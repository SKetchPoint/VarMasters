import maya.cmds as cmds
import math

# Function to calculate points between start and end locators
def calculate_points_spread(start, end, spread_factor, num_points):
    """
    Calculate points/joints between start and end based on the spread factor and make them.

    :param start: Tuple (x, y, z) for the start point.
    :param end: Tuple (x, y, z) for the end point.
    :param spread_factor: Float to determine spacing (0.5 for halving, 1 for equal, 2 for doubling).
    :param num_points: Total number of points, including start and end.
    """
    direction = (
        end[0] - start[0],
        end[1] - start[1],
        end[2] - start[2],
    )
    #square rt (xdif^2+ydif^2+zdif^2)=euclidean distance
    total_distance = math.sqrt(direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2)
    #normalize vector
    if total_distance != 0:
        direction_unit = (
            direction[0] / total_distance,
            direction[1] / total_distance,
            direction[2] / total_distance,
        )
    else:
        direction_unit = (0, 0, 0)
    #handling segments division 
    if spread_factor == 1:
        segment_length = total_distance / (num_points - 1)
        distances = [segment_length * i for i in range(num_points)]
    else:
        ratio = spread_factor
        initial_distance = total_distance * (1 - ratio) / (1 - ratio ** (num_points - 1))
        distances = [sum(initial_distance * (ratio ** j) for j in range(i)) for i in range(num_points)]

    points = []
    #geometric sequencing via common ratio 
    for dist in distances:
        position = (
            start[0] + direction_unit[0] * dist,
            start[1] + direction_unit[1] * dist,
            start[2] + direction_unit[2] * dist,
        )
        points.append(position)

    return points

def create_joint_chain(spread_factor_field, num_points_field, joint_radius_field):
    """
    Command to create the joint chain based on user input.
    """
    selected = cmds.ls(selection=True, transforms=True)

    if len(selected) != 2:
        cmds.warning("Please select exactly two locators or transforms.")
        return

    start = cmds.xform(selected[0], query=True, translation=True, worldSpace=True)
    end = cmds.xform(selected[1], query=True, translation=True, worldSpace=True)

    spread_factor = cmds.floatField(spread_factor_field, query=True, value=True)
    num_points = cmds.intField(num_points_field, query=True, value=True)
    joint_radius = cmds.floatField(joint_radius_field, query=True, value=True)

    points = calculate_points_spread(start, end, spread_factor, num_points)

    cmds.select(clear=True)  # Clear selection before creating joints
    joint_chain = []
    for i, position in enumerate(points):
        joint_name = f"joint_{i + 1:02d}"
        joint = cmds.joint(name=joint_name, position=position,radius=joint_radius)
        joint_chain.append(joint)

    print(f"Created joint chain: {joint_chain}")
    
