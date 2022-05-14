# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2017-2022 Mikhail Rachinskiy

from bpy.types import Operator
from bpy.props import EnumProperty, BoolProperty


class SCENE_OT_messythings_normalize(Operator):
    bl_label = "Normalize Objects"
    bl_description = "Normalize object properties"
    bl_idname = "scene.messythings_normalize"
    bl_options = {"REGISTER", "UNDO"}

    object_scope: EnumProperty(
        name="Objects",
        items=(
            ("SCENE", "All", ""),
            ("SELECTED", "Selected", ""),
        ),
    )
    use_mod_match_render: BoolProperty(
        name="Render Properties",
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

        layout.prop(self, "object_scope", expand=True)

        col = layout.column(heading="Modifiers")
        col.prop(self, "use_mod_match_render")

        col = layout.column(heading="Object Data")
        col.prop(self, "use_data_rename")

    def execute(self, context):
        if not (self.use_data_rename or self.use_mod_match_render):
            return {"FINISHED"}

        if self.object_scope == "SCENE":
            obs = context.scene.objects
            if not obs:
                self.report({"ERROR"}, "No objects in the scene")
                return {"CANCELLED"}
        else:
            obs = context.selected_objects
            if not obs:
                self.report({"ERROR"}, "Missing selected objects")
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

        if mod_count:
            msgs.append(f"{mod_count} Modifiers")
        if rename_count:
            msgs.append(f"{rename_count} Renamed")

        if not msgs:
            return {"CANCELLED"}

        msg = ", ".join(msgs)
        self.report({"INFO"}, msg)

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
