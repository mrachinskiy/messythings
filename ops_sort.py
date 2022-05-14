# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2017-2022 Mikhail Rachinskiy

from typing import Iterator

import bpy
from bpy.types import Operator, Object, Modifier
from bpy.props import EnumProperty, BoolProperty


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


def _ob_from_mod(mod: Modifier) -> Iterator[Object]:
    if mod.type == "NODES" and mod.node_group:
        for i in mod.node_group.inputs:
            if i.type == "OBJECT" and (ob := mod[i.identifier]):
                yield ob

    if (prop := _mod_ob_prop.get(mod.type)) and (ob := getattr(mod, prop)):
        yield ob


class SCENE_OT_messythings_deps_select(Operator):
    bl_label = "Select Dependencies"
    bl_description = "Select objects which are used in modifiers and constraints by currently selected objects"
    bl_idname = "scene.messythings_deps_select"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        dep_obs = set()

        for ob in context.selected_objects:
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

    sort_limit: EnumProperty(
        name="Sort",
        items=(
            ("ALL", "All Objects", ""),
            ("ACTIVE_COLL", "Active Collection", "(Shortcut: Alt)"),
        ),
    )
    use_collection_cleanup: BoolProperty(
        name="Claen Up Collections",
        description="Remove empty collections",
        default=True,
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(self, "sort_limit")
        layout.prop(self, "use_collection_cleanup")

    def execute(self, context):
        if self.sort_limit == "ACTIVE_COLL":
            parent_coll = context.collection
            obs = tuple(parent_coll.all_objects)
        else:
            parent_coll = context.scene.collection
            obs = tuple(context.scene.objects)

        if not obs:
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

            # Unlink

            for coll in ob.users_collection:
                coll.objects.unlink(ob)

        # Clean-up

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
        if event.alt:
            self.sort_limit = "ACTIVE_COLL"
            return self.execute(context)

        wm = context.window_manager
        return wm.invoke_props_dialog(self)
