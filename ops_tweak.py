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


from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty


class SCENE_OT_messythings_normalize(Operator):
    bl_label = "Messy Things Normalize Object Display"
    bl_description = (
        "Match render to viewport subdivision level "
        "in Subdivision modifier for all objects in the scene"
    )
    bl_idname = "scene.messythings_normalize"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        for ob in context.scene.objects:
            if ob.modifiers:
                for mod in ob.modifiers:
                    if mod.type == "SUBSURF":
                        mod.render_levels = mod.levels

        self.report({"INFO"}, "Objects display normalized")

        return {"FINISHED"}


class SCENE_OT_messythings_profile_render(Operator):
    bl_label = "Messy Things Apply Render Profile"
    bl_description = (
        "Resolution: 1080 x 1080\n"
        "Output format: PNG RGBA\n"
        "Device: GPU\n"
        "Samples: 100 (preview 10 samples)\n"
        "Tile order: Top to Bottom\n"
        "View transform: Filmic (Look: None)"
    )
    bl_idname = "scene.messythings_profile_render"
    bl_options = {"REGISTER", "UNDO"}

    resolution_x: IntProperty(
        default=1080,
        min=4,
        subtype="PIXEL",
        options={"SKIP_SAVE"},
    )
    resolution_y: IntProperty(
        default=1080,
        min=4,
        subtype="PIXEL",
        options={"SKIP_SAVE"},
    )
    samples: IntProperty(
        name="Render",
        default=100,
        min=1,
        options={"SKIP_SAVE"},
    )
    preview_samples: IntProperty(
        name="Viewport",
        default=10,
        min=0,
        options={"SKIP_SAVE"},
    )
    file_format: EnumProperty(
        name="File Format",
        items=(
            ("OPEN_EXR", "OpenEXR", ""),
            ("PNG", "PNG", ""),
        ),
        default="PNG",
        options={"SKIP_SAVE"},
    )
    display_mode: EnumProperty(
        name="Display Mode",
        items=(
            ("SCREEN", "Full Screen", ""),
            ("AREA", "Image Editor", ""),
            ("WINDOW", "New Window", ""),
            ("NONE", "Keep User Interface", ""),
        ),
        default="SCREEN",
        options={"SKIP_SAVE"},
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.separator()

        layout.prop(self, "display_mode")

        col = layout.column(align=True)
        col.prop(self, "resolution_x", text="Resolution X")
        col.prop(self, "resolution_y", text="Y")

        col = layout.column(align=True)
        col.prop(self, "samples")
        col.prop(self, "preview_samples")

        layout.prop(self, "file_format")

        layout.separator()

    def execute(self, context):
        scene = context.scene
        cycles = scene.cycles
        render = scene.render
        image = render.image_settings

        render.resolution_x = self.resolution_x
        render.resolution_y = self.resolution_y
        render.resolution_percentage = 100
        render.display_mode = self.display_mode
        render.film_transparent = True

        image.file_format = self.file_format
        image.color_mode = "RGBA"
        if self.file_format == "PNG":
            image.compression = 100
            image.color_depth = "8"
        else:
            image.color_depth = "32"

        cycles.device = "GPU"
        cycles.pixel_filter_type = "BLACKMAN_HARRIS"
        cycles.progressive = "PATH"
        cycles.use_square_samples = False
        cycles.samples = self.samples
        cycles.preview_samples = self.preview_samples
        cycles.sample_clamp_indirect = 10.0
        cycles.light_sampling_threshold = 0.01
        cycles.tile_order = "TOP_TO_BOTTOM"

        scene.view_settings.view_transform = "Filmic"
        scene.view_settings.look = "None"

        self.report({"INFO"}, "Render profile applied")

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
