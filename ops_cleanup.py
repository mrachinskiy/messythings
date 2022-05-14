# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2017-2022 Mikhail Rachinskiy

import bpy
from bpy.types import Operator
from bpy.props import BoolProperty


def _try(obj: object, name: str, value=None) -> bool:
    if getattr(obj, name, False):
        if value is not None:
            setattr(obj, name, value)
        return True
    return False


class OBJECT_OT_messythings_obdata_del(Operator):
    bl_label = "Remove Object Data"
    bl_description = "Remove object data for selected mesh objects"
    bl_idname = "object.messythings_obdata_del"
    bl_options = {"REGISTER", "UNDO"}

    use_del_vertex_groups: BoolProperty(name="Vertex Groups")
    use_del_face_maps: BoolProperty(name="Face Maps")
    use_del_shape_keys: BoolProperty(name="Shape Keys")
    use_del_uv: BoolProperty(name="UVs")
    use_del_vertex_colors: BoolProperty(name="Vertex Colors")
    use_del_attributes: BoolProperty(name="Attributes")
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
        col.prop(self, "use_del_face_maps")
        col.prop(self, "use_del_shape_keys")
        col.prop(self, "use_del_uv")
        col.prop(self, "use_del_vertex_colors")
        col.prop(self, "use_del_attributes")

        col = layout.column(heading="Geometry", align=True)
        col.prop(self, "use_del_mask")
        col.prop(self, "use_del_skin")
        col.prop(self, "use_del_normals")
        col.prop(self, "use_del_bevel")
        col.prop(self, "use_del_crease")

    def execute(self, context):
        vg_del_count = 0
        fm_del_count = 0
        sk_del_count = 0
        vc_del_count = 0
        attr_del_count = 0
        uv_del_count = 0
        mask_del_count = 0
        skin_del_count = 0
        normals_del_count = 0
        bevel_del_count = 0
        crease_del_count = 0

        for ob in context.selected_objects:
            if ob.type != "MESH":
                continue


            if self.use_del_vertex_groups and ob.vertex_groups:
                ob.vertex_groups.clear()
                vg_del_count += 1

            if self.use_del_face_maps and ob.face_maps:
                ob.face_maps.clear()
                fm_del_count += 1

            ob_data = ob.data

            if self.use_del_shape_keys and ob_data.shape_keys:
                ob.shape_key_clear()
                sk_del_count += 1

            if self.use_del_uv and ob_data.uv_layers:
                for uv in ob_data.uv_layers:
                    ob_data.uv_layers.remove(uv)
                uv_del_count += 1

            if self.use_del_vertex_colors and ob_data.vertex_colors:
                for vc in ob_data.vertex_colors:
                    ob_data.vertex_colors.remove(vc)
                vc_del_count += 1

            if self.use_del_attributes and ob_data.attributes:
                for attr in ob_data.attributes:
                    ob_data.attributes.remove(attr)
                attr_del_count += 1

            # Geometry

            override = {"object": ob}

            if self.use_del_mask and bpy.ops.mesh.customdata_mask_clear.poll(override):
                bpy.ops.mesh.customdata_mask_clear(override)
                mask_del_count += 1

            if self.use_del_skin and ob_data.skin_vertices:
                bpy.ops.mesh.customdata_skin_clear(override)
                skin_del_count += 1

            if self.use_del_normals and ob_data.has_custom_normals:
                bpy.ops.mesh.customdata_custom_splitnormals_clear(override)
                normals_del_count += 1

            if self.use_del_bevel and (ob_data.use_customdata_edge_bevel or ob_data.use_customdata_vertex_bevel):
                ob_data.use_customdata_edge_bevel = False
                ob_data.use_customdata_vertex_bevel = False
                bevel_del_count += 1

            if self.use_del_crease and (ob_data.use_customdata_edge_crease or _try(ob_data, "use_customdata_vertex_crease")):
                ob_data.use_customdata_edge_crease = False
                _try(ob_data, "use_customdata_vertex_crease", False)
                crease_del_count += 1

        msgs = []

        if vg_del_count:
            msgs.append(f"{vg_del_count} Vertex Groups")
        if sk_del_count:
            msgs.append(f"{sk_del_count} Shape Keys")
        if fm_del_count:
            msgs.append(f"{fm_del_count} Face Maps")
        if uv_del_count:
            msgs.append(f"{uv_del_count} UVs")
        if vc_del_count:
            msgs.append(f"{vc_del_count} Vertex Colors")
        if attr_del_count:
            msgs.append(f"{attr_del_count} Attributes")
        if mask_del_count:
            msgs.append(f"{mask_del_count} Mask")
        if skin_del_count:
            msgs.append(f"{skin_del_count} Skin")
        if normals_del_count:
            msgs.append(f"{normals_del_count} Normals")
        if bevel_del_count:
            msgs.append(f"{bevel_del_count} Bevel")
        if crease_del_count:
            msgs.append(f"{crease_del_count} Crease")

        if not msgs:
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
