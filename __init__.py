# SPDX-FileCopyrightText: 2020-2026 McHorse
#
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ExportHelper, path_reference_mode

# Export panel
class ExportOBJ(bpy.types.Operator, ExportHelper):
    # Panel's information
    bl_idname = "export_scene.bobj_keyframes"
    bl_label = 'Export BOBJ keyframes'
    bl_options = {'PRESET'}

    # Panel's properties
    filename_ext = ".bobj"
    filter_glob: StringProperty(default="*.bobj", options={'HIDDEN'})
    path_mode: path_reference_mode
    check_extension = True

    def execute(self, context):
        from . import export_bobj
        from mathutils import Matrix

        keywords = self.as_keywords(ignore=("axis_forward", "axis_up", "check_existing", "filter_glob", "path_mode"))

        return export_bobj.save(context, **keywords)

# Register and stuff
def menu_func_export(self, context):
    self.layout.operator(ExportOBJ.bl_idname, text="BOBJ keyframes (.bobj)")

classes = (
    ExportOBJ,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
