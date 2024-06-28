# SPDX-FileCopyrightText: 2017-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.props import BoolProperty
from bpy.types import Object, Operator


def _get_objects() -> list[Object]:
    if bpy.context.area.type == "OUTLINER":

        if bpy.context.selected_ids:

            for id in bpy.context.selected_ids:
                if id.id_type == "COLLECTION":
                    return bpy.context.collection.all_objects

            return bpy.context.selected_objects

    else:
        if bpy.context.selected_objects:
            return bpy.context.selected_objects

    return bpy.context.scene.objects


class SCENE_OT_messythings_normalize(Operator):
    bl_label = "Normalize Objects"
    bl_description = "Normalize object properties"
    bl_idname = "scene.messythings_normalize"
    bl_options = {"REGISTER", "UNDO"}

    use_mod_match_render: BoolProperty(
        name="Match Render to Viewport",
        description="Match render to viewport properties",
        default=True,
    )
    use_data_rename: BoolProperty(
        name="Rename After Object",
        description="Rename object data after object",
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(heading="Modifiers")
        col.prop(self, "use_mod_match_render")

        col = layout.column(heading="Object Data")
        col.prop(self, "use_data_rename")

    def execute(self, context):
        if not (self.use_data_rename or self.use_mod_match_render):
            return {"FINISHED"}

        obs = _get_objects()

        if not obs:
            self.report({"ERROR"}, "Objects not found")
            return {"CANCELLED"}

        mod_count = 0
        rename_count = 0
        ob_datas = set()

        for ob in obs:

            if self.use_mod_match_render and ob.modifiers:
                for mod in ob.modifiers:
                    if mod.type == "SCREW" and mod.render_steps != mod.steps:
                        mod.render_steps = mod.steps
                        mod_count += 1
                    if mod.type == "SUBSURF" and mod.render_levels != mod.levels:
                        mod.render_levels = mod.levels
                        mod_count += 1

            if self.use_data_rename and ob.data and (ob.data not in ob_datas) and (ob.data.name != ob.name):
                ob.data.name = ob.name
                ob_datas.add(ob.data)
                rename_count += 1

        msgs = []

        if self.use_mod_match_render:
            msgs.append(f"{mod_count} Modifiers")
        if self.use_data_rename:
            msgs.append(f"{rename_count} Renamed")

        self.report({"INFO"}, ", ".join(msgs))

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
