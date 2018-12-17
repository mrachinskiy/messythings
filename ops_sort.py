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


class Sort:

    def get_deps(self, context):
        scene = context.scene
        active_layer = scene.active_layer
        dep_obs = set()

        for ob in context.visible_objects:
            ob.select = False

            if ob.modifiers:
                for mod in ob.modifiers:
                    if (mod.type in {"CURVE", "LATTICE", "BOOLEAN"} and mod.object) or (
                        mod.type == "SHRINKWRAP" and mod.target
                    ):

                        mod_ob = mod.target if mod.type == "SHRINKWRAP" else mod.object
                        mod_ob.hide = False

                        if not mod_ob.is_visible(scene):
                            mod_ob.layers[active_layer] = True
                            mod_ob.select = True
                            dep_obs.add(mod_ob)

            if ob.constraints:
                for con in ob.constraints:
                    if con.type == "FOLLOW_PATH" and con.target:

                        con.target.hide = False

                        if not con.target.is_visible(scene):
                            con.target.layers[active_layer] = True
                            con.target.select = True
                            dep_obs.add(con.target)

        if dep_obs:
            for ob in dep_obs:
                scene.objects.active = ob
                break

        return len(dep_obs)

    def sort_by_layers(self, context):
        top_layers = range(0, 10)
        bottom_layers = range(10, 20)
        obs_sorted_top = 0
        obs_sorted_bottom = 0

        for ob in context.scene.objects:
            ob.hide = False

            if (ob.type == "MESH" and ob.draw_type in {"TEXTURED", "SOLID"}) or (
                ob.type == "CURVE" and (ob.data.bevel_depth or ob.data.bevel_object)
            ):
                i = 0

                for l in bottom_layers:
                    if ob.layers[l]:
                        ob.layers[l - 10] = True
                        ob.layers[l] = False
                        i = 1

                obs_sorted_top += i

            elif ob.type in {"CURVE", "LATTICE", "EMPTY", "MESH"}:
                i = 0

                for l in top_layers:

                    if ob.layers[l]:
                        ob.layers[l + 10] = True
                        ob.layers[l] = False
                        i = 1

                obs_sorted_bottom += i

        return obs_sorted_top, obs_sorted_bottom


class SCENE_OT_messythings_sort(Operator, Sort):
    bl_label = "Messy Things Sort"
    bl_description = "Sort objects by view layers"
    bl_idname = "scene.messythings_sort"
    bl_options = {"REGISTER", "UNDO"}

    use_ob_sort = BoolProperty(name="Sort Objects", description="Move Curve, Lattice, Empty and Mesh (draw type Wire or Bounds) objets to bottom layers; and Curve with bevel profile and Mesh objects to top layers")
    use_ob_dep_get = BoolProperty(name="Get Dependencies", description="Move to active view layer objects which are used in modifiers and constraints by visible objects, but located in hidden layers")

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        row = col.row(align=True)
        row.label(icon="OOPS")
        row.prop(self, "use_ob_sort")

        row = col.row(align=True)
        row.label(icon="LINKED")
        row.prop(self, "use_ob_dep_get")

    def execute(self, context):
        msgs = []

        if self.use_ob_sort:
            sorted_top, sorted_bottom = self.sort_by_layers(context)
            msgs.append("{} to top layers".format(sorted_top))
            msgs.append("{} to bottom layers".format(sorted_bottom))

        if self.use_ob_dep_get:
            result = self.get_deps(context)
            msgs.append("{} dependencies to active layer".format(result))

        if not msgs:
            return {"CANCELLED"}

        msg = "Objects sorted: " + ", ".join(msgs)
        self.report({"INFO"}, msg)

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300 * context.user_preferences.view.ui_scale)
