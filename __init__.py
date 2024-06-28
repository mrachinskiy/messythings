# SPDX-FileCopyrightText: 2017-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later


if "bpy" in locals():
    from pathlib import Path
    _essential.reload_recursive(Path(__file__).parent, locals())
else:
    import tomllib
    from pathlib import Path

    from . import _essential

    with open(Path(__file__).parent / "blender_manifest.toml", "rb") as f:
        _essential.check(tomllib.load(f)["blender_version_min"])

    import bpy

    from . import ops_cleanup, ops_sort, ops_tweak, ui


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

    bpy.types.VIEW3D_MT_object_context_menu.append(ui.draw_messythings_menu)
    bpy.types.OUTLINER_MT_collection.append(ui.draw_messythings_menu)
    bpy.types.OUTLINER_MT_object.append(ui.draw_messythings_menu)
    bpy.types.OUTLINER_MT_context_menu.append(ui.draw_messythings_menu)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    # Menu
    # ---------------------------

    bpy.types.VIEW3D_MT_object_context_menu.remove(ui.draw_messythings_menu)
    bpy.types.OUTLINER_MT_collection.remove(ui.draw_messythings_menu)
    bpy.types.OUTLINER_MT_object.remove(ui.draw_messythings_menu)
    bpy.types.OUTLINER_MT_context_menu.remove(ui.draw_messythings_menu)


if __name__ == "__main__":
    register()
