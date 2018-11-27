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


from bpy.types import Panel


class VIEW3D_PT_messythings(Panel):
    bl_category = "Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Messy Things"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        layout.label("Settings")
        layout.operator("object.messythings_apply_render_profile", text="Render Profile", icon="SCENE")

        layout.label("Viewport")
        layout.operator("object.messythings_normalize_display", text="Normalize Display", icon="WIRE")

        layout.label("Scene")
        col = layout.column(align=True)
        col.operator("object.messythings_get_misplaced_dependencies", text="Get Dependencies", icon="LINKED")
        col.operator("object.messythings_sort_by_layers", text="Sort Objects", icon="OOPS")

        layout.label("Cleanup")
        col = layout.column(align=True)
        col.operator("object.messythings_cleanup_modifiers", text="Modifiers", icon="MODIFIER")
        col.operator("object.messythings_cleanup_objects", text="Objects", icon="OBJECT_DATA")
        col.operator("scene.messythings_cleanup_materials", text="Materials", icon="MATERIAL")
        col.operator("scene.messythings_cleanup_grease_pencil", text="Grease Pencil", icon="GREASEPENCIL")
