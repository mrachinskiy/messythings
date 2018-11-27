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


from bpy.types import Operator


class OBJECT_OT_messythings_normalize_display(Operator):
    bl_label = "Messy Things Normalize Object Display"
    bl_description = (
        "Disable Double Sided, enable Draw All Edges, "
        "match render to viewport subdivision level of SubD modifier for all objects in the scene"
    )
    bl_idname = "object.messythings_normalize_display"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for ob in context.scene.objects:
            ob.hide = False

            if ob.type == "MESH":
                ob.show_all_edges = True
                ob.data.show_double_sided = False

            if ob.modifiers:
                for mod in ob.modifiers:
                    if mod.type == "SUBSURF":
                        mod.render_levels = mod.levels

        self.report({"INFO"}, "Objects display normalized")

        return {"FINISHED"}
