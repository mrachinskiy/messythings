# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
#  Copyright (C) 2017-2018  Mikhail Rachinskiy
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
    "version": (1, 0, 0),
    "blender": (2, 79, 0),
    "location": "3D View > Tool Shelf > Tools",
    "description": "Deal with badly organized projects.",
    "wiki_url": "https://github.com/mrachinskiy/messythings#readme",
    "tracker_url": "https://github.com/mrachinskiy/messythings/issues",
    "category": "Scene",
}


if "bpy" in locals():
    import importlib

    importlib.reload(ops_cleanup)
    importlib.reload(ops_layer)
    importlib.reload(ops_object)
    importlib.reload(ops_scene)
    importlib.reload(ui)
else:
    import bpy

    from . import ops_cleanup, ops_layer, ops_object, ops_scene, ui


classes = (
    ui.VIEW3D_PT_messythings,
    ops_cleanup.OBJECT_OT_messythings_cleanup_modifiers,
    ops_cleanup.OBJECT_OT_messythings_cleanup_objects,
    ops_cleanup.SCENE_OT_messythings_cleanup_grease_pencil,
    ops_cleanup.SCENE_OT_messythings_cleanup_materials,
    ops_layer.OBJECT_OT_messythings_get_misplaced_dependencies,
    ops_layer.OBJECT_OT_messythings_sort_by_layers,
    ops_object.OBJECT_OT_messythings_normalize_display,
    ops_scene.SCENE_OT_messythings_apply_render_profile,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
