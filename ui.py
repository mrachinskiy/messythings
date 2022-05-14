# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2017-2022 Mikhail Rachinskiy

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

        col = layout.column()
        col.label(text="Tweak")
        col.operator("scene.messythings_normalize", icon="SHADING_WIRE")

        layout.separator()

        col = layout.column()
        col.label(text="Sort")
        col.operator("scene.messythings_sort", text="By Collections", icon="OUTLINER")
        col.operator("scene.messythings_deps_select", icon="LINKED")

        layout.separator()

        col = layout.column()
        col.label(text="Clean Up")
        col.operator("scene.messythings_scene_cleanup", text="Scene", icon="SCENE_DATA")
        col.operator("object.messythings_obdata_del", text="Object Data", icon="MESH_DATA")
