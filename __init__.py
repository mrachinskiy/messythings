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
    "version": (1, 4, 0),
    "blender": (2, 93, 0),
    "location": "Properties > Scene",
    "description": "Deal with badly organized projects.",
    "doc_url": "https://github.com/mrachinskiy/messythings#readme",
    "tracker_url": "https://github.com/mrachinskiy/messythings/issues",
    "category": "Scene",
}


if "bpy" in locals():
    import os
    from typing import Dict
    from types import ModuleType


    def reload_recursive(path: str, mods: Dict[str, ModuleType]) -> None:
        import importlib

        for entry in os.scandir(path):

            if entry.is_file() and entry.name.endswith(".py") and not entry.name.startswith("__"):
                filename, _ = os.path.splitext(entry.name)

                if filename in mods:
                    importlib.reload(mods[filename])

            elif entry.is_dir() and not entry.name.startswith((".", "__")):

                if entry.name in mods:
                    importlib.reload(mods[entry.name])
                    reload_recursive(entry.path, mods[entry.name].__dict__)
                    continue

                reload_recursive(entry.path, mods)


    reload_recursive(os.path.dirname(__file__), locals())
else:
    import bpy

    from . import (
        ops_cleanup,
        ops_sort,
        ops_tweak,
        ui,
    )


classes = (
    ui.VIEW3D_PT_messythings,
    ops_cleanup.OBJECT_OT_messythings_obdata_del,
    ops_cleanup.SCENE_OT_messythings_scene_cleanup,
    ops_sort.SCENE_OT_messythings_deps_select,
    ops_sort.SCENE_OT_messythings_sort,
    ops_tweak.SCENE_OT_messythings_normalize,
    ops_tweak.SCENE_OT_messythings_profile_render,
)


def register():
    if bl_info["blender"] > bpy.app.version:
        addon_name = bl_info["name"].upper()
        addon_ver = ".".join(str(x) for x in bl_info["version"])
        blender_ver = ".".join(str(x) for x in bl_info["blender"][:2])
        requirements_check = RuntimeError(
            f"\n!!! BLENDER {blender_ver} IS REQUIRED FOR {addon_name} {addon_ver} !!!"
            "\n!!! READ INSTALLATION GUIDE !!!"
        )
        raise requirements_check

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
