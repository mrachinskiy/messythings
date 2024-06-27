# SPDX-FileCopyrightText: 2017-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Menu


def draw_messythings_menu(self, context):
    layout: bpy.types.UILayout = self.layout
    layout.separator()
    layout.menu("VIEW3D_MT_messythings", icon="FORCE_TURBULENCE")


class VIEW3D_MT_messythings(Menu):
    bl_label = "Messy Things"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = "INVOKE_DEFAULT"

        layout.operator("scene.messythings_normalize")

        layout.separator()

        col = layout.column()
        col.operator("scene.messythings_sort")
        col.operator("scene.messythings_deps_select")

        layout.separator()

        col = layout.column()
        col.operator("scene.messythings_scene_cleanup")
        col.operator("object.messythings_obdata_del")
