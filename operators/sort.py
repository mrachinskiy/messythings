# SPDX-FileCopyrightText: 2017-2025 Mikhail Rachinskiy
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Iterator

import bpy
from bpy.props import BoolProperty
from bpy.types import Collection, Modifier, Object, Operator


_mod_ob_prop = {
    "CURVE": "object",
    "BOOLEAN": "object",
    "LATTICE": "object",
    "MESH_DEFORM": "object",
    "SHRINKWRAP": "target",
    "ARRAY": "offset_object",
    "MIRROR": "mirror_object",
    "SIMPLE_DEFORM": "origin",
}


def _get_collection_objects() -> tuple[Collection, tuple[Object]]:
    if bpy.context.area.type == "OUTLINER" and bpy.context.selected_ids:
        for id in bpy.context.selected_ids:
            if id.id_type == "COLLECTION":
                return bpy.context.collection, tuple(bpy.context.collection.all_objects)

    return bpy.context.scene.collection, tuple(bpy.context.scene.objects)


def _ob_from_mod(mod: Modifier) -> Iterator[Object]:
    if mod.type == "NODES" and mod.node_group:
        for socket in mod.node_group.interface.items_tree:
            if socket.socket_type == "NodeSocketObject" and (ob := mod[socket.identifier]):
                yield ob

    if (prop := _mod_ob_prop.get(mod.type)) and (ob := getattr(mod, prop)):
        yield ob


class SCENE_OT_messythings_deps_select(Operator):
    bl_label = "Select Dependencies"
    bl_description = "Select objects which are used in modifiers and constraints by currently selected objects"
    bl_idname = "scene.messythings_deps_select"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        obs = context.selected_objects
        dep_obs = set()

        for ob in obs:
            ob.select_set(False)

            if ob.modifiers:
                for mod in ob.modifiers:
                    for ob_ in _ob_from_mod(mod):
                        ob_.hide_viewport = False
                        ob_.hide_set(False)
                        ob_.select_set(True)
                        dep_obs.add(ob_)

            if ob.constraints:
                for con in ob.constraints:
                    if con.type == "FOLLOW_PATH" and con.target:
                        con.target.hide_viewport = False
                        con.target.hide_set(False)
                        con.target.select_set(True)
                        dep_obs.add(con.target)

        if not dep_obs:
            self.report({"INFO"}, "Dependencies not found")
            return {"CANCELLED"}

        count = len(dep_obs)

        for ob in dep_obs:
            context.view_layer.objects.active = ob
            break

        self.report({"INFO"}, f"{count} dependencies selected")

        return {"FINISHED"}

    def invoke(self, context, event):
        if not context.selected_objects:
            self.report({"ERROR"}, "Missing selected objects")
            return {"CANCELLED"}

        return self.execute(context)


class SCENE_OT_messythings_sort(Operator):
    bl_label = "Sort by Collections"
    bl_description = "Sort all objects in the scene in Main, Helpers, Gems, Lights and Gpencil collections"
    bl_idname = "scene.messythings_sort"
    bl_options = {"REGISTER", "UNDO"}

    use_collection_cleanup: BoolProperty(
        name="Claen Up Collections",
        description="Remove empty collections",
        default=True,
    )

    def execute(self, context):
        parent_coll, obs = _get_collection_objects()

        if not obs:
            self.report({"ERROR"}, "Objects not found")
            return {"CANCELLED"}

        ob_active = context.view_layer.objects.active
        obs_main = set()
        obs_gems = set()
        obs_helpers = set()
        obs_lights = set()
        obs_gpencil = set()

        for ob in obs:
            ob.hide_viewport = False
            ob.hide_set(False)
            is_dupliface = False

            if ob.is_instancer:
                for child in ob.children:
                    if "gem" in child:
                        is_dupliface = True
                        break

            if "gem" in ob or is_dupliface:
                obs_gems.add(ob)
            elif (
                (ob.type == "MESH" and ob.display_type in {"TEXTURED", "SOLID"}) or
                (ob.type == "CURVE" and (ob.data.bevel_depth or ob.data.bevel_object)) or
                ob.type in {"FONT", "META"}
            ):
                obs_main.add(ob)
            elif ob.type == "GPENCIL":
                obs_gpencil.add(ob)
            elif ob.type in {"LIGHT", "LIGHT_PROBE"}:
                obs_lights.add(ob)
            else:
                obs_helpers.add(ob)

            # Unlink object from existing collections

            for coll in ob.users_collection:
                coll.objects.unlink(ob)

        # Clean-up empty collections

        if self.use_collection_cleanup:
            for coll in bpy.data.collections:
                if coll is not parent_coll and not coll.all_objects:
                    bpy.data.collections.remove(coll)

        # Link

        for name, obs in (
            ("Gems", obs_gems),
            ("Main", obs_main),
            ("Helpers", obs_helpers),
            ("Lights", obs_lights),
            ("Gpensil", obs_gpencil),
        ):
            if obs:
                coll = bpy.data.collections.new(name)
                parent_coll.children.link(coll)
                for ob in obs:
                    coll.objects.link(ob)

        context.view_layer.objects.active = ob_active

        self.report({"INFO"}, "Sort completed")

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
