# SPDX-FileCopyrightText: 2017-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later


if "bpy" in locals():
    from pathlib import Path

    from . import essentials

    essentials.reload_recursive(Path(__file__).parent, locals())
else:
    import bpy

    from . import operators, ui


classes = essentials.get_classes((operators, ui))


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
