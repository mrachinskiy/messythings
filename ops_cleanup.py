# SPDX-FileCopyrightText: 2017-2024 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import Operator, AttributeGroup
from bpy.props import BoolProperty


def _attr_del(attributes: AttributeGroup, attr_names: tuple[str]) -> int:
    i = 0
    for name in attr_names:
        if (attr := attributes.get(name)) is not None:
            attributes.remove(attr)
            i = 1
    return i


class OBJECT_OT_messythings_obdata_del(Operator):
    bl_label = "Remove Object Data"
    bl_description = "Remove object data for selected mesh objects"
    bl_idname = "object.messythings_obdata_del"
    bl_options = {"REGISTER", "UNDO"}

    use_del_vertex_groups: BoolProperty(name="Vertex Groups")
    use_del_shape_keys: BoolProperty(name="Shape Keys")
    use_del_uv: BoolProperty(name="UVs")
    use_del_vertex_colors: BoolProperty(name="Vertex Colors")
    use_del_mask: BoolProperty(name="Sculpt Mask")
    use_del_skin: BoolProperty(name="Skin Data")
    use_del_normals: BoolProperty(name="Custom Normals")
    use_del_bevel: BoolProperty(name="Bevel")
    use_del_crease: BoolProperty(name="Crease")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.prop(self, "use_del_vertex_groups")
        col.prop(self, "use_del_shape_keys")

        col = layout.column(heading="Attributes", align=True)
        col.prop(self, "use_del_uv")
        col.prop(self, "use_del_vertex_colors")
        col.prop(self, "use_del_bevel")
        col.prop(self, "use_del_crease")

        col = layout.column(heading="Geometry", align=True)
        col.prop(self, "use_del_mask")
        col.prop(self, "use_del_skin")
        col.prop(self, "use_del_normals")

    def execute(self, context):
        obs = context.selected_objects

        vg_del_count = 0
        sk_del_count = 0
        uv_del_count = 0
        vc_del_count = 0
        bevel_del_count = 0
        crease_del_count = 0
        mask_del_count = 0
        skin_del_count = 0
        normals_del_count = 0

        for ob in obs:
            if ob.type != "MESH":
                continue

            # Object

            if self.use_del_vertex_groups and ob.vertex_groups:
                ob.vertex_groups.clear()
                vg_del_count += 1

            # Data

            ob_data = ob.data

            if self.use_del_shape_keys and ob_data.shape_keys:
                ob.shape_key_clear()
                sk_del_count += 1

            # Attributes

            if self.use_del_uv and ob_data.uv_layers:
                for uv in ob_data.uv_layers:
                    ob_data.uv_layers.remove(uv)
                uv_del_count += 1

            if self.use_del_vertex_colors and ob_data.color_attributes:
                for vc in ob_data.color_attributes:
                    ob_data.color_attributes.remove(vc)
                vc_del_count += 1

            if self.use_del_bevel:
                bevel_del_count += _attr_del(ob_data.attributes, ("bevel_weight_edge", "bevel_weight_vert"))

            if self.use_del_crease:
                crease_del_count += _attr_del(ob_data.attributes, ("crease_edge", "crease_vert"))

            # Geometry

            with context.temp_override(object=ob):

                if self.use_del_mask and bpy.ops.mesh.customdata_mask_clear.poll():
                    bpy.ops.mesh.customdata_mask_clear()
                    mask_del_count += 1

                if self.use_del_skin and ob_data.skin_vertices:
                    bpy.ops.mesh.customdata_skin_clear()
                    skin_del_count += 1

                if self.use_del_normals and ob_data.has_custom_normals:
                    bpy.ops.mesh.customdata_custom_splitnormals_clear()
                    normals_del_count += 1

        msgs = []

        if vg_del_count:
            msgs.append(f"{vg_del_count} Vertex Groups")
        if sk_del_count:
            msgs.append(f"{sk_del_count} Shape Keys")
        if uv_del_count:
            msgs.append(f"{uv_del_count} UVs")
        if vc_del_count:
            msgs.append(f"{vc_del_count} Vertex Colors")
        if bevel_del_count:
            msgs.append(f"{bevel_del_count} Bevel")
        if crease_del_count:
            msgs.append(f"{crease_del_count} Crease")
        if mask_del_count:
            msgs.append(f"{mask_del_count} Mask")
        if skin_del_count:
            msgs.append(f"{skin_del_count} Skin")
        if normals_del_count:
            msgs.append(f"{normals_del_count} Normals")

        if not msgs:
            self.report({"INFO"}, "Found nothing to clean up")
            return {"CANCELLED"}

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
    bl_label = "Clean Up Scene"
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
            if curve:
                msgs.append(f"{curve} curve")
            if lat:
                msgs.append(f"{lat} lattice")
            if mesh:
                msgs.append(f"{mesh} mesh")

        if self.use_cleanup_modifiers:
            mod = lib.cleanup_modifiers()
            if mod:
                msgs.append(f"{mod} modifiers")

        if self.use_purge_materials:
            mat = lib.purge_materials()
            if mat:
                msgs.append(f"{mat} materials")

        if self.use_purge_gpencil:
            gp = lib.purge_gpencil()
            if gp:
                msgs.append(f"{gp} annotations")

        if not msgs:
            return {"CANCELLED"}

        msg = "Removed: " + ", ".join(msgs)
        self.report({"INFO"}, msg)

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
