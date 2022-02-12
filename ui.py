# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2017-2022 Mikhail Rachinskiy

from bpy.types import Panel


class VIEW3D_PT_messythings(Panel):
    bl_label = "Messy Things"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        flow = layout.grid_flow()

        col = flow.column()
        col.label(text="Tweak")
        col.operator("scene.messythings_normalize", icon="SHADING_WIRE")
        col.operator("scene.messythings_profile_render", text="Render Profile", icon="OUTPUT")

        col = flow.column()
        col.label(text="Sort")
        col.operator("scene.messythings_sort", text="Collections", icon="OUTLINER")
        col.operator("scene.messythings_deps_select", text="Dependencies", icon="LINKED")

        col = flow.column()
        col.label(text="Clean Up")
        col.operator("scene.messythings_scene_cleanup", text="Scene", icon="SCENE_DATA")
        col.operator("object.messythings_obdata_del", text="Object Data", icon="MESH_DATA")
