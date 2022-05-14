# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2017-2022 Mikhail Rachinskiy

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
    ui.VIEW3D_MT_messythings,
    ops_cleanup.OBJECT_OT_messythings_obdata_del,
    ops_cleanup.SCENE_OT_messythings_scene_cleanup,
    ops_sort.SCENE_OT_messythings_deps_select,
    ops_sort.SCENE_OT_messythings_sort,
    ops_tweak.SCENE_OT_messythings_normalize,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Menu
    # ---------------------------

    bpy.types.TOPBAR_MT_file.append(ui.draw_messythings_menu)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # Menu
    # ---------------------------

    bpy.types.TOPBAR_MT_file.remove(ui.draw_messythings_menu)


if __name__ == "__main__":
    register()
