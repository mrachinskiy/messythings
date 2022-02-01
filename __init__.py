# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Messy Things project organizer for Blender.
#  Copyright (C) 2017-2022  Mikhail Rachinskiy
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
    from pathlib import Path
    _essential.reload_recursive(Path(__file__).parent, locals())
else:
    from . import _essential
    _essential.check(bl_info["blender"])

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
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
