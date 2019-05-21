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
    "version": (1, 2, 1),
    "blender": (2, 80, 0),
    "location": "Properties > Scene",
    "description": "Deal with badly organized projects.",
    "wiki_url": "https://github.com/mrachinskiy/messythings#readme",
    "tracker_url": "https://github.com/mrachinskiy/messythings/issues",
    "category": "Scene",
}


if "bpy" in locals():
    import os

    addon_dir = os.path.dirname(__file__)

    def walk(path, parent_dir=None):
        import importlib

        for entry in os.scandir(path):

            if entry.is_file() and entry.name.endswith(".py"):
                filename, _ = os.path.splitext(entry.name)
                is_init = filename == "__init__"

                if parent_dir:
                    module = parent_dir if is_init else f"{parent_dir}.{filename}"
                else:
                    if is_init:
                        continue
                    module = filename

                importlib.reload(eval(module))

            elif entry.is_dir() and not entry.name.startswith((".", "__")):
                dirname = f"{parent_dir}.{entry.name}" if parent_dir else entry.name
                walk(entry.path, parent_dir=dirname)

    walk(addon_dir)
else:
    import bpy

    from . import (
        op_cleanup,
        ops_sort,
        ops_tweak,
        ui,
    )


classes = (
    ui.VIEW3D_PT_messythings,
    op_cleanup.SCENE_OT_messythings_cleanup,
    ops_sort.SCENE_OT_messythings_deps_select,
    ops_sort.SCENE_OT_messythings_sort,
    ops_tweak.SCENE_OT_messythings_normalize,
    ops_tweak.SCENE_OT_messythings_profile_render,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
