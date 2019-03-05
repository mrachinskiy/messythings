# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Messy Things project organizer for Blender.
#  Copyright (C) 2017-2019  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "Messy Things",
    "author": "Mikhail Rachinskiy",
    "version": (1, 2, 0),
    "blender": (2, 80, 0),
    "location": "Properties > Scene",
    "description": "Deal with badly organized projects.",
    "wiki_url": "https://github.com/mrachinskiy/messythings#readme",
    "tracker_url": "https://github.com/mrachinskiy/messythings/issues",
    "category": "Scene",
}


if "bpy" in locals():
    import os
    import importlib

    for entry in os.scandir(os.path.dirname(__file__)):

        if entry.is_file() and entry.name.endswith(".py") and not entry.name.startswith("__"):
            module = os.path.splitext(entry.name)[0]
            importlib.reload(eval(module))

        elif entry.is_dir() and not entry.name.startswith((".", "__")):
            for subentry in os.scandir(entry.path):
                if subentry.is_file() and subentry.name.endswith(".py"):
                    module = entry.name + "." + os.path.splitext(subentry.name)[0]
                    importlib.reload(eval(module))
else:
    import bpy

    from . import (
        ops_tweak,
        ops_sort,
        ui,
    )
    from .op_cleanup import cleanup_op


classes = (
    ui.VIEW3D_PT_messythings,
    # ui.VIEW3D_PT_messythings_tweak,
    # ui.VIEW3D_PT_messythings_sort,
    # ui.VIEW3D_PT_messythings_cleanup,
    cleanup_op.SCENE_OT_messythings_cleanup,
    ops_tweak.SCENE_OT_messythings_normalize,
    ops_tweak.SCENE_OT_messythings_profile_render,
    ops_sort.SCENE_OT_messythings_deps_select,
    ops_sort.SCENE_OT_messythings_sort,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
