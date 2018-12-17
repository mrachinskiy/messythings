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
from bpy.props import BoolProperty


class Tweak:

    def ob_normalize_display(self, context):
        for ob in context.scene.objects:
            ob.hide = False

            if ob.type == "MESH":
                ob.show_all_edges = True
                ob.data.show_double_sided = False

            if ob.modifiers:
                for mod in ob.modifiers:
                    if mod.type == "SUBSURF":
                        mod.render_levels = mod.levels

    def apply_render_profile(self, context):
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


class SCENE_OT_messythings_tweak(Operator, Tweak):
    bl_label = "Messy Things Tweak"
    bl_description = "Tweak scene and object settings"
    bl_idname = "scene.messythings_tweak"
    bl_options = {"REGISTER", "UNDO"}

    use_ob_normalize = BoolProperty(name="Normalize Object Display", description="Disable Double Sided, enable Draw All Edges, match render to viewport subdivision level of SubD modifier for all objects in the scene")
    use_render_profile = BoolProperty(
        name="Apply Render Profile",
        description=(
            "Resolution: 1080 x 1080\n"
            "Output format: PNG RGBA\n"
            "Device: GPU\n"
            "Samples: 100 (preview 10 samples)\n"
            "Tile order: Top to Bottom\n"
            "View transform: Filmic (Look: None)"
        )
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.label(icon="WIRE")
        row.prop(self, "use_ob_normalize")

        row = col.row(align=True)
        row.label(icon="RESTRICT_RENDER_OFF")
        row.prop(self, "use_render_profile")

    def execute(self, context):
        msgs = []

        if self.use_ob_normalize:
            self.ob_normalize_display(context)
            msgs.append("objects display normalized")

        if self.use_render_profile:
            self.apply_render_profile(context)
            msgs.append("render profile applied")

        if not msgs:
            return {"CANCELLED"}

        msg = "Tweaked: " + ", ".join(msgs)
        self.report({"INFO"}, msg)

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300 * context.user_preferences.view.ui_scale)
