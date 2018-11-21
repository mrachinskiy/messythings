# ##### BEGIN GPL LICENSE BLOCK #####
#
#  JewelCraft jewelry design toolkit for Blender.
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


class OBJECT_OT_messythings_cleanup_modifiers(Operator):
    bl_label = "Messy Things Cleanup Modifiers"
    bl_description = "Remove Curve, Lattice, Boolean and Shrinkwrap modifiers with empty Object or Target fields"
    bl_idname = "object.messythings_cleanup_modifiers"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
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

        self.report({"INFO"}, "{} modifiers removed".format(mod_del_count))

        return {"FINISHED"}


class OBJECT_OT_messythings_cleanup_objects(Operator):
    bl_label = "Messy Things Cleanup Objects"
    bl_description = (
        "Remove lattice, curve and empty mesh objects that are not in use by modifiers, "
        "constraints, curve Bevel Object and Taper Object properties"
    )
    bl_idname = "object.messythings_cleanup_objects"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obs_to_del = set()
        obs_in_use = set()
        curve_del_count = 0
        lat_del_count = 0
        mesh_del_count = 0

        # Get objects

        for ob in context.scene.objects:

            ob.hide = False

            if (
                ob.type in {"CURVE", "LATTICE"} or
                (ob.type == "MESH" and not ob.data.vertices and "booltron_combined" not in ob)
            ):
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

        self.report(
            {"INFO"},
            "Objects removed: {} curve, {} lattice, {} mesh".format(curve_del_count, lat_del_count, mesh_del_count),
        )

        return {"FINISHED"}


class SCENE_OT_messythings_cleanup_grease_pencil(Operator):
    bl_label = "Messy Things Cleanup Grease Pencil"
    bl_description = "Remove all grease pencil datablocks"
    bl_idname = "scene.messythings_cleanup_grease_pencil"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        count = len(bpy.data.grease_pencil)

        for gp in bpy.data.grease_pencil:
            bpy.data.grease_pencil.remove(gp)

        self.report({"INFO"}, "{} datablocks removed".format(count))

        return {"FINISHED"}


class SCENE_OT_messythings_cleanup_materials(Operator):
    bl_label = "Messy Things Cleanup Materials"
    bl_description = "Remove all materials from file, additionally remove material slots from objects"
    bl_idname = "scene.messythings_cleanup_materials"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
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

        self.report({"INFO"}, "{} materials removed".format(count))

        return {"FINISHED"}
