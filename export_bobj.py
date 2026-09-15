# SPDX-FileCopyrightText: 2020-2026 McHorse
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import bpy
from bpy_extras.wm_utils.progress_report import ProgressReport, ProgressReportSubstep

# Remove spaces from given string (so it would be spaceless)
def name_compat(name):
    return 'None' if name is None else name.replace(' ', '_')

# Yield all fcurves of an action, regardless of whether it uses the legacy
# flat fcurve list or the layered layers/strips/channelbags data model
def iter_action_fcurves(action):
    if hasattr(action, 'fcurves'):
        yield from action.fcurves
        return

    for layer in action.layers:
        for strip in layer.strips:
            if strip.type != 'KEYFRAME':
                continue

            for channelbag in strip.channelbags:
                yield from channelbag.fcurves

# Writes all action keyframes
def write_actions(context, fw, filepath):
    fw('# Animation data\n')

    # Collect the bone fcurve groups for every action, skipping ones with nothing to export
    entries = []

    for key, action in bpy.data.actions.items():
        groups = collect_action_groups(action)

        if groups:
            entries.append([key, groups])

    # When exactly one action is being exported, name it after the output
    # file instead of Blender's (often generic, e.g. "ArmatureAction") name,
    # matching the emote name the file is saved under
    if len(entries) == 1:
        entries[0][0] = os.path.splitext(os.path.basename(filepath))[0]

    for name, groups in entries:
        write_action(context, fw, name, groups)

# Collect an action's bone fcurve groups, keyed by bone name
def collect_action_groups(action):
    groups = {}

    def getOrCreate(key):
        if key in groups:
            return groups[key]

        l = []
        groups[key] = l

        return l

    # Collect groups
    for fc in iter_action_fcurves(action):
        if fc.data_path.startswith('pose.bones["'):
            key = fc.data_path[12:]
            key = key[:key.index('"')]

            getOrCreate(key).append(fc)

    return groups

# Write an action
def write_action(context, fw, name, groups):
    fw('an %s\n' % name)

    for key, group in groups.items():
        fw('ao %s\n' % name_compat(key))
        
        for fcurve in group:
            data_path = fcurve.data_path
            index = fcurve.array_index
            length = len(fcurve.keyframe_points)
            dvalue = 0
        
            if data_path.endswith('location'):
                data_path = 'location'
            elif data_path.endswith('rotation_euler'):
                data_path = 'rotation'
            elif data_path.endswith('scale'):
                data_path = 'scale'
                dvalue = 1
            else:
                continue
            
            if length <= 0:
                continue

            all_default = True

            # Prevent writing actions which fully consist out of default values
            for keyframe in fcurve.keyframe_points:
                if keyframe.co[1] != dvalue:
                    all_default = False

                    break;

            if all_default: 
                continue

            # Write the action group
            fw('ag %s %d\n' % (data_path, index))
        
            last_frame = None
        
            for keyframe in fcurve.keyframe_points:
                # Avoid inserting keyframes with duplicate X value
                if last_frame == keyframe.co[0]:
                    continue
            
                fw(stringify_keyframe(context, keyframe) + '\n')
                last_frame = keyframe.co[0]

# Stringify a keyframe
def stringify_keyframe(context, keyframe):
    fps = context.scene.render.fps
    f = 20 / fps

    interp = keyframe.interpolation
    # round the frame to a whole number because minecraft seems to sometimes just have a heart attack and die
    result = 'kf %d %f %s' % (round(float(keyframe.co[0]) * float(f)), keyframe.co[1], interp)
    result += ' %f %f %f %f' % (keyframe.handle_left[0] * f, keyframe.handle_left[1], keyframe.handle_right[0] * f, keyframe.handle_right[1])
    
    return result

def save(context, filepath):
    with ProgressReport(context.window_manager) as progress:
        scene = context.scene

        progress.enter_substeps(1)
        write_file(context, filepath, scene, progress)
        progress.leave_substeps()

    return {'FINISHED'}

def write_file(context, filepath, scene, progress=ProgressReport()):
    with ProgressReportSubstep(progress, 2, "BOBJ Export path: %r" % filepath, "BOBJ Export Finished") as subprogress1:
        with open(filepath, "w", encoding="utf8", newline="\n") as f:
            fw = f.write

            # Write Header
            fw('# Blender v%s BOBJ keyframes: %r\n' % (bpy.app.version_string, os.path.basename(bpy.data.filepath)))

            # Write keyframes to the file
            write_actions(context, fw, filepath)
            
        subprogress1.step("Finished exporting keyframes")