# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Messy Things project organizer for Blender.
#  Copyright (C) 2017-2018  Mikhail Rachinskiy
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


class Cleanup:

    def cleanup_objects(self, context):
        obs_to_del = set()
        obs_in_use = set()
        curve_del_count = 0
        lat_del_count = 0
        mesh_del_count = 0

        # Get objects

        for ob in context.scene.objects:

            ob.hide = False

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

    def cleanup_modifiers(self, context):
        mod_del_count = 0

        for ob in context.scene.objects:
            ob.hide = False

            if ob.modifiers:
                for mod in ob.modifiers:

                    if (mod.type in {"CURVE", "LATTICE", "BOOLEAN"} and not mod.object) or (
                        mod.type == "SHRINKWRAP" and not mod.target
                    ):
                        ob.modifiers.remove(mod)
                        mod_del_count += 1

        return mod_del_count

    def cleanup_materials(self, context):
        scene = context.scene
        active_object = context.active_object
        count = len(bpy.data.materials)

        for mat in bpy.data.materials:
            bpy.data.materials.remove(mat)

        for ob in scene.objects:

            if ob.material_slots:
                scene.objects.active = ob

                while ob.material_slots:
                    bpy.ops.object.material_slot_remove("EXEC_DEFAULT")

        scene.objects.active = active_object

        return count

    def cleanup_grease_pencil(self, context):
        count = len(bpy.data.grease_pencil)

        for gp in bpy.data.grease_pencil:
            bpy.data.grease_pencil.remove(gp)

        return count


class SCENE_OT_messythings_cleanup(Operator, Cleanup):
    bl_label = "Messy Things Cleanup"
    bl_description = "Remove redundant or purge all datablocks of set type"
    bl_idname = "scene.messythings_cleanup"
    bl_options = {"REGISTER", "UNDO"}

    use_objects = BoolProperty(name="Objects", description="Remove lattice, curve and empty mesh objects that are not in use by modifiers, constraints, curve Bevel Object and Taper Object properties")
    use_modifiers = BoolProperty(name="Modifiers", description="Remove Curve, Lattice, Boolean and Shrinkwrap modifiers with empty Object or Target fields")
    use_materials = BoolProperty(name="Materials", description="Purge all materials from file, additionally remove material slots from objects")
    use_gp = BoolProperty(name="Grease Pencil", description="Purge all grease pencil datablocks")

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)

        row = col.row(align=True)
        row.label(icon="OBJECT_DATA")
        row.prop(self, "use_objects")

        row = col.row(align=True)
        row.label(icon="MODIFIER")
        row.prop(self, "use_modifiers")

        row = col.row(align=True)
        row.label(icon="MATERIAL")
        row.prop(self, "use_materials")

        row = col.row(align=True)
        row.label(icon="GREASEPENCIL")
        row.prop(self, "use_gp")

    def execute(self, context):
        msgs = []

        if self.use_objects:
            curve, lat, mesh = self.cleanup_objects(context)
            msgs.append("{} curve".format(curve))
            msgs.append("{} lattice".format(lat))
            msgs.append("{} mesh".format(mesh))

        if self.use_modifiers:
            mod = self.cleanup_modifiers(context)
            msgs.append("{} modifiers".format(mod))

        if self.use_materials:
            mat = self.cleanup_materials(context)
            msgs.append("{} materials".format(mat))

        if self.use_gp:
            gp = self.cleanup_grease_pencil(context)
            msgs.append("{} gp".format(gp))

        if not msgs:
            return {"CANCELLED"}

        msg = "Removed: " + ", ".join(msgs)
        self.report({"INFO"}, msg)

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300 * context.user_preferences.view.ui_scale)
