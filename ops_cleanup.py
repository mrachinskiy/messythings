# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2017-2022 Mikhail Rachinskiy

from bpy.types import Operator
from bpy.props import BoolProperty


class OBJECT_OT_messythings_obdata_del(Operator):
    bl_label = "Remove Object Data"
    bl_description = "Remove object data for selected objects"
    bl_idname = "object.messythings_obdata_del"
    bl_options = {"REGISTER", "UNDO"}

    use_del_vertex_groups: BoolProperty(name="Vertex Groups")
    use_del_vertex_colors: BoolProperty(name="Vertex Colors")
    use_del_uv: BoolProperty(name="UVs")
    use_del_crease: BoolProperty(name="Edge Crease")
    use_del_bevel: BoolProperty(name="Edge & Vert Bevel")

    def execute(self, context):
        vg_del_count = 0
        vc_del_count = 0
        uv_del_count = 0
        crease_del_count = 0
        bevel_del_count = 0
        msgs = []

        for ob in context.selected_objects:
            if ob.data:
                ob_data = ob.data
                is_mesh = ob.type == "MESH"

                if self.use_del_vertex_groups and ob.vertex_groups:
                    ob.vertex_groups.clear()
                    vg_del_count += 1

                if self.use_del_vertex_colors and is_mesh and ob_data.vertex_colors:
                    for vc in ob_data.vertex_colors:
                        ob_data.vertex_colors.remove(vc)
                    vc_del_count += 1

                if self.use_del_uv and is_mesh and ob_data.uv_layers:
                    for uv in ob_data.uv_layers:
                        ob_data.uv_layers.remove(uv)
                    uv_del_count += 1

                if self.use_del_crease and is_mesh and ob_data.use_customdata_edge_crease:
                    ob_data.use_customdata_edge_crease = False
                    crease_del_count += 1

                if self.use_del_bevel and is_mesh and (ob_data.use_customdata_edge_bevel or ob_data.use_customdata_vertex_bevel):
                    ob_data.use_customdata_edge_bevel = False
                    ob_data.use_customdata_vertex_bevel = False
                    bevel_del_count += 1

        if self.use_del_vertex_groups:
            msgs.append(f"{vg_del_count} Vertex Groups")
        if self.use_del_vertex_colors:
            msgs.append(f"{vc_del_count} Vertex Colors")
        if self.use_del_uv:
            msgs.append(f"{uv_del_count} UVs")
        if self.use_del_crease:
            msgs.append(f"{crease_del_count} Crease")
        if self.use_del_bevel:
            msgs.append(f"{bevel_del_count} Bevel")

        msg = "Removed: " + ", ".join(msgs)
        self.report({"INFO"}, msg)

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.selected_objects:
            self.report({"ERROR"}, "Missing selected objects")
            return {"CANCELLED"}

        wm = context.window_manager
        return wm.invoke_props_dialog(self)


class SCENE_OT_messythings_scene_cleanup(Operator):
    bl_label = "Scene Clean Up"
    bl_description = "Remove redundant or purge all datablocks of set type"
    bl_idname = "scene.messythings_scene_cleanup"
    bl_options = {"REGISTER", "UNDO"}

    use_cleanup_objects: BoolProperty(
        name="Objects",
        description=(
            "Remove lattice, curve and empty mesh objects that are not in use by "
            "modifiers, constraints, curve Bevel Object and Taper Object properties"
        ),
        default=True,
    )
    use_cleanup_modifiers: BoolProperty(
        name="Modifiers",
        description="Remove Curve, Lattice, Boolean and Shrinkwrap modifiers with empty Object or Target fields",
        default=True,
    )
    use_purge_materials: BoolProperty(
        name="Materials",
        description="Purge all materials from file, additionally remove material slots from objects",
    )
    use_purge_gpencil: BoolProperty(
        name="Annotations",
        description="Purge all annotations from file"
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(heading="Redundant", align=True)
        col.prop(self, "use_cleanup_objects")
        col.prop(self, "use_cleanup_modifiers")

        col = layout.column(heading="Purge", align=True)
        col.prop(self, "use_purge_materials")
        col.prop(self, "use_purge_gpencil")

    def execute(self, context):
        from . import lib

        msgs = []

        if self.use_cleanup_objects:
            curve, lat, mesh = lib.cleanup_objects()
            msgs.append(f"{curve} curve")
            msgs.append(f"{lat} lattice")
            msgs.append(f"{mesh} mesh")

        if self.use_cleanup_modifiers:
            mod = lib.cleanup_modifiers()
            msgs.append(f"{mod} modifiers")

        if self.use_purge_materials:
            mat = lib.purge_materials()
            msgs.append(f"{mat} materials")

        if self.use_purge_gpencil:
            gp = lib.purge_gpencil()
            msgs.append(f"{gp} annotations")

        if not msgs:
            return {"CANCELLED"}

        msg = "Removed: " + ", ".join(msgs)
        self.report({"INFO"}, msg)

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
