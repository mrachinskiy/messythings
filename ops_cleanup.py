# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Messy Things project organizer for Blender.
#  Copyright (C) 2017-2019  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


import bpy
from bpy.types import Operator
from bpy.props import BoolProperty


class OBJECT_OT_messythings_obdata_del(Operator):
    bl_label = "Messy Things Remove Object Data"
    bl_description = "Remove object data for selected objects"
    bl_idname = "object.messythings_obdata_del"
    bl_options = {"REGISTER", "UNDO"}

    use_del_vertex_groups: BoolProperty(name="Vertex Groups")
    use_del_vertex_colors: BoolProperty(name="Vertex Colors")
    use_del_uv: BoolProperty(name="UVs")
    use_del_crease: BoolProperty(name="Edge Crease")
    use_del_bevel: BoolProperty(name="Edge & Vert Bevel")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        layout.prop(self, "use_del_vertex_groups")
        layout.prop(self, "use_del_vertex_colors")
        layout.prop(self, "use_del_uv")
        layout.prop(self, "use_del_crease")
        layout.prop(self, "use_del_bevel")

        layout.separator()

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
    bl_label = "Messy Things Cleanup"
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

        layout.separator()

        col = layout.column(align=True)
        col.prop(self, "use_cleanup_objects")
        col.prop(self, "use_cleanup_modifiers")

        col = layout.column(align=True)
        col.label(text="Purge", icon="ERROR")
        col.prop(self, "use_purge_materials")
        col.prop(self, "use_purge_gpencil")

        layout.separator()

    def execute(self, context):
        msgs = []

        if self.use_cleanup_objects:
            curve, lat, mesh = self.cleanup_objects(context)
            msgs.append(f"{curve} curve")
            msgs.append(f"{lat} lattice")
            msgs.append(f"{mesh} mesh")

        if self.use_cleanup_modifiers:
            mod = self.cleanup_modifiers(context)
            msgs.append(f"{mod} modifiers")

        if self.use_purge_materials:
            mat = self.purge_materials(context)
            msgs.append(f"{mat} materials")

        if self.use_purge_gpencil:
            gp = self.purge_gpencil(context)
            msgs.append(f"{gp} annotations")

        if not msgs:
            return {"CANCELLED"}

        msg = "Removed: " + ", ".join(msgs)
        self.report({"INFO"}, msg)

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def purge_materials(self, context):
        count = 0
        override = {"object": None}

        for mat in bpy.data.materials:
            if not mat.is_grease_pencil:
                bpy.data.materials.remove(mat)
                count += 1

        for ob in context.scene.objects:
            if ob.type != "GPENCIL":
                if ob.material_slots:
                    override["object"] = ob

                    for _ in ob.material_slots:
                        bpy.ops.object.material_slot_remove(override)

        return count

    def purge_gpencil(self, context):
        count = 0
        excluded = set()

        for ob in context.scene.objects:
            if ob.type == "GPENCIL":
                excluded.add(ob.data)

        for gp in bpy.data.grease_pencils:
            if gp not in excluded:
                bpy.data.grease_pencils.remove(gp)
                count += 1

        return count

    def cleanup_modifiers(self, context):
        count = 0

        for ob in context.scene.objects:
            if ob.modifiers:
                for mod in ob.modifiers:
                    if (
                        (mod.type in {"CURVE", "LATTICE", "BOOLEAN"} and not mod.object) or
                        (mod.type == "SHRINKWRAP" and not mod.target)
                    ):
                        ob.modifiers.remove(mod)
                        count += 1

        return count

    def cleanup_objects(self, context):
        obs_to_del = set()
        obs_in_use = set()
        curve_del_count = 0
        lat_del_count = 0
        mesh_del_count = 0

        # Get objects

        for ob in context.scene.objects:

            ob.hide_viewport = False
            ob.hide_set(False)

            if ob.type in {"CURVE", "LATTICE"}:
                obs_to_del.add(ob)

            elif ob.type == "MESH" and not ob.data.vertices:
                ob_del = True

                if ob.modifiers:
                    for mod in ob.modifiers:
                        if mod.type == "BOOLEAN" and mod.operation == "UNION" and mod.object:
                            ob_del = False  # Booltron combined object
                            break

                if ob_del:
                    obs_to_del.add(ob)

            # Object dependencies

            if ob.modifiers:
                for mod in ob.modifiers:
                    if mod.type in {"CURVE", "LATTICE"} and mod.object:
                        obs_in_use.add(mod.object)

            if ob.constraints:
                for con in ob.constraints:
                    if con.type == "FOLLOW_PATH" and con.target:
                        obs_in_use.add(con.target)

            if ob.type == "CURVE":
                if ob.data.bevel_object:
                    obs_in_use.add(ob.data.bevel_object)
                if ob.data.taper_object:
                    obs_in_use.add(ob.data.taper_object)

        # Remove objects

        if obs_to_del:
            for ob in obs_to_del:
                if ob not in obs_in_use:

                    if ob.type == "CURVE":
                        curve_del_count += 1
                    elif ob.type == "LATTICE":
                        lat_del_count += 1
                    elif ob.type == "MESH":
                        mesh_del_count += 1

                    bpy.data.objects.remove(ob)

        # Report

        for area in context.screen.areas:
            area.tag_redraw()

        return curve_del_count, lat_del_count, mesh_del_count
