# SPDX-FileCopyrightText: 2020-2026 McHorse
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy_extras.wm_utils.progress_report import ProgressReport, ProgressReportSubstep

# Map the shorthand data path written by the exporter back to the real property name
DATA_PATHS = {
    'location': 'location',
    'rotation': 'rotation_euler',
    'scale': 'scale',
}

# Find or create an F-Curve for the given data-block, regardless of whether
# this Blender uses the legacy flat fcurve list or the layered
# layers/strips/channelbags/slots data model (added in Blender 4.4)
def ensure_fcurve(action, obj, data_path, index, group_name):
    if hasattr(action, 'fcurve_ensure_for_datablock'):
        return action.fcurve_ensure_for_datablock(obj, data_path, index=index, group_name=group_name)

    fcurve = action.fcurves.find(data_path, index=index)

    if fcurve is None:
        fcurve = action.fcurves.new(data_path, index=index, action_group=group_name)

    return fcurve

def load(context, filepath):
    obj = context.object

    if obj is None or obj.type != 'ARMATURE':
        return {'CANCELLED'}, "Select the Armature object this BOBJ file was exported from"

    with ProgressReport(context.window_manager) as progress:
        progress.enter_substeps(1)
        result = read_file(context, filepath, obj, progress)
        progress.leave_substeps()

    return result

def read_file(context, filepath, obj, progress=ProgressReport()):
    with ProgressReportSubstep(progress, 2, "BOBJ Import path: %r" % filepath, "BOBJ Import Finished") as subprogress1:
        scene = context.scene
        fps = scene.render.fps
        f = 20 / fps

        if obj.animation_data is None:
            obj.animation_data_create()

        original_action = obj.animation_data.action

        action = None
        bone_name = None
        fcurve = None
        touched_fcurves = []

        with open(filepath, "r", encoding="utf8") as fh:
            for line in fh:
                line = line.rstrip('\n')

                if not line or line.startswith('#'):
                    continue

                if line.startswith('an '):
                    name = line[3:]
                    action = bpy.data.actions.get(name)

                    if action is None:
                        action = bpy.data.actions.new(name)

                    action.use_fake_user = True
                    obj.animation_data.action = action
                    bone_name = None
                    fcurve = None

                elif line.startswith('ao '):
                    bone_name = line[3:]
                    fcurve = None

                elif line.startswith('ag '):
                    fcurve = None

                    if action is None or bone_name is None:
                        continue

                    parts = line.split()
                    prop = DATA_PATHS.get(parts[1])

                    if prop is None:
                        continue

                    index = int(parts[2])
                    data_path = 'pose.bones["%s"].%s' % (bone_name, prop)
                    fcurve = ensure_fcurve(action, obj, data_path, index, bone_name)
                    fcurve.keyframe_points.clear()
                    touched_fcurves.append(fcurve)

                elif line.startswith('kf '):
                    if fcurve is None:
                        continue

                    parts = line.split()
                    frame = float(parts[1]) / f
                    value = float(parts[2])
                    interp = parts[3]
                    handle_left = (float(parts[4]) / f, float(parts[5]))
                    handle_right = (float(parts[6]) / f, float(parts[7]))

                    keyframe = fcurve.keyframe_points.insert(frame, value, options={'FAST'})
                    keyframe.interpolation = interp
                    keyframe.handle_left_type = 'FREE'
                    keyframe.handle_right_type = 'FREE'
                    keyframe.handle_left = handle_left
                    keyframe.handle_right = handle_right

        for fc in touched_fcurves:
            fc.keyframe_points.sort()
            fc.update()

        obj.animation_data.action = original_action

        subprogress1.step("Finished importing keyframes")

    return {'FINISHED'}, None
