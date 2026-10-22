import maya.cmds as cmds
import math

# ---------------- Simulation Function ----------------
def create_bounce_sim(*args):
    obj = cmds.ls(selection=True)
    if not obj:
        cmds.warning("Please select an object to simulate.")
        return
    obj = obj[0]

    try:
        start_height = float(cmds.textField(startHeightField, query=True, text=True))
        floor_height = float(cmds.textField(floorHeightField, query=True, text=True))
        rest_time = float(cmds.textField(restTimeField, query=True, text=True))
        weight = cmds.textField(weightField, query=True, text=True)
        weight = float(weight) if weight else None
        vx = float(cmds.textField(velXField, query=True, text=True))
        vy = float(cmds.textField(velYField, query=True, text=True))
        vz = float(cmds.textField(velZField, query=True, text=True))
        air_density = float(cmds.textField(airDensityField, query=True, text=True))
        drag_coeff = float(cmds.textField(dragCoeffField, query=True, text=True))
        area = float(cmds.textField(areaField, query=True, text=True))
        # convert UI spin deg/sec -> rad/sec
        spinX = math.radians(float(cmds.textField(spinXField, query=True, text=True)))
        spinZ = math.radians(float(cmds.textField(spinZField, query=True, text=True)))
    except:
        cmds.warning("Invalid input. Please check all fields.")
        return

    # --- Material lookup ---
    material = cmds.optionMenu(materialMenu, query=True, value=True)
    materials = {
        "Rubber": {"restitution": 0.9, "friction": 0.8},
        "Steel": {"restitution": 0.6, "friction": 0.5},
        "Wood": {"restitution": 0.5, "friction": 0.6},
        "Glass": {"restitution": 0.95, "friction": 0.2},
        "Custom": {
            "restitution": float(cmds.textField(restitutionField, query=True, text=True)),
            "friction": float(cmds.textField(frictionField, query=True, text=True))
        }
    }
    restitution = materials[material]["restitution"]
    friction = materials[material]["friction"]

    g = 9.81  # gravity
    radius = math.sqrt(area / math.pi)
    # compute inertia: I = 2/5 m r^2 for a sphere
    I = (2.0/5.0) * (weight/g if weight else air_density*4/3*math.pi*radius**3) * radius**2

    # Mass
    if weight:
        mass = weight / g
    else:
        volume = (4/3) * math.pi * radius**3
        mass = air_density * volume  # crude approximation

    # Initial states
    pos = [0.0, start_height, 0.0]
    vel = [vx, vy, vz]
    omega = [spinX, 0.0, spinZ]  # angular velocity vector
    cumulative_rot = [0.0, 0.0, 0.0]  # cumulative rotation in radians

    # FPS
    fps = cmds.currentUnit(query=True, time=True)
    fps_map = {"game": 15.0, "film": 24.0, "pal": 25.0, "ntsc": 30.0,
               "show": 48.0, "palf": 50.0, "ntscf": 60.0}
    numeric_fps = fps_map.get(fps, 24.0)

    dt = 1.0 / (numeric_fps * 10)  # 10 substeps per frame
    t = 0.0
    step = 0
    max_steps = int(rest_time / dt)

    keyframes = []
    next_key_time = 0.0
    start_scene_frame = cmds.playbackOptions(query=True, min=True)

    while step < max_steps:
        # --- Forces ---
        Fg = -mass * g
        vmag = math.sqrt(sum(v**2 for v in vel))
        if vmag > 0:
            drag_mag = 0.5 * air_density * drag_coeff * area * vmag**2
            drag = [-drag_mag * v / vmag for v in vel]
        else:
            drag = [0, 0, 0]

        # Accelerations
        ax = drag[0] / mass
        ay = (Fg + drag[1]) / mass
        az = drag[2] / mass

        # Integrate velocity and position
        vel[0] += ax * dt
        vel[1] += ay * dt
        vel[2] += az * dt
        pos[0] += vel[0] * dt
        pos[1] += vel[1] * dt
        pos[2] += vel[2] * dt
        t += dt
        step += 1

        # --- Collision ---
        if pos[1] <= floor_height and vel[1] < 0:
            pos[1] = floor_height
            vel[1] *= -restitution

            # tangential friction at bounce
            vt = [vel[0], vel[2]]
            vtan_mag = math.sqrt(vt[0]**2 + vt[1]**2)
            if vtan_mag > 0:
                slip_dir = [vt[0]/vtan_mag, vt[1]/vtan_mag]
                slip_reduction = friction * g * dt
                reduction = min(vtan_mag, slip_reduction)
                vel[0] -= reduction * slip_dir[0]
                vel[2] -= reduction * slip_dir[1]

                # angular spin from torque (approx)
                alpha = (5.0/2.0) * (reduction / radius)
                omega[0] += -slip_dir[1] * alpha
                omega[2] += slip_dir[0] * alpha

        # --- Record only whole frame ---
        if t >= next_key_time:
            keyframes.append((next_key_time, tuple(pos), tuple(omega)))
            next_key_time += 1.0 / numeric_fps

    # --- Apply keys ---
    for sim_t, p, w in keyframes:
        scene_frame = start_scene_frame + int(round(sim_t * numeric_fps))
        cmds.currentTime(scene_frame, edit=True)
        cmds.xform(obj, worldSpace=True, translation=p)
        cmds.setKeyframe(obj, attribute="translateX", t=scene_frame)
        cmds.setKeyframe(obj, attribute="translateY", t=scene_frame)
        cmds.setKeyframe(obj, attribute="translateZ", t=scene_frame)

        # accumulate rotation
        delta_rot = [w[i] * (1.0/numeric_fps) for i in range(3)]
        for i in range(3):
            cumulative_rot[i] += delta_rot[i]

        # apply rotation in degrees using cumulative rotation
        cmds.rotate(math.degrees(cumulative_rot[0]),
                    math.degrees(cumulative_rot[1]),
                    math.degrees(cumulative_rot[2]),
                    obj, absolute=True, objectSpace=True)
        cmds.setKeyframe(obj, attribute="rotateX", t=scene_frame)
        cmds.setKeyframe(obj, attribute="rotateY", t=scene_frame)
        cmds.setKeyframe(obj, attribute="rotateZ", t=scene_frame)

    cmds.currentTime(start_scene_frame, edit=True)
    print("Simulation complete. Keys set.")


# ----------------- UI -----------------
if cmds.window("bounceSimWin", exists=True):
    cmds.deleteUI("bounceSimWin")

win = cmds.window("bounceSimWin", title="Ball Bounce Simulator", widthHeight=(300, 550))
layout = cmds.columnLayout(adjustableColumn=True)

cmds.text(label="Enter parameters:")

cmds.text(label="Start Height (m):")
startHeightField = cmds.textField(text="10")

cmds.text(label="Floor Height (m):")
floorHeightField = cmds.textField(text="0")

cmds.text(label="Rest Time (seconds):")
restTimeField = cmds.textField(text="10")

cmds.text(label="Weight (N, optional):")
weightField = cmds.textField()

cmds.text(label="Velocity X (m/s):")
velXField = cmds.textField(text="0")

cmds.text(label="Velocity Y (m/s):")
velYField = cmds.textField(text="0")

cmds.text(label="Velocity Z (m/s):")
velZField = cmds.textField(text="0")

cmds.text(label="Air Density (kg/m^3):")
airDensityField = cmds.textField(text="1.225")

cmds.text(label="Drag Coefficient:")
dragCoeffField = cmds.textField(text="0.47")

cmds.text(label="Cross Sectional Area (m^2):")
areaField = cmds.textField(text="0.05")

cmds.text(label="Initial Spin (deg/sec) X:")
spinXField = cmds.textField(text="0")

cmds.text(label="Initial Spin (deg/sec) Z:")
spinZField = cmds.textField(text="0")

cmds.text(label="Material:")
materialMenu = cmds.optionMenu()
for m in ["Rubber", "Steel", "Wood", "Glass", "Custom"]:
    cmds.menuItem(label=m)

cmds.text(label="Custom Restitution (if custom):")
restitutionField = cmds.textField(text="0.7")

cmds.text(label="Custom Friction (if custom):")
frictionField = cmds.textField(text="0.5")

cmds.button(label="Simulate Bounce", command=create_bounce_sim)

cmds.showWindow(win)
