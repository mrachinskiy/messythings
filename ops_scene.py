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


from bpy.types import Operator


class SCENE_OT_messythings_apply_render_profile(Operator):
    bl_label = "Messy Things Apply Render Profile"
    bl_description = "Apply render profile"
    bl_idname = "object.messythings_apply_render_profile"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene

        render = scene.render

        render.resolution_x = 1080
        render.resolution_y = 1080
        render.resolution_percentage = 100
        render.image_settings.file_format = "PNG"
        render.image_settings.color_mode = "RGBA"
        render.image_settings.compression = 100
        render.display_mode = "SCREEN"

        cycles = scene.cycles

        cycles.film_transparent = True
        cycles.device = "GPU"
        cycles.pixel_filter_type = "BLACKMAN_HARRIS"
        cycles.progressive = "PATH"
        cycles.use_square_samples = False
        cycles.samples = 100
        cycles.preview_samples = 10
        cycles.sample_clamp_indirect = 10.0
        cycles.light_sampling_threshold = 0.01
        cycles.tile_order = "TOP_TO_BOTTOM"

        scene.view_settings.view_transform = "Filmic"
        scene.view_settings.look = "None"

        return {"FINISHED"}
